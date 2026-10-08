"""
ams_anim_lib - procedural character/prop/environment animation primitives.

Every primitive encodes professional principles explicitly:
  anticipation (pre-keys), spacing (interpolation choice), arcs (mid-keys),
  weight (asymmetric ease in/out), follow-through & overlapping action
  (settle keys after the driver stops), secondary action (bob/sway/flicker).

Runs under real Blender and under tools/blender_stub. Camera movement is NEVER
used as a substitute for missing body animation here - camera placeholders stay
static; all motion lives on objects and lights.
"""

import math
import random

RAD = math.radians


# ---------------------------------------------------------------------- #
# core
# ---------------------------------------------------------------------- #
def fr(f0, f1, t):
    return int(round(f0 + (f1 - f0) * t))


def key(obj, frame, loc=None, rot=None, scale=None):
    n = 0
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert("location", frame=frame)
        n += 1
    if rot is not None:
        obj.rotation_euler = rot
        obj.keyframe_insert("rotation_euler", frame=frame)
        n += 1
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert("scale", frame=frame)
        n += 1
    return n


def spacing(obj, interp="BEZIER"):
    """Apply spacing to every fcurve on obj (BEZIER=eased, LINEAR=even, CONSTANT=step)."""
    ad = obj.animation_data
    for fc in ad.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = interp


def child(root, name):
    stack = [root]
    while stack:
        o = stack.pop()
        if o.name == name:
            return o
        stack.extend(list(o.children))
    raise KeyError(f"{name} under {root.name}")


def children_named(root, name):
    out, stack = [], [root]
    while stack:
        o = stack.pop()
        if o.name == name:
            out.append(o)
        stack.extend(list(o.children))
    return out


def hold(obj, f0, f1):
    n = key(obj, f0, loc=obj.location, rot=obj.rotation_euler)
    n += key(obj, f1, loc=obj.location, rot=obj.rotation_euler)
    return n


# ---------------------------------------------------------------------- #
# body primitives
# ---------------------------------------------------------------------- #
def walk(root, f0, f1, dist=(-0.4, 0.0), stride=0.06, prefix="WICK", arc=0.006):
    """Full walk: anticipation crouch, stride swing on limbs, hip bob on arcs,
    follow-through settle. Returns key count."""
    d = math.hypot(*dist)
    steps = max(2, int(d / stride))
    x0, y0, z0 = root.location
    n = key(root, f0, loc=(x0, y0, z0 - 0.004), rot=(RAD(2), 0, root.rotation_euler[2]))  # anticipation
    n += key(root, fr(f0, f1, 0.08), loc=(x0, y0, z0))
    legL, legR = child(root, prefix + "_legL"), child(root, prefix + "_legR")
    armL = children_named(root, prefix + "_armL")
    armR = children_named(root, prefix + "_armR")
    for i in range(steps + 1):
        t = 0.08 + 0.88 * i / steps
        f = fr(f0, f1, min(t, 0.96))
        px = x0 + dist[0] * (t - 0.08) / 0.88
        py = y0 + dist[1] * (t - 0.08) / 0.88
        bob = arc if i % 2 else 0.0
        n += key(root, f, loc=(px, py, z0 + bob))
        s = 1 if i % 2 else -1
        n += key(legL, f, rot=(RAD(22 * s), 0, 0))
        n += key(legR, f, rot=(RAD(-22 * s), 0, 0))
        if armL:
            n += key(armL[0], f, rot=(0, RAD(18 + 8 * -s), 0))
        if armR:
            n += key(armR[0], f, rot=(0, RAD(-18 + 8 * s), 0))
    n += key(root, fr(f0, f1, 0.98), loc=(x0 + dist[0], y0 + dist[1], z0 + 0.002))  # follow-through
    n += key(root, f1, loc=(x0 + dist[0], y0 + dist[1], z0), rot=(0, 0, root.rotation_euler[2]))
    spacing(root)
    spacing(legL)
    spacing(legR)
    return n


