"""
Procedural material builders for NINETY-TWO TURNS.

Every material is authored as a node graph (Principled BSDF + optional
noise/bump or emission) so it reconstructs identically on any Blender version
and on the cloud render layer. Runs under real Blender and under the stub.

Material ids are referenced from ASSET_MANIFEST.json and the asset builders.
"""

import os

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
TEXTURES = os.path.abspath(os.path.join(HERE, "..", "textures"))


def _new_mat(mid):
    mat = bpy.data.materials.get(mid)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(mid)
    mat.use_nodes = True
    return mat


def _bsdf_out(mat):
    """Reuse the default Principled/Output pair when present (real Blender
    creates them on use_nodes=True); create them under the stub."""
    nt = mat.node_tree
    bsdf = out = None
    for n in list(nt.nodes):
        t = str(getattr(n, "type", ""))
        if t in ("BSDF_PRINCIPLED", "ShaderNodeBsdfPrincipled") and bsdf is None:
            bsdf = n
        elif t in ("OUTPUT_MATERIAL", "ShaderNodeOutputMaterial") and out is None:
            out = n
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    if out is None:
        out = nt.nodes.new("ShaderNodeOutputMaterial")
    linked = False
    for l in list(getattr(nt.links, "_links", [])) if hasattr(nt.links, "_links") else []:
        linked = linked or (l[0] is bsdf and l[1] is out)
    if not linked:
        try:
            nt.links.new(bsdf.outputs[0], out.inputs[0])
        except Exception:
            pass  # already linked in real Blender default tree
    return bsdf


def _blend(mat):
    """Transparent blend, Blender-version safe (4.2 renamed the enum)."""
    if hasattr(mat, "surface_blend_method"):
        mat.surface_blend_method = "ALPHA_BLEND"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND"


def _set(bsdf, names, value):
    for n in names:
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = value
            return


def _noise_bump(mat, bsdf, scale=18.0, strength=0.25):
    nt = mat.node_tree
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    nt.links.new(noise.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs[0], bsdf.inputs["Normal"])


def build_brass_aged():
    m = _new_mat("MAT_BRASS_AGED")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.38, 0.26, 0.10, 1))
    _set(b, ["Metallic"], 1.0)
    _set(b, ["Roughness"], 0.45)
    _noise_bump(m, b, 22.0, 0.2)
    return m


def build_brass_polished():
    m = _new_mat("MAT_BRASS_POLISHED")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.55, 0.40, 0.16, 1))
    _set(b, ["Metallic"], 1.0)
    _set(b, ["Roughness"], 0.18)
    return m


def build_iron_rusted():
    m = _new_mat("MAT_IRON_RUSTED")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.08, 0.07, 0.06, 1))
    _set(b, ["Metallic"], 0.7)
    _set(b, ["Roughness"], 0.7)
    _noise_bump(m, b, 30.0, 0.35)
    return m


def build_glass_drum():
    m = _new_mat("MAT_GLASS_DRUM")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.9, 0.95, 0.95, 1))
    _set(b, ["Roughness"], 0.05)
    _set(b, ["Transmission Weight", "Transmission"], 1.0)
    _set(b, ["Alpha"], 0.25)
    return m


def build_water_dark():
    m = _new_mat("MAT_WATER_DARK")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.015, 0.045, 0.055, 1))
    _set(b, ["Roughness"], 0.08)
    _noise_bump(m, b, 60.0, 0.08)
    return m


def build_stone_barnacle():
    m = _new_mat("MAT_STONE_BARNACLE")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.22, 0.23, 0.21, 1))
    _set(b, ["Roughness"], 0.9)
    _noise_bump(m, b, 40.0, 0.5)
    return m


def build_wood_rotted():
    m = _new_mat("MAT_WOOD_ROTTED")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.16, 0.10, 0.06, 1))
    _set(b, ["Roughness"], 0.85)
    _noise_bump(m, b, 25.0, 0.3)
    return m


def build_rope_hemp():
    m = _new_mat("MAT_ROPE_HEMP")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.35, 0.27, 0.16, 1))
    _set(b, ["Roughness"], 0.95)
    return m


def build_cloth_coat():
    m = _new_mat("MAT_CLOTH_COAT")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.13, 0.16, 0.20, 1))
    _set(b, ["Roughness"], 1.0)
    return m


def build_skin_child():
    m = _new_mat("MAT_SKIN_CHILD")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.55, 0.38, 0.28, 1))
    _set(b, ["Roughness"], 0.6)
    return m


def _emission(mid, color, strength):
    m = _new_mat(mid)
    nt = m.node_tree
    em = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def build_amber_glow():
    return _emission("MAT_AMBER_GLOW", (1.0, 0.55, 0.15), 30.0)


