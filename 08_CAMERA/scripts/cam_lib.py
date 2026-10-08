"""
cam_lib - cinematography primitives: executable camera direction.

Conventions (match Blender and the scene builders):
  * a camera looks along its local -Z; with rotation_euler (pitch, 0, yaw)
    and yaw=0 it faces +Y; positive pitch tilts it down.
  * master axis: sea/ship +X == FRAME RIGHT, tower -X == FRAME LEFT for the
    default camera side (-Y of the subject). Reverse setups flag `reverse`.
  * every move is motivated; nothing shakes. The only fast move in the film
    is the SC06_SH002 whip; "handheld" beats are a single slow drift, not noise.
  * sensor 36x20.25mm (16:9). frame_height(d) = d * 20.25 / lens  (mm->m).
"""

import math

RAD = math.radians
SENSOR_H = 0.02025  # metres, 16:9 on a 36mm sensor


def frame_height(dist, lens):
    return dist * SENSOR_H / (lens / 1000.0)


def vfov(lens):
    return 2 * math.atan((SENSOR_H / 2) / (lens / 1000.0))


def world_pos(obj):
    """Parent-chain world position, honouring yaw at each level."""
    x, y, z = obj.location
    p = obj.parent
    while p is not None:
        yaw = p.rotation_euler[2] if p.rotation_euler else 0.0
        c, s = math.cos(yaw), math.sin(yaw)
        x, y = p.location[0] + x * c - y * s, p.location[1] + x * s + y * c
        z += p.location[2]
        p = p.parent
    return (x, y, z)


def look_at_rot(cam_pos, target):
    """Blender convention: camera looks along local -Z; pitch 90deg = horizontal,
    smaller pitch tilts down, larger tilts up (scene builders use ~(85deg,0,yaw))."""
    dx, dy, dz = target[0] - cam_pos[0], target[1] - cam_pos[1], target[2] - cam_pos[2]
    horiz = math.hypot(dx, dy)
    pitch = math.atan2(horiz, -dz)
    yaw = math.atan2(-dx, dy)
    return (pitch, 0.0, yaw)


def forward_vec(rot):
    pitch, _, yaw = rot
    return (-math.sin(yaw) * math.sin(pitch) * -1 - 0, 0, 0)  # placeholder, replaced below


def forward(rot):
    """World forward (view) direction for rotation_euler (pitch, 0, yaw)."""
    pitch, _, yaw = rot
    # local -Z -> world: Rx(p)*(0,0,-1) = (0, sin p, -cos p); then Rz(y).
    sx, cx = math.sin(pitch), math.cos(pitch)
    sy, cy = math.sin(yaw), math.cos(yaw)
    return (-sy * sx, cy * sx, -cx)


def right_vec(rot):
    f = forward(rot)
    # right = forward x up (up = +Z), normalised on the ground plane
    rx, ry = f[1], -f[0]
    n = math.hypot(rx, ry) or 1.0
    return (rx / n, ry / n, 0.0)


def offset_dir(az_deg):
    """az=0 -> camera sits -Y of subject (default); 90 -> +X; 180 -> +Y (reverse)."""
    a = RAD(az_deg)
    return (math.sin(a), -math.cos(a), 0.0)


def place(cam, loc, target, lens, fstop=5.6, focus=None):
    cam.location = loc
    cam.rotation_euler = look_at_rot(loc, target)
    cam.data.lens = lens
    cam.data.dof.use_dof = True
    cam.data.dof.aperture.fstop = fstop
    d = focus if focus is not None else math.dist(loc, target)
    cam.data.dof.focus_distance = d
    return d


# ---------------------------------------------------------------------- #
# motivated moves. every function returns (key_count, path_positions)
# and keys ONLY inside [f0, f1].
# ---------------------------------------------------------------------- #
def _kf_loc(cam, frame, loc):
    cam.location = loc
    cam.keyframe_insert("location", frame=frame)
    return 1


def _kf_rot(cam, frame, rot):
    cam.rotation_euler = rot
    cam.keyframe_insert("rotation_euler", frame=frame)
    return 1


def _kf_focus(cam, frame, d):
    cam.data.dof.focus_distance = d
    cam.data.dof.keyframe_insert("focus_distance", frame=frame)
    return 1