def climb(root, f0, f1, height=0.8, reaches=4, prefix="WICK"):
    z0 = root.location[2]
    armL, armR = child(root, prefix + "_armL"), child(root, prefix + "_armR")
    n = key(root, f0, loc=root.location)
    for i in range(reaches):
        t0, t1 = i / reaches, (i + 1) / reaches
        a = armL if i % 2 else armR
        other = armR if i % 2 else armL
        n += key(a, fr(f0, f1, min(1.0, t0 + 0.1)), rot=(RAD(-70), 0, 0))     # reach up (arc via bez)
        n += key(other, fr(f0, f1, min(1.0, t0 + 0.2)), rot=(RAD(-20), 0, 0)) # overlap
        n += key(root, fr(f0, f1, t1), loc=(root.location[0], root.location[1],
                                            z0 + height * (i + 1) / reaches))
        n += key(root, fr(f0, f1, t1), rot=(0, RAD(3 if i % 2 else -3), 0))  # weight sway
    n += key(root, f1, rot=(0, 0, 0))
    spacing(root, "BEZIER")
    return n


def brace(root, f0, f1, lean=RAD(12)):
    n = key(root, f0, rot=(0, 0, 0))
    n += key(root, fr(f0, f1, 0.25), rot=(lean * 0.6, 0, 0))     # anticipation-ish dip
    n += key(root, fr(f0, f1, 0.45), rot=(lean, 0, 0))           # strain
    n += key(root, fr(f0, f1, 0.7), rot=(lean * 1.12, 0, 0))     # overshoot gust
    n += key(root, f1, rot=(lean, 0, 0))                          # hold against wind
    spacing(root)
    return n


def collapse(root, f0, f1, tilt=RAD(78)):
    n = key(root, f0, rot=(0, 0, 0))
    n += key(root, fr(f0, f1, 0.55), rot=(tilt * 0.2, 0, 0))     # exhausted slow lean
    n += key(root, fr(f0, f1, 0.8), rot=(tilt, 0, 0))            # give way (fast, weight)
    n += key(root, fr(f0, f1, 0.9), rot=(tilt * 0.94, 0, 0))     # follow-through bounce
    n += key(root, f1, rot=(tilt, 0, 0))
    spacing(root)
    return n


def look(head_or_root, f0, f1, rot_target, prefix="WICK", overshoot=1.15):
    n = key(head_or_root, f0, rot=(0, 0, 0))
    n += key(head_or_root, fr(f0, f1, 0.6),
             rot=tuple(v * overshoot for v in rot_target))
    n += key(head_or_root, f1, rot=rot_target)
    spacing(head_or_root)
    return n


def iris(eyes, f0, f1, a=1.0, b=0.2):
    """Shutter-aperture facial performance for WICK's eyes."""
    n = 0
    for e in eyes:
        n += key(e, f0, scale=(1, a, 1))
        n += key(e, fr(f0, f1, 0.7), scale=(1, b * 0.85, 1))   # overshoot
        n += key(e, f1, scale=(1, b, 1))
        spacing(e)
    return n


def head_drop(head, f0, f1):
    n = key(head, f0, rot=(0, 0, 0))
    n += key(head, fr(f0, f1, 0.8), rot=(RAD(28), 0, 0))
    n += key(head, f1, rot=(RAD(24), 0, 0))
    spacing(head)
    return n


# ---------------------------------------------------------------------- #
# props
# ---------------------------------------------------------------------- #
def gauge_value_to_rot(v):
    return RAD(225 - 2.7 * v) - RAD(90)


def needle(gauge_root, f0, f1, v0, v1, stepped=False):
    nd = child(gauge_root, "GAUGE_needle")
    n = 0
    if stepped and v0 is not None and v1 is not None and abs(v0 - v1) >= 1:
        step = 1 if v1 > v0 else -1
        vals = list(range(int(v0), int(v1) + step, step))
        for i, v in enumerate(vals):
            n += key(nd, fr(f0, f1, i / max(1, len(vals) - 1)), rot=(0, 0, gauge_value_to_rot(v)))
        spacing(nd, "CONSTANT")
    else:
        n += key(nd, f0, rot=(0, 0, gauge_value_to_rot(v0 if v0 is not None else 0)))
        n += key(nd, f1, rot=(0, 0, gauge_value_to_rot(v1 if v1 is not None else 0)))
        spacing(nd)
    return n


