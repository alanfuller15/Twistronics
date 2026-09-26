# Exact Sites source for Claude review

Restores version 18 then applies the actual Git patches for versions 19–21. Every source file is checked against hashes read from the original Sites commits. This is a portable source/history transfer, not a claim that Sites commit objects exist in this GitHub repository.

Run `python materialize.py /new/absolute/output 21` (Python 3.12+, Git), then install from package-lock.json as needed. All sources, build scripts, compiled bundles, scientific display data, and binary density frames are included. No credentials or dependencies are packaged. Do not deploy the reconstructed site during review.

Current deployed v21 Sites commit: ee72c7b07b3465f37ea9575dcdebf0fcb3716457.
Current index.html SHA-256: 929f470cfa46aad574da7650d09a8c91abb0698b1f2fcbc582745fd6332b0563.

Independent review requested on PR #2. For coverage exporter replay, use the audited scientific repository separately and supply the script's repo argument. Original v18–21 byte hashes and source IDs are in MANIFEST.json.
