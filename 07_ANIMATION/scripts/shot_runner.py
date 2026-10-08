"""
shot_runner - executes one shot's animation on top of its built scene.

Used by the generated 07_ANIMATION/SHOT_ANIMATION/anim_<SHOT>.py scripts and by
the harness. Only the target shot's frame range is keyed - the film is never
animated in one operation.
"""

import bpy

import ams_assets
import ams_anim_lib as AN
from shot_specs import SPECS, PRINCIPLES

RAD = AN.RAD


def _all_objects():
    out = []

    def rec(c):
        for o in list(c.objects):
            out.append(o)
        for ch in list(c.children):
            rec(ch)
    rec(bpy.context.scene.collection)
    return out


def _top(name):
    hits = [o for o in _all_objects() if o.name == name]
    if not hits:
        raise KeyError(f"no object {name} in scene")
    return hits[0]


def resolve(tok):
    if tok == "WICK":
        return _top("CHAR_WICK")
    if tok == "CHILD":
        return _top("CHAR_CHILD")
    if tok == "SHIP":
        return _top("CHAR_SHIP")
    if tok == "WICK_HEAD":
        return AN.child(_top("CHAR_WICK"), "WICK_head")
    if tok == "WICK_EYES":
        w = _top("CHAR_WICK")
        return [AN.child(w, "WICK_eyeL"), AN.child(w, "WICK_eyeR")]
    if tok == "GAUGE":
        return AN.child(_top("CHAR_WICK"), "PROP_GAUGE")
    if tok == "KEY_WICK":
        return AN.child(_top("CHAR_WICK"), "PROP_KEY")
    if tok == "KEY_CHILD":
        return AN.child(_top("CHAR_CHILD"), "PROP_KEY")
    if tok == "SPARK":
        return AN.child(_top("CHAR_WICK"), "PROP_SPARK")
    if tok == "COIL":
        return AN.child(_top("CHAR_WICK"), "WICK_coil")
    if tok == "POLE":
        return _top("PROP_POLE")
    if tok == "DOOR":
        return _top("PROP_DOOR")
    if tok == "STAIR":
        return _top("PROP_STAIR")
    if tok == "RAIL":
        return _top("PROP_RAIL")
    if tok == "GANTRY":
        return _top("STREETS_gantry_walk")
    if tok == "BUOY":
        return _top("PROP_BELLBUOY")
    if tok == "SPOT":
        hits = [o for o in _all_objects() if o.data is not None and getattr(o.data, "type", "") == "SPOT"]
        return hits[0]
    if tok.startswith("LIGHT_"):
        lights = [o for o in _all_objects() if o.data is not None and hasattr(o.data, "energy")]
        return lights[int(tok.split("_")[1])]
    raise KeyError(tok)


# ---------------------------------------------------------------------- #
# runner-local micro primitives
# ---------------------------------------------------------------------- #
def _turns_free(o, f0, f1, turns=3):
    n = 0
    for i in range(turns):
        a, b = i / turns, (i + 0.7) / turns
        n += AN.key(o, AN.fr(f0, f1, a), rot=(0, 0, RAD(360 * i)))
        n += AN.key(o, AN.fr(f0, f1, b), rot=(0, 0, RAD(360 * (i + 1))))
        n += AN.key(o, AN.fr(f0, f1, min(b + 0.1, 1.0)), rot=(0, 0, RAD(360 * (i + 1))))
    AN.spacing(o, "LINEAR")
    return n


def _needle_tremble(g, f0, f1, v=92):
    nd = AN.child(g, "GAUGE_needle")
    r = AN.gauge_value_to_rot(v)
    n = AN.key(nd, f0, rot=(0, 0, r))
    n += AN.key(nd, AN.fr(f0, f1, 0.3), rot=(0, 0, r + RAD(2)))
    n += AN.key(nd, AN.fr(f0, f1, 0.5), rot=(0, 0, r - RAD(1.5)))
    n += AN.key(nd, f1, rot=(0, 0, r))
    AN.spacing(nd)
    return n


def _lift_pole(actor, pole, f0, f1):
    x, y, z = actor.location
    n = AN.key(pole, f0, loc=(x + 0.15, y, 0.02), rot=(0, RAD(90), 0))
    n += AN.key(pole, AN.fr(f0, f1, 0.5), loc=(x + 0.06, y + 0.05, 0.3), rot=(0, RAD(35), 0))
    n += AN.key(pole, f1, loc=(x + 0.05, y + 0.05, 0.35), rot=(0, 0, 0))
    AN.spacing(pole)
    return n


