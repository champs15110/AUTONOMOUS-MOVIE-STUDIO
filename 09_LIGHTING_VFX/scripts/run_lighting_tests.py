#!/usr/bin/env python3
"""
Stage 09 lighting/VFX harness — NINETY-TWO TURNS.

Per scene (10): rebuild the scene from 06_ASSETS, apply the scene's lighting
and VFX design, then verify:
  1. shadow-coherence   exactly one shadow-casting light == the planned key
  2. character-lit      every character anchor receives light (E >= 1.0 proxy)
  3. face-readability   warm fill within 6 m; fill/key energy ratio >= 0.08
  4. materials          every mesh has materials, all from the 06 registry
  5. background         env dressing present (>=5 objects) and world not black
  6. design-adherence   built lights/world match LIGHTING plan exactly
  7. vfx-objects        every planned effect exists with its object count
  8. wind-direction     storm rain (SC05-07) slants camera-right (+X)
  9. exposure-proxy     key-light E at character within plan bounds
                        (PROXY: broadcast-range legality is measured on real
                         frames at render QC, task T11)
 10. shot-timing        rain ignition (SC04_SH003), lee calm (SC07_SH008) and
                        ignition glow (SC08_SH007) keyed to approved frames
 11. coverage           all 58 shots carry a lighting setup ref + grade note;
                        every effect carries a story purpose

Writes: LIGHTING_PLAN.json, VFX_PLAN.json, LIGHTING_INDEX.json,
        vfx/VFX_INDEX.json, LIGHTING_QC.md
Exit 0 only when every scene PASSES.
"""

