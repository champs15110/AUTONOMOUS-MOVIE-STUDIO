"""
cam_runner - executes one shot's camera direction on its built, animated scene.

Sequence per shot (independently recoverable):
  1. build the shot's scene          (ams_assets.build_scene)
  2. run the shot's animation        (shot_runner.build_shot - subjects end at
                                      their final blocking pose; camera frames
                                      the pose the shot holds on)
  3. place + key the camera from shot_cams.SHOT_CAMS via cam_lib primitives.
The scene's camera placeholder object is reused - one camera per scene.
"""

import math

import bpy

import ams_assets
import cam_lib as CL
import shot_runner
from shot_cams import SHOT_CAMS


def _top(name):
    hits = []

    def rec(c):
        for o in list(c.objects):
            if o.name == name:
                hits.append(o)
        for ch in list(c.children):
            rec(ch)
    rec(bpy.context.scene.collection)
    if not hits:
        raise KeyError(name)
    return hits[0]


def resolve_point(tok):
    """token -> world (x,y,z); tuples pass through."""
    if isinstance(tok, (tuple, list)):
        return tuple(tok)
    table = {"SOCKET": "PILLAR_socket", "BURNER": "PROP_BURNER"}
    if tok in table:
        return CL.world_pos(_top(table[tok]))
    return CL.world_pos(shot_runner.resolve(tok))


def resolve_object(tok):
    if tok in ("SOCKET", "BURNER"):
        return _top({"SOCKET": "PILLAR_socket", "BURNER": "PROP_BURNER"}[tok])
    return shot_runner.resolve(tok)


def build_shot_camera(shot_id, shot_record, with_anim=True):
    f0, f1 = int(shot_record["frame_in"]), int(shot_record["frame_out"])
    ams_assets.build_scene(shot_record["scene_id"])
    if with_anim:
        shot_runner.build_shot(shot_id, shot_record)  # subjects at final pose

    spec = SHOT_CAMS[shot_id]
    cam = bpy.context.scene.camera
    lens = float(spec["lens"])
    fstop = spec.get("fstop", 5.6)
    motion = spec.get("motion", ("hold",))

    if "loc" in spec:
        target = resolve_point(spec["target"])
        subject_pt = target
        subject_true = target
        cam_pos = tuple(spec["loc"])
    else:
        anchor = resolve_point(spec["subj"])
        aim = spec.get("aim")
        subject_pt = tuple(a + (o or 0) for a, o in zip(anchor, aim)) if aim else anchor
        subject_true = anchor
        base = anchor
        if motion[0] == "dolly":
            base = tuple(a - d for a, d in zip(anchor, (motion[1], motion[2], 0)))
        z = base[2] + spec.get("h", 0.0)
        if motion[0] == "crane_rise":
            z -= motion[1]
        d = CL.offset_dir(spec.get("az", 0))
        cam_pos = (base[0] + d[0] * spec["dist"], base[1] + d[1] * spec["dist"], z)

    dist_end = CL.place(cam, cam_pos, subject_pt, lens, fstop)

    keys, path = 0, [tuple(cam.location)]
    m = motion[0]
    if m == "hold":
        keys, path = CL.hold(cam, f0, f1)
    elif m == "push_in":
        keys, path = CL.push_in(cam, f0, f1, subject_pt, spec["dist"], motion[1])
    elif m == "crane_back_up":
        keys, path = CL.crane_back_up(cam, f0, f1, subject_pt, spec["dist"],
                                      motion[1], cam.location[2], motion[2])
    elif m == "dolly":
        delta = (motion[1], motion[2], 0)
        t_end = subject_pt
        t_start = tuple(a - d for a, d in zip(subject_pt, delta))
        keys, path = CL.dolly_lateral(cam, f0, f1, (motion[1], motion[2]),
                                      target0=t_start, target1=t_end)
    elif m == "crane_rise":
        keys, path = CL.crane_rise(cam, f0, f1, motion[1], follow_rot_target=subject_pt)
    elif m == "descend":
        keys, path = CL.descend_with(cam, f0, f1, motion[1], subject_pt)
    elif m == "tilt_to":
        p0 = cam.rotation_euler[0]
        p1 = CL.look_at_rot(cam.location, resolve_point(motion[1]))[0]
        keys, path = CL.tilt(cam, f0, f1, p0, p1, at=motion[2])
    elif m == "pan_hold":
        keys, path = CL.pan_hold(cam, f0, f1, subject_pt, resolve_point(motion[1]))
    elif m == "whip":
        keys, path = CL.whip_to(cam, f0, f1, resolve_point(motion[1]))
    elif m == "cut_to":
        keys, path = CL.cut_to(cam, f0, f1, tuple(motion[1]), resolve_point(motion[2]))
    elif m == "micro_drift":
        keys, path = CL.micro_drift(cam, f0, f1, motion[1], motion[2])
    elif m == "rack":
        d1 = math.dist(cam.location, resolve_point(motion[1]))
        keys, path = CL.rack_focus(cam, f0, f1, cam.data.dof.focus_distance, d1)
    else:
        raise KeyError(f"unknown motion {m}")

    # moves that end on a new compositional anchor re-target the subject point
    if m in ("pan_hold", "whip", "tilt_to"):
        subject_true = subject_pt = resolve_point(motion[1])
    elif m == "cut_to":
        subject_true = subject_pt = resolve_point(motion[2])

    # focus must end on the subject even when the camera moved (push/crane/dolly)
    if m != "rack":
        d_end = math.dist(cam.location, subject_pt)
        if abs(cam.data.dof.focus_distance - d_end) > 0.02:
            cam.data.dof.focus_distance = d_end
            cam.data.dof.keyframe_insert("focus_distance", frame=f1)
            keys += 1

    # measurements for QC
    cam_pos_end = tuple(cam.location)
    dist_final = math.dist(cam_pos_end, subject_pt)
    frac = spec["subj_h"] / CL.frame_height(dist_final, lens)
    return {"shot_id": shot_id, "scene_id": shot_record["scene_id"],
            "frames": [f0, f1], "lens": lens, "fstop": fstop,
            "motion": m, "keys": keys, "path": [tuple(p) for p in path],
            "cam_loc_end": cam_pos_end, "cam_rot_end": tuple(cam.rotation_euler),
            "subject_pt": subject_pt, "subject_true": subject_true,
            "dist_final": dist_final,
            "scale_frac": frac, "focus_end": cam.data.dof.focus_distance,
            "spec": {k: v for k, v in spec.items() if k != "motion"},
            "note": spec["note"]}
