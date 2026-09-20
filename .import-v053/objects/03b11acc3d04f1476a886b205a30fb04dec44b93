#!/usr/bin/env python3
"""Convert cppcheck XML (v2) to SARIF. No third-party dependency.
Used by the CI action because apt's cppcheck may predate native SARIF output."""
import sys, json, xml.etree.ElementTree as ET
def main():
    xml_in, sarif_out = sys.argv[1], sys.argv[2]
    try:
        root = ET.parse(xml_in).getroot()
    except Exception:
        json.dump({"version":"2.1.0","runs":[{"tool":{"driver":{"name":"Cppcheck"}},"results":[]}]}, open(sarif_out,"w"))
        return
    results=[]
    for err in root.findall(".//error"):
        loc = err.find("location")
        if loc is None: continue
        cwe = err.get("cwe")
        rid = "CWE-%s" % cwe if cwe and cwe != "0" else (err.get("id") or "cppcheck")
        sev = err.get("severity","warning")
        lvl = {"error":"error","warning":"warning"}.get(sev,"note")
        try: line = max(1,int(loc.get("line","1")))
        except: line = 1
        results.append({"ruleId":rid,"level":lvl,"message":{"text":err.get("msg","")},
            "locations":[{"physicalLocation":{"artifactLocation":{"uri":loc.get("file","")},
            "region":{"startLine":line}}}]})
    json.dump({"version":"2.1.0","$schema":"https://json.schemastore.org/sarif-2.1.0.json",
        "runs":[{"tool":{"driver":{"name":"Cppcheck"}},"results":results}]}, open(sarif_out,"w"))
    print("converted %d cppcheck findings" % len(results))
if __name__ == "__main__": main()