import json
import math
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for _p in (os.path.join(ROOT, "tools", "blender_stub"),
           os.path.join(ROOT, "06_ASSETS", "scripts"),
           os.path.join(ROOT, "06_ASSETS", "materials"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bpy  # noqa: E402
import ams_materials as MATS  # noqa: E402
import light_design as LD  # noqa: E402
import light_runner as LR  # noqa: E402

OUT_DIR = os.path.join(ROOT, "09_LIGHTING_VFX")
SCENE_FILES = {sid: f"09_LIGHTING_VFX/SCENE_LIGHTING/light_{sid}.py" for sid in LD.SCENES}
CHAR_ANCHORS = ("CHAR_WICK", "CHAR_CHILD", "CHAR_GIRL")


def world_pos(o):
    p = [0.0, 0.0, 0.0]
    while o is not None:
        p = [p[i] + o.location[i] for i in range(3)]
        o = o.parent
    return p


def e_est(light_obj, at):
    ld = light_obj.data
    if ld.type == "SUN":
        return ld.energy
    d = max(0.5, math.dist(world_pos(light_obj), at))
    return ld.energy / (d * d)


def world_settings(w):
    """(color, strength) from the world's Background node."""
    found = ((0, 0, 0), 0.0)
    for n in w.node_tree.nodes:
        if (n.inputs["Color"].default_value is not None
                and n.inputs["Strength"].default_value is not None):
            found = (tuple(n.inputs["Color"].default_value[:3]),
                     n.inputs["Strength"].default_value)
    return found


def coll_objects(name):
    out = []

    def rec(c):
        for o in list(c.objects):
            out.append(o)
        for ch in list(c.children):
            rec(ch)

    def find(c):
        if c.name == name:
            rec(c)
            return
        for ch in list(c.children):
            find(ch)
    find(bpy.context.scene.collection)
    return out


def run_scene(sid):
    bpy._reset()
    LR.build_scene_lighting(sid)
    spec = LD.LIGHTING[sid]
    objs = LD.all_objects()
    lights = [o for o in objs if o.data is not None and hasattr(o.data, "energy")]
    by_name = {o.name: o for o in lights}
    anchors = [world_pos(o) for o in objs if o.name in CHAR_ANCHORS]
    checks = {}

    # 1 shadow coherence
    casters = [o.name for o in lights if o.data.use_shadow]
    checks["shadow-coherence"] = (casters == [spec["key"]], casters)

    # 2 character lit  /  9 exposure proxy
    if anchors:
        lit = all(max(e_est(o, a) for o in lights) >= 1.0 for a in anchors)
        checks["character-lit"] = (lit, f"{len(anchors)} anchor(s)")
        key = by_name[spec["key"]]
        ekey = min(min(e_est(key, a) for a in anchors),
                   max(e_est(key, a) for a in anchors))
        lo, hi = spec["exposure"]
        checks["exposure-proxy"] = (lo <= ekey <= hi, f"E_key~{ekey:.1f} in [{lo},{hi}]")
    else:
        checks["character-lit"] = (True, "no characters")
        checks["exposure-proxy"] = (True, "no characters")

    # 3 face readability (close characters only; distant ships excluded)
    if anchors:
        key = by_name[spec["key"]]
        ratios = []
        for a in anchors:
            fill = sum(o.data.energy for o in lights
                       if o is not key and math.dist(world_pos(o), a) <= 6.0)
            ratios.append(fill / key.data.energy)
        checks["face-readability"] = (min(ratios) >= 0.08, f"min fill ratio {min(ratios):.2f}")
    else:
        checks["face-readability"] = (True, "no characters")

    # 4 materials from the registry
    bad = []
    for o in objs:
        if o.data is not None and hasattr(o.data, "materials"):
            mats = list(o.data.materials)
            if not mats or any(m is None or m.name not in MATS._BUILDERS for m in mats):
                bad.append(o.name)
    checks["materials"] = (not bad, f"{len(bad)} bare mesh(es)" if bad else "all registered")

    # 5 background not empty
    env = coll_objects(f"{sid}_ENV")
    wcolor, wstrength = world_settings(bpy.context.scene.world)
    checks["background"] = (len(env) >= 5 and wstrength >= 0.2,
                            f"{len(env)} env objects, world strength {wstrength}")

    # 6 design adherence
    probs = []
    for name, tune in spec["tune"].items():
        if name not in by_name:
            probs.append(f"{name} missing")
            continue
        for k, v in tune.items():
            if getattr(by_name[name].data, k) != v:
                probs.append(f"{name}.{k}={getattr(by_name[name].data, k)}!={v}")
    for name, ltype, energy, color, loc in spec["add"]:
        o = by_name.get(name)
        if o is None:
            probs.append(f"{name} fill missing")
            continue
        ad = getattr(o.data, "_animation_data", None)
        fc = [c for c in ad.action.fcurves if c.data_path == "energy"] if ad else []
        if fc:  # energy keyed (ignition swell) - the base key must match the plan
            if not any(abs(k.co[1] - energy) < 1e-6 for k in fc[0].keyframe_points):
                probs.append(f"{name} base energy keyed wrong")
        elif abs(o.data.energy - energy) > 1e-6:
            probs.append(f"{name} energy {o.data.energy}!={energy}")
    if list(wcolor) != list(spec["world"][0]) or wstrength != spec["world"][1]:
        probs.append("world mismatch")
    checks["design-adherence"] = (not probs, "; ".join(probs) or "matches plan")

    # 7 vfx objects + 8 wind direction
    wfails = []
    for entry in LD.VFX.get(sid, []):
        root = next((o for o in objs if o.name == entry["id"]), None)
        if root is None:
            wfails.append(f"{entry['id']} missing")
            continue
        if entry["kind"] in ("rain", "motes", "spray"):
            kids = [o for o in objs if o.parent is root]
            if len(kids) != entry["count"]:
                wfails.append(f"{entry['id']} {len(kids)}!={entry['count']}")
            if entry["kind"] == "rain" and sid in ("SC05", "SC06", "SC07"):
                if any(k.rotation_euler[1] <= 0 for k in kids):
                    wfails.append(f"{entry['id']} not slanted camera-right")
    checks["vfx-objects"] = (not wfails, "; ".join(wfails) or f"{len(LD.VFX.get(sid, []))} effect(s)")
    if sid in ("SC05", "SC06", "SC07"):
        checks["wind-direction"] = (not any("slanted" in f for f in wfails),
                                    "+X (camera-right) slant")

    # 10 shot timing (representative-frame keys)
    tfails = []
    if sid == "SC04":
        f0 = LR.SHOT_FRAMES["SC04_SH003"][0]
        r4 = next(o for o in objs if o.name == "RAIN_SC04")
        fc = [c for c in r4.animation_data.action.fcurves
              if c.data_path == "scale" and c.array_index == 2][0]
        frames = [k.co[0] for k in fc.keyframe_points]
        if f0 + 12 not in frames or not any(f <= f0 for f in frames):
            tfails.append(f"rain ignition not keyed at SH003+12 ({frames})")
    if sid == "SC07":
        f0 = LR.SHOT_FRAMES["SC07_SH008"][0]
        r7 = next(o for o in objs if o.name == "RAIN_SC07")
        fc = [c for c in r7.animation_data.action.fcurves
              if c.data_path == "scale" and c.array_index == 2][0]
        if not any(k.co[0] == f0 - 1 for k in fc.keyframe_points):
            tfails.append("lee calm not keyed at SH008")
    if sid == "SC08":
        f0 = LR.SHOT_FRAMES["SC08_SH007"][0]
        g = next(o for o in objs if o.name == "IGNITION_GLOW")
        fc = [c for c in g.animation_data.action.fcurves
              if c.data_path == "scale" and c.array_index == 0][0]
        if not any(k.co[0] == f0 for k in fc.keyframe_points):
            tfails.append("glow ignition not keyed at SH007")
    if sid in ("SC04", "SC07", "SC08"):
        checks["shot-timing"] = (not tfails, "; ".join(tfails) or "keys on approved frames")

    return checks


def main():
    os.makedirs(os.path.join(OUT_DIR, "vfx"), exist_ok=True)
    results, qc_lines = {}, []
    all_pass = True
    for sid in LD.SCENES:
        checks = run_scene(sid)
        ok = all(v[0] for v in checks.values())
        results[sid] = {"status": "VERIFIED" if ok else "FAILED", "checks": checks}
        all_pass &= ok
        mark = "VERIFIED" if ok else "FAILED"
        qc_lines.append(f"| {sid} | {mark} | " +
                        "; ".join(f"{k}: {'ok' if v[0] else 'FAIL — ' + str(v[1])}"
                                  for k, v in checks.items()) + " |")
        print(f"{sid}: {mark}  " + ", ".join(
            f"{k}{'✓' if v[0] else '✗ ' + str(v[1])}" for k, v in checks.items()))

    # 11 coverage: 58 shots with setup ref + grade note; effects have purpose
    shots_map, missing = {}, []
    for shot_id, sid in sorted(LR.SHOT_SCENE.items()):
        grade = LR.SHOT_GRADE.get(shot_id, "")
        if not grade:
            missing.append(shot_id)
        shots_map[shot_id] = dict(scene=sid, setup=SCENE_FILES[sid], grade=grade,
                                  frames=LR.SHOT_FRAMES[shot_id])
    no_purpose = [e["id"] for lst in LD.VFX.values() for e in lst if not e.get("purpose")]
    coverage_ok = not missing and not no_purpose and len(shots_map) == 58
    all_pass &= coverage_ok
    qc_lines.append(f"| ALL | {'VERIFIED' if coverage_ok else 'FAILED'} | coverage: "
                    f"{len(shots_map)}/58 shots with setup+grade; purposeless effects: "
                    f"{len(no_purpose)} |")
    print(f"coverage: {len(shots_map)}/58 shots | purposeless effects: {len(no_purpose)}")

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    plan = dict(
        schema_version=1, task_id="T08_LIGHTING_VFX", project_id="AMS-001",
        film_title="NINETY-TWO TURNS", fps=24, generated=now,
        design_rules=[
            "one shadow-casting light per scene (the planned key) — coherent shadows",
            "warm fill within 6 m of every close character — faces stay readable",
            "wind is camera-right (+X) in storm scenes SC05-07 (CONTINUITY_BIBLE §4)",
            "rain begins exactly at SC04_SH003, full storm SC05-07, lee calm at "
            "SC07_SH008, drizzle SC09, clear dawn SC10",
            "world shader never black — depth from gradient, not void",
            "all materials from the registered 06_ASSETS library (18 entries)",
            "no effect without a story purpose (every VFX row carries one)",
        ],
        scenes={sid: dict(
            time=LD.LIGHTING[sid]["time"], mood=LD.LIGHTING[sid]["mood"],
            world=dict(color=list(LD.LIGHTING[sid]["world"][0]),
                       strength=LD.LIGHTING[sid]["world"][1]),
            key=LD.LIGHTING[sid]["key"],
            shadow_casters=list(LD.LIGHTING[sid]["shadow_casters"]),
            tuned=LD.LIGHTING[sid]["tune"],
            added=[dict(zip(("name", "type", "energy", "color", "location"), a))
                   for a in LD.LIGHTING[sid]["add"]],
            exposure=LD.LIGHTING[sid]["exposure"],
            file=SCENE_FILES[sid],
            status=results[sid]["status"],
        ) for sid in LD.SCENES},
        shots=shots_map,
    )
    effects = []
    for sid in LD.SCENES:
        for e in LD.VFX.get(sid, []):
            effects.append(dict(
                scene=sid, id=e["id"], kind=e["kind"], purpose=e["purpose"],
                shots=e.get("start_shot") or e.get("shot") or e.get("shots") or "scene-wide",
                material={"rain": "MAT_RAIN_STREAK", "fog": "MAT_FOG_BANK",
                          "motes": "MAT_DUST_MOTE", "spray": "MAT_RAIN_STREAK",
                          "glow": "MAT_AMBER_GLOW"}[e["kind"]],
                object=e["id"], status="VERIFIED" if results[sid]["status"] == "VERIFIED"
                else "FAILED", **{k: v for k, v in e.items()
                                  if k not in ("id", "kind", "purpose", "shots", "shot",
                                               "start_shot", "calm_shot")},
            ))
    vfx_plan = dict(
        schema_version=1, task_id="T08_LIGHTING_VFX", generated=now,
        policy="no effect without story purpose — every row below carries one",
        wind="camera-right (+X) in SC05-07 per CONTINUITY_BIBLE §4",
        rain_timeline="begins SC04_SH003, full storm SC05-07, lee calm SC07_SH008, "
                      "drizzle SC09, clear SC10",
        effects=effects,
    )
    index = dict(schema_version=1, task_id="T08_LIGHTING_VFX", generated=now,
                 scenes=[dict(scene_id=sid, file=SCENE_FILES[sid],
                              key=LD.LIGHTING[sid]["key"],
                              world_strength=LD.LIGHTING[sid]["world"][1],
                              status=results[sid]["status"]) for sid in LD.SCENES])
    vindex = dict(schema_version=1, task_id="T08_LIGHTING_VFX", generated=now,
                  effects=[dict(id=e["id"], scene=e["scene"], kind=e["kind"],
                                purpose=e["purpose"], object=e["object"],
                                status=e["status"]) for e in effects])

    for name, doc in (("LIGHTING_PLAN.json", plan), ("VFX_PLAN.json", vfx_plan),
                      ("LIGHTING_INDEX.json", index)):
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2)
            fh.write("\n")
    with open(os.path.join(OUT_DIR, "vfx", "VFX_INDEX.json"), "w", encoding="utf-8") as fh:
        json.dump(vindex, fh, indent=2)
        fh.write("\n")

    qc = ["# Stage 09 — Lighting/VFX QC (NINETY-TWO TURNS)", "",
          f"Generated: {now} · harness: `run_lighting_tests.py` (structural, stub bpy)", "",
          "Checks per scene: shadow-coherence, character-lit, face-readability, materials,",
          "background, design-adherence, vfx-objects, wind-direction (storm scenes),",
          "exposure-proxy, shot-timing (SC04/07/08). Global: 58/58 shot coverage with",
          "setup ref + grade note; every effect has a story purpose.", "",
          "**Exposure note:** `exposure-proxy` is a structural estimate (key-light energy at",
          "the character anchor). Broadcast-range legality on real frames is measured at",
          "render QC in task T11 — not claimed here.", "",
          "| Scene | Status | Detail |", "|---|---|---|"] + qc_lines + [""]
    with open(os.path.join(OUT_DIR, "LIGHTING_QC.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(qc))

    print("PASS" if all_pass else "FAIL")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
