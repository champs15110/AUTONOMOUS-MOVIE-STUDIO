#!/usr/bin/env python3
"""
Emit the Stage 03 design bibles from the design manifests, so the markdown and the JSON
are the same data:

  03_CHARACTERS/CHARACTER_BIBLE.md   <- 03_CHARACTERS/CHARACTER_MANIFEST.json
  04_WORLD/WORLD_BIBLE.md            <- 04_WORLD/WORLD_MANIFEST.json (environments)
  04_WORLD/PROP_BIBLE.md             <- 04_WORLD/WORLD_MANIFEST.json (props)

It also asserts that every field the Design Director is required to define is present and
non-empty for every character, environment and prop.

Run:  python3 tools/build_design_bibles.py
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHAR = os.path.join(ROOT, "03_CHARACTERS", "CHARACTER_MANIFEST.json")
WORLD = os.path.join(ROOT, "04_WORLD", "WORLD_MANIFEST.json")

CHAR_FIELDS = ["name", "role", "personality", "body", "face", "clothing", "materials",
               "colors", "accessories", "expressions", "body_language", "movement_style"]
ENV_FIELDS = ["architecture", "scale", "materials", "lighting", "atmosphere",
              "time_of_day", "weather", "important_background_elements"]
PROP_FIELDS = ["design", "scale", "material", "purpose", "continuity_requirements"]

missing: list[str] = []


def ck(cond: bool, label: str) -> None:
    if not cond:
        missing.append(label)


def img_links(paths, base=ROOT) -> str:
    if not paths:
        return "_no reference image yet_"
    return "\n".join(f"![{os.path.basename(p)}]({os.path.relpath(p, os.path.dirname(base))})"
                     if False else f"![{os.path.basename(p)}]({p})" for p in paths)


def character_md(c: dict) -> str:
    o = []
    a = o.append
    a(f'## {c["name"]}')
    a("")
    a(f'**id:** `{c["id"]}` · **role:** {c["role"]} · **provenance:** {c["provenance"]}')
    a("")
    for f in CHAR_FIELDS:
        ck(bool(c.get(f)), f'{c["id"]}.{f}')
    a(f'**Personality.** {c["personality"]}')
    a("")
    a("### Body")
    a(f'- **Proportions:** {c["body"]["proportions"]}')
    a(f'- **Height:** {c["body"]["height"]}')
    a(f'- **Silhouette:** {c["body"]["silhouette"]}')
    a(f'- **Buildable geometry:** {c["body"]["buildable_geometry"]}')
    a("")
    a("### Face")
    a(f'- **Face:** {c["face"]["face"]}')
    a(f'- **Eyes:** {c["face"]["eyes"]}')
    a(f'- **Mouth:** {c["face"]["mouth"]}')
    a("")
    a(f'**Clothing.** {c["clothing"]}')
    a("")
    a("**Materials.** " + "; ".join(c["materials"]))
    a("")
    a(f'**Colours.** palette {", ".join(c["colors"]["palette"])} · accent {c["colors"]["accent"]}')
    a("")
    a("**Accessories.** " + "; ".join(c["accessories"]))
    a("")
    a(f'**Expressions.** {c["expressions"]}')
    a("")
    a(f'**Body language.** {c["body_language"]}')
    a("")
    a(f'**Movement style.** {c["movement_style"]}')
    a("")
    a("**Continuity.**")
    for n in c["continuity_notes"]:
        a(f"- {n}")
    a("")
    a(f'**Reference images:** {" · ".join(c["reference_images"])}')
    a("")
    return "\n".join(o)


def env_md(e: dict) -> str:
    o = []
    a = o.append
    a(f'## {e["name"]}')
    a("")
    a(f'**id:** `{e["id"]}` · **scenes:** {", ".join(e["scenes"])}')
    a("")
    for f in ENV_FIELDS:
        ck(bool(e.get(f)), f'{e["id"]}.{f}')
    a(f'**Architecture.** {e["architecture"]}')
    a("")
    a(f'**Scale.** {e["scale"]}')
    a("")
    a("**Materials.** " + "; ".join(e["materials"]))
    a("")
    a(f'**Lighting.** {e["lighting"]}')
    a("")
    a(f'**Atmosphere.** {e["atmosphere"]}')
    a("")
    a(f'**Time of day.** {e["time_of_day"]}')
    a("")
    a(f'**Weather.** {e["weather"]}')
    a("")
    a("**Important background elements.** " + "; ".join(e["important_background_elements"]))
    a("")
    a(f'**Palette.** {", ".join(e["palette"])} · **Modularity.** {e["modularity"]}')
    a("")
    a("**Continuity.**")
    for n in e["continuity_notes"]:
        a(f"- {n}")
    a("")
    a(f'**Reference images:** {" · ".join(e["reference_images"])}')
    a("")
    return "\n".join(o)


def prop_md(p: dict) -> str:
    o = []
    a = o.append
    a(f'### {p["name"]}')
    a("")
    for f in PROP_FIELDS:
        ck(bool(p.get(f)), f'{p["id"]}.{f}')
    a(f'**Design.** {p["design"]}')
    a("")
    a(f'**Scale.** {p["scale"]}')
    a("")
    a(f'**Material.** {p["material"]}')
    a("")
    a(f'**Purpose.** {p["purpose"]}')
    a("")
    a("**Continuity requirements.**")
    for n in p["continuity_requirements"]:
        a(f"- {n}")
    a("")
    a(f'_Reference: {" · ".join(p["reference_images"])}_')
    a("")
    return "\n".join(o)


def main() -> int:
    ch = json.load(open(CHAR, encoding="utf-8"))
    wo = json.load(open(WORLD, encoding="utf-8"))

    # ---- CHARACTER_BIBLE.md
    o = []
    a = o.append
    a(f'# CHARACTER BIBLE — {ch["film_title"]}')
    a("")
    a("**Project:** AMS-2026-001 · **Task:** T03_CHARACTER_WORLD · "
      "**Machine twin:** `CHARACTER_MANIFEST.json`")
    a("")
    a(ch["design_director_note"])
    a("")
    a(f'**Reference images:** {" · ".join(ch["reference_images"])}')
    a("")
    a("---")
    a("")
    for c in ch["characters"]:
        a(character_md(c))
        a("---")
        a("")
    cb = "\n".join(o)
    open(os.path.join(ROOT, "03_CHARACTERS", "CHARACTER_BIBLE.md"), "w",
         encoding="utf-8").write(cb)

    # ---- WORLD_BIBLE.md
    o = []
    a = o.append
    a(f'# WORLD BIBLE — {wo["film_title"]}')
    a("")
    a("**Project:** AMS-2026-001 · **Task:** T03_CHARACTER_WORLD · "
      "**Machine twin:** `WORLD_MANIFEST.json` · **Props:** `PROP_BIBLE.md`")
    a("")
    a(wo["world_director_note"])
    a("")
    a("## Global rules")
    a("")
    a(f'**Lighting.** {wo["global_rules"]["lighting"]}')
    a("")
    a(f'**Weather progression.** {wo["global_rules"]["weather_progression"]}')
    a("")
    a(f'**Water.** {wo["global_rules"]["water"]}')
    a("")
    a("**Colour script.**")
    a("")
    a("| Scenes | Key | Purpose |")
    a("|---|---|---|")
    for r in wo["global_rules"]["color_script"]:
        a(f'| {", ".join(r["scenes"])} | {r["key"]} | {r["purpose"]} |')
    a("")
    a("---")
    a("")
    for e in wo["environments"]:
        a(env_md(e))
        a("---")
        a("")
    open(os.path.join(ROOT, "04_WORLD", "WORLD_BIBLE.md"), "w",
         encoding="utf-8").write("\n".join(o))

    # ---- PROP_BIBLE.md
    o = []
    a = o.append
    a(f'# PROP BIBLE — {wo["film_title"]}')
    a("")
    a("**Project:** AMS-2026-001 · **Task:** T03_CHARACTER_WORLD · "
      "**Machine twin:** `WORLD_MANIFEST.json` · **Prop sheet:** "
      "`04_WORLD/REFERENCE_IMAGES/PROPS_master_sheet.png`")
    a("")
    a("Every prop carries design, scale, material, purpose and continuity requirements. "
      "Continuity requirements are enforced by `02_SCREENPLAY/verify_shot_list.py` and must "
      "be re-checked at QC.")
    a("")
    a("---")
    a("")
    for p in wo["props"]:
        a(prop_md(p))
        a("---")
        a("")
    open(os.path.join(ROOT, "04_WORLD", "PROP_BIBLE.md"), "w",
         encoding="utf-8").write("\n".join(o))

    print(f"characters {len(ch['characters'])} | environments {len(wo['environments'])} | "
          f"props {len(wo['props'])}")
    if missing:
        print(f"MISSING FIELDS ({len(missing)}):")
        for m in missing:
            print("   x", m)
        return 1
    print("all required character / environment / prop fields present and non-empty")
    print("wrote CHARACTER_BIBLE.md, WORLD_BIBLE.md, PROP_BIBLE.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
