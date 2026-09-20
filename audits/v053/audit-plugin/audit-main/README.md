# audit — a multi-scanner consensus re-ranker for static analysis

**The idea in one line:** run several security scanners, then rank findings higher where
*independent tools agree* — because when different tools flag the same spot, it's much more
likely to be a real bug worth your time.

Static analysis tools are noisy: run one on real code and you get hundreds of warnings, most of
them false alarms. This is the #1 documented reason teams abandon these tools. `audit` attacks
the noise by trusting **consensus**: it ingests findings from multiple scanners (in the standard
SARIF format), merges the ones pointing at the same bug, and re-ranks so the agreed-upon,
review-worthy findings rise to the top.

## Does it actually work? (validated on real vulnerabilities, not synthetic benchmarks)

Tested against **135 real vulnerable functions across 9 real open-source C/C++ projects**
(binutils, ffmpeg, libpng, openssl, sqlite, and more — using their known CVEs as ground truth):

- **ROC-AUC 0.755** — given a vulnerable file and a clean one, it ranks the vulnerable one higher
  ~3 times out of 4 (0.5 = coin flip).
- **Catch ~65% of vulnerable files by reviewing just the top 20%** of ranked findings.
- **~13x concentration** — files flagged by 4 tools were ~13x more likely to be truly vulnerable
  than files flagged by just 1.

These line up with independent published research (combining tools beats the best single tool by
~17 percentage points, arXiv:2407.12241).

## Try it in ~2 minutes (C/C++)

```bash
# 1. get findings from two scanners (SARIF format)
flawfinder --sarif your_code/ > flawfinder.sarif
cppcheck --enable=all --xml --xml-version=2 your_code/ 2> cppcheck.xml
python3 src/cppcheck_xml_to_sarif.py cppcheck.xml cppcheck.sarif

# 2. re-rank by consensus
python3 src/audit.py --ingest flawfinder.sarif cppcheck.sarif --json out.json

# 3. (optional) collapse cross-tool duplicates in the display
python3 src/audit_dedup_display.py out.json out_display.json
```
The top of `out.json` is your review queue, ordered by review-worthiness.

## Honest scope (what it is and isn't)

- **Validated on C/C++** with flawfinder, cppcheck, and CodeQL. Other languages/tools: unproven,
  not disproven — the engine is language-agnostic (works on SARIF), but the consensus signal
  hasn't been validated elsewhere yet.
- It's a **triage aid** — it surfaces review-worthy code. It does **not** prove exploitability.
- **0.755 is useful, not magic.** It beats a coin flip and the best single tool; it's not an oracle.
- The newest piece (cross-tool duplicate display) handles the case where tools agree on *location*.
  Harder cases (a bug whose source and sink are in different functions) are documented as an open
  problem, not solved.

## Why trust the numbers
Every claim here was measured against real CVEs and reported honestly — including results that
weren't flattering. The methodology (external grounding, significance-testing surprising results,
golden-master safety checks) is documented in the repo. Feedback and criticism very welcome.

*(License: see LICENSE. This is a research-grade tool / proof of concept.)*
