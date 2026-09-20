#!/usr/bin/env python3
"""
audit_html_report.py — generate a self-contained HTML report from audit.py JSON.

Usage:
    python3 audit.py --ingest a.sarif b.sarif --json out.json
    python3 audit_html_report.py out.json report.html

No server, no dependencies, no network. Produces one standalone .html file that
opens in any browser. Design target: a security-triage instrument for an auditor
who reads scanner output all day — dense, legible, score-forward, trustworthy.
Not a marketing dashboard.
"""
import json, sys, html, datetime

def esc(s): return html.escape(str(s))

def score_band(score, mx):
    # relative bands for color, not absolute — highest findings read hottest
    if mx <= 0: return "b0"
    r = score / mx
    if r >= 0.85: return "b4"
    if r >= 0.65: return "b3"
    if r >= 0.45: return "b2"
    if r >= 0.25: return "b1"
    return "b0"

def build(data):
    ranked = data.get("ranked", [])
    tools = data.get("tools", [])
    qw = data.get("quality_weighting", {}) or {}
    sig = data.get("signal_assessment", {}) or {}
    raw = data.get("raw_result_count", 0)
    dedup = data.get("deduplicated_count", len(ranked))
    mx = max((f.get("score", 0) for f in ranked), default=0)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    multi = sum(1 for f in ranked if f.get("n_tools", 1) > 1)

    mode = qw.get("mode", "—")
    mode_note = {
        "MEASURED": "Weights computed from ground truth in this ingest.",
        "PRIOR": "Coarse cross-dataset tool-quality priors applied (not measured on this code).",
        "MIXED": "Per-tool: recognized tools weighted by prior, others flat.",
        "INACTIVE": "Flat — all tool agreements weighted equally.",
    }.get(mode, "")

    rows = []
    for f in ranked:
        band = score_band(f.get("score", 0), mx)
        toolchips = "".join(
            f'<span class="chip">{esc(t)}</span>' for t in f.get("tools", []))
        consensus = ('<span class="consensus">%d tools</span>' % f["n_tools"]
                     if f.get("n_tools", 1) > 1 else '')
        noisy = '<span class="noisy" title="location flagged as noisy">noisy loc</span>' if f.get("noisy_loc") else ''
        rows.append(f'''<tr class="{band}">
          <td class="rank">{esc(f.get("rank",""))}</td>
          <td class="score"><span class="sv">{esc(f.get("score",""))}</span></td>
          <td class="rule">{esc(f.get("ruleId",""))}</td>
          <td class="loc"><span class="file">{esc(f.get("uri",""))}</span><span class="ln">:{esc(f.get("line",""))}</span></td>
          <td class="lvl {esc(f.get("level",""))}">{esc(f.get("level",""))}</td>
          <td class="tools">{toolchips}{consensus}</td>
          <td class="msg">{esc(f.get("message",""))}{noisy}</td>
        </tr>''')

    tools_line = ", ".join(esc(t) for t in tools) or "—"
    conf = esc(sig.get("ranking_confidence", "—"))
    informative = ", ".join(esc(s) for s in sig.get("informative_signals", [])) or "none"

    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>audit — review-worthiness report</title>