def spin_away(obj, f0, f1, direction=(1.0, 0.3), turns=3.0, gust_t=0.35):
    x0, y0, z0 = obj.location
    n = key(obj, f0, loc=(x0, y0, z0), rot=(0, 0, 0))
    n += key(obj, fr(f0, f1, gust_t), loc=(x0, y0, z0), rot=(0, 0, RAD(8)))  # held, then gust
    n += key(obj, fr(f0, f1, gust_t + 0.05), rot=(0, 0, RAD(30)))
    n += key(obj, f1, loc=(x0 + direction[0] * 4, y0 + direction[1] * 2, z0 - 1.2),
             rot=(0, 0, RAD(360 * turns)))
    spacing(obj, "LINEAR")
    return n


def reach_grab(root, f0, f1, prefix="WICK", arm="R"):
    a = child(root, prefix + "_arm" + arm)
    n = key(a, f0, rot=(0, RAD(-18), 0))
    n += key(a, fr(f0, f1, 0.3), rot=(RAD(20), 0, 0))            # anticipation back
    n += key(a, fr(f0, f1, 0.6), rot=(RAD(-95), 0, 0))           # extend
    n += key(a, fr(f0, f1, 0.7), rot=(RAD(-102), 0, 0))          # overshoot
    n += key(a, f1, rot=(RAD(-90), 0, 0))                        # grip settle
    spacing(a)
    return n


def push_door(root, door, f0, f1):
    n = key(root, f0, rot=(0, 0, 0))
    n += key(root, fr(f0, f1, 0.25), rot=(RAD(14), 0, 0))        # push 1
    n += key(root, fr(f0, f1, 0.4), rot=(RAD(4), 0, 0))          # reset
    n += key(root, fr(f0, f1, 0.7), rot=(RAD(18), 0, 0))         # push 2 (heavier)
    n += key(root, f1, rot=(RAD(8), 0, 0))
    m = key(door, f0, rot=(0, 0, 0))
    m += key(door, fr(f0, f1, 0.28), rot=(0, 0, RAD(4)))
    m += key(door, fr(f0, f1, 0.75), rot=(0, 0, RAD(38)))
    m += key(door, f1, rot=(0, 0, RAD(42)))
    spacing(root)
    spacing(door, "BEZIER")
    return n + m


def turn_key(actor_root, key_obj, f0, f1, turns=1):
    n = 0
    for i in range(turns):
        t0, t1 = i / turns, (i + 0.5) / turns
        n += key(key_obj, fr(f0, f1, t0), rot=(0, 0, RAD(360 * i)))
        n += key(key_obj, fr(f0, f1, t1), rot=(0, 0, RAD(360 * (i + 1))))
    spacing(key_obj, "CONSTANT")   # ratchet clicks
    return n


def unspool(root, f0, f1):
    spring = child(root, "WICK_coil")
    head = child(root, "WICK_head")
    n = key(spring, f0, scale=(1, 1, 1))
    for i in range(1, 7):
        n += key(spring, fr(f0, f1, i / 7), scale=(1 - 0.13 * i, 1 - 0.13 * i, 1))
    spacing(spring, "LINEAR")
    n += head_drop(head, fr(f0, f1, 0.6), f1)
    return n


def kneel_turn(root, f0, f1, key_obj):
    n = key(root, f0, loc=root.location)
    n += key(root, fr(f0, f1, 0.4), loc=(root.location[0], root.location[1],
                                         root.location[2] - 0.18))          # kneel
    n += key(root, fr(f0, f1, 0.55), loc=(root.location[0], root.location[1],
                                          root.location[2] - 0.16))          # settle
    m = turn_key(root, key_obj, fr(f0, f1, 0.7), f1, turns=1)
    return n + m