def _carry_pole(pole, f0, f1, delta=(0, 0), dz=0.0):
    x, y, z = pole.location
    n = AN.key(pole, f0, loc=(x, y, z))
    n += AN.key(pole, f1, loc=(x + delta[0], y + delta[1], z + dz))
    AN.spacing(pole)
    return n


def _pole_horizontal(pole, f0, f1):
    n = AN.key(pole, f0, rot=(0, 0, 0))
    n += AN.key(pole, f1, rot=(0, RAD(90), 0))
    AN.spacing(pole)
    return n


def _shield_arm(actor, f0, f1):
    a = AN.child(actor, "WICK_armR")
    n = AN.key(a, f0, rot=(0, RAD(-18), 0))
    n += AN.key(a, f1, rot=(RAD(-90), 0, RAD(35)))
    AN.spacing(a)
    return n


def _swing_one_arm(actor, f0, f1, amp=14, period=28):
    a = AN.child(actor, "WICK_armL")
    n = AN.sway(a, f0, f1, amp=amp, period=period, axis=0)
    n += AN.sway(actor, f0, f1, amp=amp / 4, period=period, axis=1)
    return n


def _coil_catch(actor, f0, f1):
    c = AN.child(actor, "WICK_coil")
    h = AN.child(actor, "WICK_head")
    n = AN.key(c, f0, scale=(0.2, 0.2, 1))
    n += AN.key(c, AN.fr(f0, f1, 0.5), scale=(0.26, 0.26, 1))
    AN.spacing(c, "CONSTANT")
    n += AN.key(h, f0, rot=(RAD(24), 0, 0))
    n += AN.key(h, f1, rot=(RAD(6), 0, 0))
    AN.spacing(h)
    return n


def _settle(o, f0, f1):
    z = o.rotation_euler[2]
    n = AN.key(o, f0, rot=(0, 0, z))
    n += AN.key(o, AN.fr(f0, f1, 0.4), rot=(0, 0, z - RAD(6)))
    n += AN.key(o, f1, rot=(0, 0, z))
    AN.spacing(o)
    return n


def _dim(light, f0, f1, peak=2000.0):
    n = AN._light_key(light, f0, peak)
    n += AN._light_key(light, f1, 40.0)
    AN.spacing(AN._ldata(light), "LINEAR")
    return n