<style>
  :root {{
    --ink:#14171c; --ink2:#3a4048; --line:#d6d3cb; --paper:#faf9f6;
    --panel:#ffffff; --accent:#1f5c4d; --mut:#7c8188;
    --b0:#f4f2ee; --b1:#fbeede; --b2:#f7d9b0; --b3:#eeb27a; --b4:#e08a54;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink);
    font:14px/1.5 "SF Mono",ui-monospace,"Cascadia Code",Menlo,Consolas,monospace; }}
  .wrap {{ max-width:1180px; margin:0 auto; padding:32px 28px 80px; }}
  header {{ border-bottom:2px solid var(--ink); padding-bottom:18px; margin-bottom:6px; }}
  h1 {{ font-size:15px; letter-spacing:.14em; text-transform:uppercase; margin:0 0 3px;
    font-weight:700; }}
  .sub {{ color:var(--mut); font-size:12px; letter-spacing:.03em; }}
  .stats {{ display:flex; gap:0; margin:22px 0 8px; border:1px solid var(--line);
    background:var(--panel); }}
  .stat {{ flex:1; padding:14px 16px; border-right:1px solid var(--line); }}
  .stat:last-child {{ border-right:none; }}
  .stat .n {{ font-size:26px; font-weight:700; letter-spacing:-.02em; line-height:1; }}
  .stat .l {{ font-size:10.5px; text-transform:uppercase; letter-spacing:.11em;
    color:var(--mut); margin-top:6px; }}
  .stat .n.accent {{ color:var(--accent); }}
  .band {{ display:flex; gap:14px; flex-wrap:wrap; margin:16px 0 4px;
    font-size:11.5px; color:var(--ink2); }}
  .band .pill {{ border:1px solid var(--line); padding:7px 11px; background:var(--panel); }}
  .band .pill b {{ color:var(--ink); font-weight:700; }}
  .modebar {{ margin:14px 0 26px; padding:12px 15px; border-left:3px solid var(--accent);
    background:var(--panel); border-top:1px solid var(--line);
    border-right:1px solid var(--line); border-bottom:1px solid var(--line);
    font-size:12.5px; color:var(--ink2); }}
  .modebar b {{ color:var(--ink); letter-spacing:.05em; }}
  table {{ width:100%; border-collapse:collapse; background:var(--panel);
    border:1px solid var(--line); font-size:12.5px; }}
  thead th {{ text-align:left; font-size:10px; text-transform:uppercase;
    letter-spacing:.1em; color:var(--mut); padding:10px 12px;
    border-bottom:1.5px solid var(--ink); position:sticky; top:0; background:var(--panel); }}
  tbody td {{ padding:9px 12px; border-bottom:1px solid var(--line); vertical-align:top; }}
  tbody tr.b4 {{ background:var(--b4); }} tbody tr.b3 {{ background:var(--b3); }}
  tbody tr.b2 {{ background:var(--b2); }} tbody tr.b1 {{ background:var(--b1); }}
  tbody tr.b0 {{ background:var(--panel); }}
  tbody tr.b3, tbody tr.b4 {{ color:#2a1a0e; }}
  .rank {{ color:var(--mut); font-variant-numeric:tabular-nums; width:34px; }}
  .score {{ width:52px; }}
  .sv {{ font-weight:700; font-size:14px; font-variant-numeric:tabular-nums; }}
  .rule {{ font-weight:600; white-space:nowrap; }}
  .loc .file {{ color:var(--ink); }} .loc .ln {{ color:var(--mut); }}
  .lvl {{ text-transform:uppercase; font-size:10px; letter-spacing:.08em; width:70px; }}
  .lvl.error {{ color:#a8321e; font-weight:700; }}
  .lvl.warning {{ color:#9a6b12; }} .lvl.note {{ color:var(--mut); }}
  .chip {{ display:inline-block; border:1px solid currentColor; opacity:.75;
    padding:1px 6px; margin:0 4px 2px 0; font-size:10.5px; border-radius:2px; }}
  .consensus {{ display:inline-block; background:var(--accent); color:#fff;
    padding:1px 7px; font-size:10.5px; font-weight:700; border-radius:2px; }}
  .noisy {{ display:inline-block; margin-left:8px; color:var(--mut);
    font-size:10px; font-style:italic; }}
  .msg {{ color:var(--ink2); }}
  footer {{ margin-top:22px; font-size:11px; color:var(--mut); line-height:1.7; }}
  footer b {{ color:var(--ink2); }}
  .controls {{ margin:0 0 10px; font-size:11.5px; color:var(--mut); }}
  .controls input {{ font:inherit; padding:6px 9px; border:1px solid var(--line);
    background:var(--panel); width:260px; }}
  @media (max-width:720px) {{ .stats {{ flex-wrap:wrap; }} .stat {{ min-width:50%; }}
    .msg {{ display:none; }} }}
</style></head><body><div class="wrap">
<header>
  <h1>Review-Worthiness Report</h1>
  <div class="sub">audit.py deterministic re-rank · generated {now}</div>
</header>
<div class="stats">
  <div class="stat"><div class="n">{dedup}</div><div class="l">findings ranked</div></div>
  <div class="stat"><div class="n">{raw}</div><div class="l">raw (pre-dedup)</div></div>
  <div class="stat"><div class="n accent">{multi}</div><div class="l">multi-tool consensus</div></div>
  <div class="stat"><div class="n">{len(tools)}</div><div class="l">scanners</div></div>
</div>
<div class="band">
  <span class="pill">scanners: <b>{tools_line}</b></span>
  <span class="pill">ranking confidence: <b>{conf}</b></span>
  <span class="pill">informative signals: <b>{informative}</b></span>
</div>
<div class="modebar"><b>Weighting: {esc(mode)}</b> — {esc(mode_note)}</div>
<div class="controls">
  <input id="q" placeholder="filter by file, rule, or message…" oninput="flt()">
</div>
<table id="t"><thead><tr>
  <th>#</th><th>Score</th><th>Rule</th><th>Location</th><th>Level</th><th>Flagged by</th><th>Message</th>
</tr></thead><tbody>
{"".join(rows)}
</tbody></table>
<footer>
  <b>What this is:</b> findings from your scanners, deduplicated and ordered by
  review-worthiness (location + multi-tool agreement + tool quality + severity).
  Higher = look first. <b>What this is not:</b> a ranking by exploitability, and
  not a substitute for human review — it orders what to examine, it doesn't
  decide what's real. Ranking is deterministic: same input, same order.
</footer>
</div>
<script>
function flt(){{
  var q=document.getElementById('q').value.toLowerCase();
  document.querySelectorAll('#t tbody tr').forEach(function(r){{
    r.style.display = r.textContent.toLowerCase().indexOf(q)>-1 ? '' : 'none';
  }});
}}
</script>
</body></html>'''

def main():
    if len(sys.argv) < 3:
        print("usage: python3 audit_html_report.py <audit_json> <output_html>")
        sys.exit(1)
    data = json.load(open(sys.argv[1]))
    open(sys.argv[2], "w").write(build(data))
    print(f"wrote {sys.argv[2]} ({len(data.get('ranked',[]))} findings)")

if __name__ == "__main__":
    main()