def build_spark_glow():
    return _emission("MAT_SPARK_GLOW", (1.0, 0.62, 0.18), 60.0)


def build_whitegold():
    return _emission("MAT_WHITEGOLD", (1.0, 0.85, 0.55), 200.0)


def build_eye_shutter():
    m = _new_mat("MAT_EYE_SHUTTER")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.45, 0.32, 0.13, 1))
    _set(b, ["Metallic"], 1.0)
    _set(b, ["Roughness"], 0.3)
    return m


def build_gauge_dial():
    m = _new_mat("MAT_GAUGE_DIAL")
    nt = m.node_tree
    b = _bsdf_out(m)
    # from_pydata meshes carry no UVs; use generated (bounding-box) coordinates
    # so the dial samples correctly on the flat disc without a UV layer.
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(TEXTURES, "gauge_dial.png"))
    nt.links.new(tc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    _set(b, ["Roughness"], 0.4)
    _set(b, ["Metallic"], 0.0)
    return m


def build_rain_streak():
    m = _new_mat("MAT_RAIN_STREAK")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.72, 0.80, 0.88, 1))
    _set(b, ["Roughness"], 0.08)
    _set(b, ["Metallic"], 0.0)
    _set(b, ["Alpha"], 0.35)
    _blend(m)
    return m


def build_fog_bank():
    m = _new_mat("MAT_FOG_BANK")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (0.55, 0.60, 0.66, 1))
    _set(b, ["Roughness"], 1.0)
    _set(b, ["Alpha"], 0.07)
    _blend(m)
    return m


def build_dust_mote():
    m = _new_mat("MAT_DUST_MOTE")
    b = _bsdf_out(m)
    _set(b, ["Base Color"], (1.0, 0.85, 0.62, 1))
    _set(b, ["Roughness"], 0.9)
    _set(b, ["Alpha"], 0.5)
    _set(b, ["Emission Color"], (1.0, 0.8, 0.5, 1))
    _set(b, ["Emission Strength"], 0.4)
    _blend(m)
    return m


MATERIALS = [
    ("MAT_BRASS_AGED", "build_brass_aged", []),
    ("MAT_BRASS_POLISHED", "build_brass_polished", []),
    ("MAT_IRON_RUSTED", "build_iron_rusted", []),
    ("MAT_GLASS_DRUM", "build_glass_drum", []),
    ("MAT_WATER_DARK", "build_water_dark", []),
    ("MAT_STONE_BARNACLE", "build_stone_barnacle", []),
    ("MAT_WOOD_ROTTED", "build_wood_rotted", []),
    ("MAT_ROPE_HEMP", "build_rope_hemp", []),
    ("MAT_CLOTH_COAT", "build_cloth_coat", []),
    ("MAT_SKIN_CHILD", "build_skin_child", []),
    ("MAT_AMBER_GLOW", "build_amber_glow", []),
    ("MAT_SPARK_GLOW", "build_spark_glow", []),
    ("MAT_WHITEGOLD", "build_whitegold", []),
    ("MAT_EYE_SHUTTER", "build_eye_shutter", []),
    ("MAT_GAUGE_DIAL", "build_gauge_dial", ["TEX_GAUGE_DIAL"]),
    ("MAT_RAIN_STREAK", "build_rain_streak", []),
    ("MAT_FOG_BANK", "build_fog_bank", []),
    ("MAT_DUST_MOTE", "build_dust_mote", []),
]


_BUILDERS = {
    "MAT_BRASS_AGED": build_brass_aged,
    "MAT_BRASS_POLISHED": build_brass_polished,
    "MAT_IRON_RUSTED": build_iron_rusted,
    "MAT_GLASS_DRUM": build_glass_drum,
    "MAT_WATER_DARK": build_water_dark,
    "MAT_STONE_BARNACLE": build_stone_barnacle,
    "MAT_WOOD_ROTTED": build_wood_rotted,
    "MAT_ROPE_HEMP": build_rope_hemp,
    "MAT_CLOTH_COAT": build_cloth_coat,
    "MAT_SKIN_CHILD": build_skin_child,
    "MAT_AMBER_GLOW": build_amber_glow,
    "MAT_SPARK_GLOW": build_spark_glow,
    "MAT_WHITEGOLD": build_whitegold,
    "MAT_EYE_SHUTTER": build_eye_shutter,
    "MAT_GAUGE_DIAL": build_gauge_dial,
    "MAT_RAIN_STREAK": build_rain_streak,
    "MAT_FOG_BANK": build_fog_bank,
    "MAT_DUST_MOTE": build_dust_mote,
}


def build_all():
    return {mid: fn() for mid, fn in _BUILDERS.items()}
