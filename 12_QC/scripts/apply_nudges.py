#!/usr/bin/env python3
"""
apply_nudges - rewrite the patched shot_cams entries (from nudge_patches.json)
into 08_CAMERA/scripts/shot_cams.py, appending a QC-13 provenance tag to each
note. Idempotent: skips shots already tagged.

Run: python3 12_QC/scripts/apply_nudges.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
P = os.path.join(ROOT, "08_CAMERA", "scripts", "shot_cams.py")
PJ = json.load(open(os.path.join(HERE, "nudge_patches.json"), encoding="utf-8"))
PJ["unfixed"] = [s for s in PJ["unfixed"] if s not in PJ["patches"]]

s = open(P, encoding="utf-8").read()
for sid, patch in PJ["patches"].items():
    spec = patch["spec"]
    if "QC-13 nudge" in spec.get("note", ""):
        continue
    spec = dict(spec)
    spec["note"] = spec.get("note", "") + " QC-13 nudge: camera re-placed for " \
        "clear subject line of sight (ERR-0004 fix), framing window kept."
    body = ", ".join(f"{k}={v!r}" for k, v in spec.items())
    new = f'"{sid}": dict({body}),'
    pat = re.compile(re.escape(f'"{sid}": dict(') + r".*?\),\n", re.S)
    s2, n = pat.subn(new + "\n", s, count=1)
    assert n == 1, sid
    s = s2

open(P, "w", encoding="utf-8").write(s)
json.dump(PJ, open(os.path.join(HERE, "nudge_patches.json"), "w"), indent=2)
print("patched entries:", len(PJ["patches"]), "| unfixed:", PJ["unfixed"])