def _ease(cam):
    ad = cam.animation_data
    if ad:
        for fc in ad.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"


def hold(cam, f0, f1):
    n = _kf_loc(cam, f0, cam.location) + _kf_loc(cam, f1, cam.location)
    n += _kf_rot(cam, f0, cam.rotation_euler) + _kf_rot(cam, f1, cam.rotation_euler)
    _ease(cam)
    return n, [tuple(cam.location)]


def push_in(cam, f0, f1, target, d0, d1, height=None):
    """Slow motivated push along the view axis. height overrides cam z at the end."""
    gx, gy = target[0] - cam.location[0], target[1] - cam.location[1]
    gn = math.hypot(gx, gy) or 1.0
    dirx, diry = gx / gn, gy / gn  # ground-plane direction cam -> target
    n, path = 0, []
    for f, d in ((f0, d0), (f1, d1)):
        z = cam.location[2] if height is None else height
        loc = (target[0] - dirx * d, target[1] - diry * d, z)
        n += _kf_loc(cam, f, loc)
        n += _kf_rot(cam, f, look_at_rot(loc, target))
        path.append(loc)
    _ease(cam)
    return n, path


def crane_back_up(cam, f0, f1, target, d0, d1, z0, z1):
    """Continuous back-and-up crane (the SC01_SH004 reveal)."""
    gx, gy = target[0] - cam.location[0], target[1] - cam.location[1]
    gn = math.hypot(gx, gy) or 1.0
    dirx, diry = gx / gn, gy / gn
    n, path = 0, []
    steps = 6
    for i in range(steps + 1):
        t = i / steps
        e = t * t * (3 - 2 * t)  # smoothstep spacing
        d, z = d0 + (d1 - d0) * e, z0 + (z1 - z0) * e
        f = int(round(f0 + (f1 - f0) * t))
        loc = (target[0] - dirx * d, target[1] - diry * d, z)
        n += _kf_loc(cam, f, loc)
        n += _kf_rot(cam, f, look_at_rot(loc, target))
        path.append(loc)
    _ease(cam)
    return n, path


def dolly_lateral(cam, f0, f1, delta, target0=None, target1=None):
    """Lateral dolly / tracking move in world XY. When targets are given the
    camera re-aims each end so a walking subject stays centred (parallel track)."""
    x, y, z = cam.location
    end = (x + delta[0], y + delta[1], z)
    n = _kf_loc(cam, f0, (x, y, z)) + _kf_loc(cam, f1, end)
    if target0 is not None and target1 is not None:
        n += _kf_rot(cam, f0, look_at_rot((x, y, z), target0))
        n += _kf_rot(cam, f1, look_at_rot(end, target1))
    else:
        _kf_rot(cam, f0, cam.rotation_euler) + _kf_rot(cam, f1, cam.rotation_euler)
    _ease(cam)
    return n, [(x, y, z), end]


def crane_rise(cam, f0, f1, dz, follow_rot_target=None):
    """Vertical track matched to a climb."""
    x, y, z = cam.location
    n, path = 0, []
    for f, zz in ((f0, z), (f1, z + dz)):
        loc = (x, y, zz)
        n += _kf_loc(cam, f, loc)
        n += _kf_rot(cam, f, look_at_rot(loc, follow_rot_target) if follow_rot_target else cam.rotation_euler)
        path.append(loc)
    _ease(cam)
    return n, path


def descend_with(cam, f0, f1, z_end, target):
    """Goes under with her (SC04_SH004)."""
    x, y, _ = cam.location
    n, path = 0, []
    for f, z in ((f0, cam.location[2]), (f1, z_end)):
        loc = (x, y, z)
        n += _kf_loc(cam, f, loc)
        n += _kf_rot(cam, f, look_at_rot(loc, target))
        path.append(loc)
    _ease(cam)
    return n, path


def tilt(cam, f0, f1, pitch0, pitch1, at=1.0):
    """Pitch move: tilt up the stair / follow the stair section down.
    at<1.0 -> the tilt completes at that fraction, then holds."""
    yw = cam.rotation_euler[2]
    fm = int(round(f0 + (f1 - f0) * at))
    n = _kf_rot(cam, f0, (pitch0, 0, yw))
    n += _kf_rot(cam, fm, (pitch1, 0, yw))
    if fm < f1:
        n += _kf_rot(cam, f1, (pitch1, 0, yw))
    n += _kf_loc(cam, f0, cam.location) + _kf_loc(cam, f1, cam.location)
    _ease(cam)
    return n, [tuple(cam.location)]