# ---------------------------------------------------------------------- #
# environment / secondary
# ---------------------------------------------------------------------- #
def flicker(light, f0, f1, base=50.0, amp=8.0, seed=7, step=6):
    rnd = random.Random(seed)
    n = 0
    f = f0
    while f <= f1:
        n += _light_key(light, f, base + rnd.uniform(-amp, amp))
        f += step
    spacing(light, "LINEAR")
    return n


def _light_key(light, frame, energy):
    light.energy = energy
    light.keyframe_insert("energy", frame=frame)
    return 1


def bob(obj, f0, f1, amp=0.05, period=48, rot_amp=1.5):
    n = 0
    f = f0
    i = 0
    while f <= f1:
        ph = 2 * math.pi * i / 4
        n += key(obj, f, loc=(obj.location[0], obj.location[1],
                              obj.location[2] + amp * math.sin(ph)),
                 rot=(RAD(rot_amp) * math.sin(ph + 1.0), 0, obj.rotation_euler[2]))
        f += max(4, period // 4)
        i += 1
    spacing(obj, "BEZIER")
    return n


def sway(obj, f0, f1, amp=2.0, period=40, axis=0):
    n = 0
    f, i = f0, 0
    while f <= f1:
        ph = 2 * math.pi * i / 4
        r = [0, 0, 0]
        r[axis] = RAD(amp) * math.sin(ph)
        n += key(obj, f, rot=tuple(r))
        f += max(4, period // 4)
        i += 1
    spacing(obj)
    return n


def tear_fall(obj, f0, f1, drop=6.0, shake=4):
    x0, y0, z0 = obj.location
    n = key(obj, f0, loc=(x0, y0, z0))
    for i in range(1, shake + 1):                                     # shudder anticipation
        n += key(obj, f0 + i, loc=(x0 + 0.01 * (1 if i % 2 else -1), y0, z0))
    n += key(obj, f0 + shake + 2, loc=(x0, y0, z0 - 0.05))
    n += key(obj, f1, loc=(x0 + 0.4, y0, z0 - drop), rot=(RAD(25), 0, 0))  # accelerating fall
    spacing(obj, "LINEAR")
    return n


def bloom(light, f0, f1, delay=0.35, peak=2000.0):
    n = _light_key(light, f0, 0.0)
    n += _light_key(light, fr(f0, f1, delay), 0.0)          # beat of black
    n += _light_key(light, fr(f0, f1, delay) + 3, peak)     # ignition snap
    n += _light_key(light, f1, peak)
    spacing(light, "CONSTANT")
    return n


def beam_sweep(spot, f0, f1, deg=140):
    z0 = spot.rotation_euler[2]
    n = key(spot, f0, rot=(spot.rotation_euler[0], spot.rotation_euler[1], z0))
    n += key(spot, f1, rot=(spot.rotation_euler[0], spot.rotation_euler[1], z0 + RAD(deg)))
    spacing(spot, "LINEAR")
    return n


# ---------------------------------------------------------------------- #
# shot-specific primitives
# ---------------------------------------------------------------------- #
def key_slip(key_obj, f0, f1, turns=4):
    """Winding: discrete ratchet turns, then the fourth-turn slip with recoil."""
    n = 0
    for i in range(turns):
        n += key(key_obj, fr(f0, f1, i / (turns + 1)), rot=(0, 0, RAD(360 * i)))
        n += key(key_obj, fr(f0, f1, (i + 0.5) / (turns + 1)), rot=(0, 0, RAD(360 * (i + 1))))
    spacing(key_obj, "CONSTANT")
    n += key(key_obj, fr(f0, f1, 0.85), rot=(0, 0, RAD(360 * turns + 25)))   # slip overshoot
    n += key(key_obj, f1, rot=(0, 0, RAD(360 * turns + 18)))                  # recoil settle
    return n


def stutter(root, f0, f1, dist=0.15, prefix="WICK", seed=5):
    """Degraded gait: irregular spacing, spasmic limb keys - rhythm deliberately broken."""
    rnd = random.Random(seed)
    x0, y0, z0 = root.location
    legL, legR = child(root, prefix + "_legL"), child(root, prefix + "_legR")
    n = key(root, f0, loc=(x0, y0, z0))
    t = 0.0
    i = 0
    while t < 0.95:
        t += rnd.uniform(0.08, 0.22)
        adv = rnd.uniform(0.2, 1.0) * dist / 5
        n += key(root, fr(f0, f1, min(t, 0.95)),
                 loc=(x0 - adv * i, y0, z0 + (0.002 if i % 2 else 0)), rot=(RAD(rnd.uniform(0, 6)), 0, 0))
        n += key(legL, fr(f0, f1, min(t, 0.95)), rot=(RAD(rnd.uniform(-14, 20)), 0, 0))
        n += key(legR, fr(f0, f1, min(t, 0.95)), rot=(RAD(rnd.uniform(-20, 14)), 0, 0))
        i += 1
    n += key(root, f1, loc=(x0 - dist, y0, z0))
    spacing(root, "LINEAR")
    return n


def drop_under(root, f0, f1, depth=0.6):
    """Grip fails: fast fall with flail, then water drag (linear, heavy)."""
    x0, y0, z0 = root.location
    n = key(root, f0, loc=(x0, y0, z0))
    n += key(root, fr(f0, f1, 0.1), loc=(x0, y0, z0 + 0.01))      # last grip
    n += key(root, fr(f0, f1, 0.45), loc=(x0, y0, z0 - depth), rot=(RAD(40), 0, RAD(90)))
    n += key(root, f1, loc=(x0, y0, z0 - depth - 0.05), rot=(RAD(55), 0, RAD(120)))
    spacing(root, "LINEAR")
    a = child(root, "WICK_armL")
    n += sway(a, f0, f1, amp=25, period=16)
    return n


def offer(root, f0, f1, twice=True, prefix="WICK"):
    """Offer the spark: reach, nothing, reset, reach again (overlapping arm/head)."""
    a = child(root, prefix + "_armR")
    h = child(root, prefix + "_head")
    n = key(a, f0, rot=(0, RAD(-18), 0))
    n += key(a, fr(f0, f1, 0.3), rot=(RAD(-80), 0, 0))
    n += key(h, fr(f0, f1, 0.35), rot=(RAD(10), 0, 0))            # head follows, late
    if twice:
        n += key(a, fr(f0, f1, 0.5), rot=(RAD(-30), 0, 0))        # reset
        n += key(a, fr(f0, f1, 0.75), rot=(RAD(-88), 0, 0))       # reposition, try again
        n += key(h, fr(f0, f1, 0.8), rot=(RAD(14), 0, 0))
    n += key(a, f1, rot=(RAD(-70), 0, 0))
    n += key(h, f1, rot=(RAD(18), 0, 0))                          # droop of understanding
    spacing(a)
    spacing(h)
    return n


def reveal_scale(obj, f0, f1, s0=0.0, s1=1.0):
    n = key(obj, f0, scale=(s0, s0, s0))
    n += key(obj, fr(f0, f1, 0.7), scale=(s1 * 1.1, s1 * 1.1, s1 * 1.1))
    n += key(obj, f1, scale=(s1, s1, s1))
    spacing(obj)
    return n


def ship_turn(ship, f0, f1, deg=35):
    """Ponderous turn toward harbour - slow ease, no snap."""
    z0 = ship.rotation_euler[2]
    n = key(ship, f0, rot=(0, 0, z0))
    n += key(ship, fr(f0, f1, 0.4), rot=(0, 0, z0))               # pause before turning
    n += key(ship, f1, rot=(0, RAD(4), z0 + RAD(deg)))
    spacing(ship)
    return n
