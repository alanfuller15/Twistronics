#!/usr/bin/env python3
"""
audit_dedup_display.py — STANDALONE display-only cross-tool dedup.
Reads audit.py's --json output, adds a 'display_group' to cross-tool duplicate findings
(Type 1: same file, line within tolerance, same CWE-class, DIFFERENT tools), and writes
an augmented JSON. Does NOT modify audit.py and does NOT change ranking/score/order —
it only ADDS annotation fields to the existing ranked list.

Usage:  python3 audit_dedup_display.py audit_result.json [out.json]
Grounding: DefectDojo two-algorithm model (same-tool dedup stays; cross-tool is separate,
location+class); bounded hand-verifiable CWE->class map; junk-drawer CWEs denylisted;
unknown CWE -> no grouping (graceful, never a false merge).
"""
import json, sys, re

_CWE_CLASS = {119:"buf",120:"buf",121:"buf",122:"buf",125:"buf",126:"buf",127:"buf",
              787:"buf",788:"buf",805:"buf",476:"null",415:"uaf",416:"uaf",825:"uaf",
              457:"uninit",456:"uninit",824:"uninit",908:"uninit",665:"uninit",
              401:"leak",404:"leak",772:"leak",775:"leak",134:"fmt",190:"int",191:"int",369:"int"}
_CWE_DENY = {398,561,563,570,571,682,704}
# CodeQL C/C++ security queries carry a rule NAME (cpp/...), not always a CWE number, once
# past ingestion. Bounded, hand-verifiable name->class map (mirrors the CWE classes above).
_CODEQL_RULE_CLASS = {
    "cpp/double-free":"uaf", "cpp/use-after-free":"uaf",
    "cpp/tainted-format-string":"fmt", "cpp/uncontrolled-format-string":"fmt",
    "cpp/overrunning-write":"buf", "cpp/badly-bounded-write":"buf",
    "cpp/very-likely-overrunning-write":"buf", "cpp/unbounded-write":"buf",
    "cpp/overrunning-write-with-float":"buf", "cpp/out-of-bounds":"buf",
    "cpp/uninitialized-local":"uninit", "cpp/init-order-reversed":"uninit",
    "cpp/incorrect-not-operator-usage":"int", "cpp/integer-overflow":"int",
    "cpp/tainted-arithmetic":"int", "cpp/comparison-with-wider-type":"int",
    "cpp/null-pointer-dereference":"null", "cpp/redundant-null-check":"null",
    "cpp/memory-leak":"leak", "cpp/double-close":"leak", "cpp/open-call-mode":"leak",
}
TOL = 3

def _cwe_class(rec):
    rid = str(rec.get('ruleId','')).strip().lower()
    if rid in _CODEQL_RULE_CLASS: return _CODEQL_RULE_CLASS[rid]
    blob = f"{rec.get('ruleId','')} {rec.get('message','')} {rec.get('uri','')}"
    for m in re.finditer(r"cwe[-_/:=\"'\s]{0,4}(\d+)", blob, re.I):
        n = int(m.group(1))
        if n in _CWE_DENY: continue
        if n in _CWE_CLASS: return _CWE_CLASS[n]
    return None

def _basename(u):
    u = str(u or "").replace("\\","/")
    return u.rsplit("/",1)[-1] if "/" in u else u

def annotate(data):
    ranked = data.get("ranked", [])
    n = len(ranked)
    parent = list(range(n))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: parent[max(ra,rb)]=min(ra,rb)
    meta=[]
    for r in ranked:
        ln=r.get("line"); ln=ln if isinstance(ln,int) else None
        meta.append((_basename(r.get("uri","")), ln, _cwe_class(r), frozenset(r.get("tools") or [])))
    for i in range(n):
        fi,li,ci,ti=meta[i]
        if li is None or ci is None: continue
        for j in range(i+1,n):
            fj,lj,cj,tj=meta[j]
            if fi!=fj or lj is None or cj is None: continue
            if ci!=cj or abs(li-lj)>TOL: continue
            if ti & tj: continue          # share a tool -> same-tool dup, never group
            union(i,j)
    groups={}
    for i in range(n): groups.setdefault(find(i),[]).append(i)
    ngrouped=0
    for root,idxs in groups.items():
        if len(idxs)>1:
            merged=sorted({t for k in idxs for t in (ranked[k].get("tools") or [])})
            for k in idxs:
                ranked[k]["display_group"]=int(root)
                ranked[k]["display_also_flagged_by"]=merged
            ngrouped+=1
    data["display_groups_count"]=ngrouped
    return data, ngrouped

if __name__=="__main__":
    if len(sys.argv)<2:
        print("usage: audit_dedup_display.py <audit_result.json> [out.json]"); sys.exit(1)
    inp=sys.argv[1]; out=sys.argv[2] if len(sys.argv)>2 else inp.replace(".json","_display.json")
    data=json.load(open(inp))
    data,ng=annotate(data)
    json.dump(data, open(out,"w"), indent=2)
    print(f"wrote {out}: {ng} cross-tool display group(s) added; ranking untouched (audit.py not modified)")