# ---------------------------------------------------------------------- #
# dispatch table: name -> adapter(p, f0, f1); p carries resolved objects
# ---------------------------------------------------------------------- #
TABLE = {
    "walk": lambda p, a, b: AN.walk(p["actor"], a, b, **{k: v for k, v in p.items() if k != "actor"}),
    "climb": lambda p, a, b: AN.climb(p["actor"], a, b, **{k: v for k, v in p.items() if k != "actor"}),
    "brace": lambda p, a, b: AN.brace(p["actor"], a, b, **{k: v for k, v in p.items() if k != "actor"}),
    "collapse": lambda p, a, b: AN.collapse(p["actor"], a, b, **{k: v for k, v in p.items() if k != "actor"}),
    "stutter": lambda p, a, b: AN.stutter(p["actor"], a, b, **{k: v for k, v in p.items() if k != "actor"}),
    "drop_under": lambda p, a, b: AN.drop_under(p["actor"], a, b, **{k: v for k, v in p.items() if k != "actor"}),
    "offer": lambda p, a, b: AN.offer(p["actor"], a, b, **{k: v for k, v in p.items() if k != "actor"}),
    "unspool": lambda p, a, b: AN.unspool(p["actor"], a, b),
    "reach_grab": lambda p, a, b: AN.reach_grab(p["actor"], a, b),
    "look": lambda p, a, b: AN.look(p["head"], a, b, p["rot"]),
    "hold": lambda p, a, b: AN.hold(p["obj"], a, b),
    "iris": lambda p, a, b: AN.iris(p["eyes"], a, b, p.get("a", 1.0), p.get("b", 0.2)),
    "needle": lambda p, a, b: AN.needle(p["gauge"], a, b, p.get("v0"), p.get("v1"), p.get("stepped", False)),
    "needle_tremble": lambda p, a, b: _needle_tremble(p["gauge"], a, b, p.get("v", 92)),
    "key_slip": lambda p, a, b: AN.key_slip(p["obj"], a, b, p.get("turns", 4)),
    "turns_free": lambda p, a, b: _turns_free(p["obj"], a, b, p.get("turns", 3)),
    "turn_key": lambda p, a, b: AN.turn_key(None, p["key_obj"], a, b, p.get("turns", 1)),
    "spin_away": lambda p, a, b: AN.spin_away(p["obj"], a, b, p.get("direction", (1, 0.3)), p.get("turns", 3)),
    "push_door": lambda p, a, b: AN.push_door(p["actor"], p["door"], a, b),
    "kneel_turn": lambda p, a, b: AN.kneel_turn(p["actor"], a, b, p["key_obj"]),
    "flicker": lambda p, a, b: AN.flicker(p["light"], a, b, p.get("base", 50), p.get("amp", 8), p.get("seed", 7)),
    "bob": lambda p, a, b: AN.bob(p["obj"], a, b, p.get("amp", 0.05), p.get("period", 48)),
    "sway": lambda p, a, b: AN.sway(p["obj"], a, b, p.get("amp", 2), p.get("period", 40), p.get("axis", 0)),
    "tear_fall": lambda p, a, b: AN.tear_fall(p["obj"], a, b, p.get("drop", 6)),
    "bloom": lambda p, a, b: AN.bloom(p["light"], a, b, p.get("delay", 0.35), p.get("peak", 2000)),
    "dim": lambda p, a, b: _dim(p["light"], a, b, p.get("peak", 2000)),
    "beam_sweep": lambda p, a, b: AN.beam_sweep(p["spot"], a, b, p.get("deg", 140)),
    "reveal_scale": lambda p, a, b: AN.reveal_scale(p["obj"], a, b),
    "ship_turn": lambda p, a, b: AN.ship_turn(p["ship"], a, b, p.get("deg", 35)),
    "lift_pole": lambda p, a, b: _lift_pole(p["actor"], p["pole"], a, b),
    "carry_pole": lambda p, a, b: _carry_pole(p["pole"], a, b, p.get("delta", (0, 0)), p.get("dz", 0.0)),
    "pole_horizontal": lambda p, a, b: _pole_horizontal(p["pole"], a, b),
    "shield_arm": lambda p, a, b: _shield_arm(p["actor"], a, b),
    "swing_one_arm": lambda p, a, b: _swing_one_arm(p["actor"], a, b, p.get("amp", 14), p.get("period", 28)),
    "coil_catch": lambda p, a, b: _coil_catch(p["actor"], a, b),
    "settle": lambda p, a, b: _settle(p["key_obj"], a, b),
}

TOK_ARG = {"obj", "actor", "head", "eyes", "gauge", "pole", "door", "key_obj",
           "ship", "spot", "light", "stair", "rail", "gantry", "buoy"}


def dispatch(name, kw, f0, f1):
    p = {}
    for k, v in kw.items():
        if k in ("t0", "t1"):
            continue
        p[k] = resolve(v) if (k in TOK_ARG and isinstance(v, str)) else v
    a0, a1 = AN.fr(f0, f1, kw.get("t0", 0.0)), AN.fr(f0, f1, kw.get("t1", 1.0))
    return TABLE[name](p, a0, a1)


def build_shot(shot_id, shot_record):
    f0, f1 = int(shot_record["frame_in"]), int(shot_record["frame_out"])
    ams_assets.build_scene(shot_record["scene_id"])
    spec = SPECS[shot_id]
    total, used = 0, []
    for name, kw in spec["acts"]:
        total += dispatch(name, kw, f0, f1)
        used.append(name)
    # gauge continuity: if the shot has a gauge value but no needle act, hold it
    if shot_record.get("gauge_in") is not None and not any(
            u in ("needle", "needle_tremble") for u in used):
        try:
            total += dispatch("needle", {"gauge": "GAUGE", "v0": shot_record["gauge_in"],
                                         "v1": shot_record.get("gauge_out", shot_record["gauge_in"]),
                                         "t0": 0.0, "t1": 1.0}, f0, f1)
            used.append("needle_hold")
        except KeyError:
            pass  # scenes without WICK (e.g. SC09) carry no gauge
    principles = sorted({pr for u in used for pr in PRINCIPLES.get(u, [])})
    return {"shot_id": shot_id, "frame_start": f0, "frame_end": f1,
            "keys": total, "principles": principles, "acts": used,
            "note": spec["note"]}