def pan_hold(cam, f0, f1, target_a, target_b, move_t0=0.0, move_t1=0.5):
    """Follows something out of frame, then holds (SC05_SH003)."""
    fm = int(round(f0 + (f1 - f0) * move_t0))
    fe = int(round(f0 + (f1 - f0) * move_t1))
    n = _kf_rot(cam, f0, look_at_rot(cam.location, target_a))
    n += _kf_rot(cam, fm, look_at_rot(cam.location, target_a))
    n += _kf_rot(cam, fe, look_at_rot(cam.location, target_b))
    n += _kf_rot(cam, f1, look_at_rot(cam.location, target_b))
    n += _kf_loc(cam, f0, cam.location) + _kf_loc(cam, f1, cam.location)
    _ease(cam)
    return n, [tuple(cam.location)]


def whip_to(cam, f0, f1, target, at=0.55, frames=6):
    """THE single fast move of the film (SC06_SH002). Deliberate, not noise."""
    f_start = int(round(f0 + (f1 - f0) * at))
    f_end = min(f1, f_start + frames)
    n = _kf_rot(cam, f0, cam.rotation_euler) + _kf_rot(cam, f_start, cam.rotation_euler)
    n += _kf_rot(cam, f_end, look_at_rot(cam.location, target))
    n += _kf_rot(cam, f1, look_at_rot(cam.location, target))
    n += _kf_loc(cam, f0, cam.location) + _kf_loc(cam, f1, cam.location)
    ad = cam.animation_data
    for fc in ad.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
    return n, [tuple(cam.location)]


def cut_to(cam, f0, f1, loc_b, target_b, at=0.5):
    """In-shot hard cut: POV then reverse (SC06_SH005). CONSTANT keyframes."""
    fm = int(round(f0 + (f1 - f0) * at))
    loc_a, rot_a = tuple(cam.location), cam.rotation_euler
    n = _kf_loc(cam, f0, loc_a) + _kf_rot(cam, f0, rot_a)
    n += _kf_loc(cam, fm, loc_a) + _kf_rot(cam, fm, rot_a)
    n += _kf_loc(cam, fm + 1, loc_b) + _kf_rot(cam, fm + 1, look_at_rot(loc_b, target_b))
    n += _kf_loc(cam, f1, loc_b) + _kf_rot(cam, f1, look_at_rot(loc_b, target_b))
    ad = cam.animation_data
    for fc in ad.action.fcurves:
        for kp in fc.keyframe_points:
            fr_ = int(round(kp.co[0]))
            kp.interpolation = "CONSTANT" if fr_ <= fm else "BEZIER"
    return n, [loc_a, loc_b]


def micro_drift(cam, f0, f1, amp=0.008, axis=1):
    """Motivated 'handheld' beat: ONE slow drift across the whole shot, no noise."""
    x, y, z = cam.location
    d = [0.0, 0.0, 0.0]
    d[axis] = amp
    n = _kf_loc(cam, f0, (x, y, z)) + _kf_loc(cam, f1, (x + d[0], y + d[1], z + d[2]))
    n += _kf_rot(cam, f0, cam.rotation_euler) + _kf_rot(cam, f1, cam.rotation_euler)
    _ease(cam)
    return n, [(x, y, z), (x + d[0], y + d[1], z + d[2])]


def rack_focus(cam, f0, f1, d0, d1, at0=0.15, at1=0.6):
    """Focus pull, camera body locked (SC05_SH007 gauge->door)."""
    fa = int(round(f0 + (f1 - f0) * at0))
    fb = int(round(f0 + (f1 - f0) * at1))
    n = _kf_focus(cam, f0, d0) + _kf_focus(cam, fa, d0)
    n += _kf_focus(cam, fb, d1) + _kf_focus(cam, f1, d1)
    n += _kf_loc(cam, f0, cam.location) + _kf_loc(cam, f1, cam.location)
    n += _kf_rot(cam, f0, cam.rotation_euler) + _kf_rot(cam, f1, cam.rotation_euler)
    _ease(cam)
    return n, [tuple(cam.location)]
