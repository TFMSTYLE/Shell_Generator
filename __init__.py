# SPDX-FileCopyrightText: 2025-2026 The French Monkey
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "Shell",
    "author": "The French Monkey",
    "version": (1, 0, 1),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Shell",
    "description": "Generate parametric shell",
    "category": "Add Mesh",
    "license": "GPL-3.0-or-later",
}

import bpy, bmesh, math
from math import sin, cos, exp, tau
from mathutils import Vector, Matrix

# ------------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------------

def get_or_make_material(name, color):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs[0].default_value = (*color, 1.0)
    return mat

def assign_shell_material(obj):
    mat = get_or_make_material("Shell_Material", (0.95, 0.85, 0.7))
    obj.data.materials.clear()
    obj.data.materials.append(mat)

# ------------------------------------------------------------------------
# Core geometry
# ------------------------------------------------------------------------

def _center_and_frame(theta, base_radius, a_growth, b_vertical):
    r = base_radius * exp(a_growth * theta)
    dr = a_growth * r
    z = b_vertical * theta
    c = Vector((r * cos(theta), r * sin(theta), z))
    dc = Vector((dr*cos(theta) - r*sin(theta), dr*sin(theta) + r*cos(theta), b_vertical))
    T = dc.normalized() if dc.length_squared > 1e-20 else Vector((1, 0, 0))
    R = Vector((cos(theta), sin(theta), 0))
    B = T.cross(R)
    if B.length_squared < 1e-20: B = T.cross(Vector((0, 0, 1)))
    if B.length_squared < 1e-20: B = Vector((0, 1, 0))
    B.normalize()
    N = B.cross(T)
    if N.length_squared < 1e-20: N = R
    else: N.normalize()
    return c, T, N, B

def _rotate_in_plane(N, B, phi):
    c, s = cos(phi), sin(phi)
    return N*c + B*s, -N*s + B*c

def build_shell_mesh(props):
    bm = bmesh.new()
    turns = max(1, int(props.turns))
    steps = max(24, int(props.steps_per_turn))
    base_r, a, b = props.base_radius, props.radial_growth, props.vertical_growth
    aper_a, aper_b, flare = props.aperture_a, props.aperture_b, props.flare
    twist_deg, segs = props.twist_per_turn, max(8, int(props.aperture_segments))
    rib_amp, rib_freq = props.rib_amplitude, props.rib_frequency

    total = turns * steps
    dθ = (turns * tau) / total
    twist_r = math.radians(twist_deg) / tau
    rings = []

    for i in range(total + 1):
        θ = i * dθ
        C, T, N, B = _center_and_frame(θ, base_r, a, b)
        φ = twist_r * θ
        Np, Bp = _rotate_in_plane(N, B, φ)
        g = exp(a * θ)
        Aa, Bb = aper_a * g * flare, aper_b * g
        if rib_amp and rib_freq:
            mod = 1 + rib_amp * sin(rib_freq * θ * 2)
            Aa *= mod; Bb *= mod
        ring = [bm.verts.new(C + Np*(Aa*cos(u)) + Bp*(Bb*sin(u))) for u in [(j/segs)*tau for j in range(segs)]]
        rings.append(ring)

    for i in range(len(rings)-1):
        r0, r1 = rings[i], rings[i+1]
        for j in range(segs):
            try: bm.faces.new((r0[j], r0[(j+1)%segs], r1[(j+1)%segs], r1[j]))
            except: pass

    mesh = bpy.data.meshes.new("ShellMesh")
    bm.to_mesh(mesh); bm.free(); mesh.update()
    return mesh

# ------------------------------------------------------------------------
# Finalize
# ------------------------------------------------------------------------

def finalize_shell(obj, props):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    if props.smooth_shading:
        bpy.ops.object.shade_smooth()

    normals = getattr(obj.data, "normals", None)
    if normals:
        normals.use_auto_smooth = True
        normals.auto_smooth_angle = math.radians(60)

    assign_shell_material(obj)
    obj.name = "Shell"
    return obj

# ------------------------------------------------------------------------
# Rebuild / Generate
# ------------------------------------------------------------------------

def rebuild_shell(obj, props):
    mesh = build_shell_mesh(props)
    old = obj.data
    obj.data = mesh
    if old and old.users == 0:
        bpy.data.meshes.remove(old)
    finalize_shell(obj, props)
    return obj

def generate_shell(context):
    p = context.scene.shellgen_props
    obj = context.active_object
    keys = (
        "turns", "steps_per_turn",
        "base_radius", "radial_growth", "vertical_growth",
        "aperture_a", "aperture_b", "flare",
        "twist_per_turn", "aperture_segments",
        "rib_amplitude", "rib_frequency",
        "smooth_shading"
    )

    if obj and obj.type == "MESH" and obj.get("shell_generator") and obj.select_get():
        for k in keys:
            if hasattr(p, k):
                obj[k] = getattr(p, k)
        rebuild_shell(obj, p)
        return obj

    mesh = build_shell_mesh(p)
    new_obj = bpy.data.objects.new("Shell", mesh)
    context.collection.objects.link(new_obj)
    context.view_layer.objects.active = new_obj
    new_obj.select_set(True)
    new_obj["shell_generator"] = True
    finalize_shell(new_obj, p)
    return new_obj

# ------------------------------------------------------------------------
# Live Update
# ------------------------------------------------------------------------

def update_shell(self, context):
    if not self.live_update:
        return

    obj = context.active_object

    if not obj or obj.type != "MESH" or "shell_generator" not in obj or not obj.select_get():
        return

    rebuild_shell(obj, self)

# ------------------------------------------------------------------------
# Properties
# ------------------------------------------------------------------------

class ShellGenProperties(bpy.types.PropertyGroup):
    live_update: bpy.props.BoolProperty(name="Live Update", default=False)

    # Sweep controls
    turns: bpy.props.IntProperty(name="Turns", default=5, min=1, max=50, subtype='FACTOR', update=update_shell)
    steps_per_turn: bpy.props.IntProperty(name="Steps per Turn", default=96, min=16, max=1024, subtype='FACTOR', update=update_shell)

    # Raup parameters
    base_radius: bpy.props.FloatProperty(name="Base Radius r₀", default=0.2, min=0.001, max=10.0, subtype='FACTOR', update=update_shell)
    radial_growth: bpy.props.FloatProperty(name="Radial Growth a", default=0.06, min=0.0, max=0.3, subtype='FACTOR', description="Exponential growth factor in radius per radian", update=update_shell)
    vertical_growth: bpy.props.FloatProperty(name="Vertical Rate b", default=0.02, min=0.0, max=0.2, subtype='FACTOR', description="Axial rise per radian", update=update_shell)

    # Aperture shape 
    aperture_a: bpy.props.FloatProperty(name="Aperture A (N-axis)", default=0.10, min=0.001, max=5.0, subtype='FACTOR', update=update_shell)
    aperture_b: bpy.props.FloatProperty(name="Aperture B (B-axis)", default=0.06, min=0.001, max=5.0, subtype='FACTOR', update=update_shell)
    flare: bpy.props.FloatProperty(name="Flare (elongate A)", default=1.4, min=0.5, max=3.0, subtype='FACTOR', description="Elongation along the local N-axis", update=update_shell)
    twist_per_turn: bpy.props.FloatProperty(name="Aperture Twist (°/turn)", default=12.0, min=0.0, max=90.0, subtype='FACTOR', update=update_shell)
    aperture_segments: bpy.props.IntProperty(name="Aperture Segments", default=24, min=8, max=128, subtype='FACTOR', update=update_shell)

    # Ornamentation
    rib_amplitude: bpy.props.FloatProperty(name="Rib Amplitude", default=0.10, min=0.0, max=1.0, subtype='FACTOR', update=update_shell)
    rib_frequency: bpy.props.FloatProperty(name="Rib Frequency (per turn)", default=6.0, min=0.0, max=64.0, subtype='FACTOR', update=update_shell)

    # Shading
    smooth_shading: bpy.props.BoolProperty(name="Smooth Shading", default=True, update=update_shell)
    
# ------------------------------------------------------------------------
# Operators
# ------------------------------------------------------------------------

class SHELLGEN_OT_generate(bpy.types.Operator):
    bl_idname = "shell.generate"
    bl_label = "Generate Shell"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        generate_shell(context)
        return {"FINISHED"}
    
class SHELLGEN_OT_reset(bpy.types.Operator):
    bl_idname = "shell.reset"
    bl_label = "Reset Settings"
    bl_description = "Reset all shell parameters to their default values"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.shellgen_props
        live_state = props.live_update 

        for prop_name, prop in ShellGenProperties.bl_rna.properties.items():
            if prop.is_readonly or prop.identifier == "rna_type":
                continue
            if prop.identifier == "live_update":
                continue
            try:
                setattr(props, prop.identifier, prop.default)
            except Exception:
                pass

        props.live_update = live_state

        if live_state:
            update_shell(props, context)

        self.report({'INFO'}, "Shell settings reset to defaults")
        return {'FINISHED'}
    
# ------------------------------------------------------------------------
# UI
# ------------------------------------------------------------------------

class VIEW3D_PT_shell_generator(bpy.types.Panel):
    bl_label = "Shell"
    bl_idname = "VIEW3D_PT_shell_generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shell"

    def draw(self, context):
        layout = self.layout
        p = context.scene.shellgen_props
        o = context.object

        layout.operator("shell.generate", text="Generate Shell", icon="FORCE_VORTEX")

        row = layout.row(align=True)
        row.prop(p, "live_update", toggle=True)
        row.operator("shell.reset", text="Reset")

        layout.separator(factor=0.5)

        layout.prop(p, "turns")
        layout.prop(p, "steps_per_turn")

        layout.prop(p, "base_radius")
        layout.prop(p, "radial_growth")
        layout.prop(p, "vertical_growth")

        layout.separator(factor=0.5)

        layout.prop(p, "aperture_a")
        layout.prop(p, "aperture_b")
        layout.prop(p, "flare")
        layout.prop(p, "twist_per_turn")
        layout.prop(p, "aperture_segments")

        layout.separator(factor=0.5)

        layout.prop(p, "rib_amplitude")
        layout.prop(p, "rib_frequency")

        layout.prop(p, "smooth_shading", toggle=True)

        layout.separator(factor=0.5)

        if o and o.type == "MESH" and "shell_generator" in o and o.select_get():
            layout.label(text=f"Editing: {o.name}", icon="FORCE_VORTEX")
        else:
            layout.label(text="No generated shell selected", icon="INFO")

# ------------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------------

classes = (
    ShellGenProperties,
    SHELLGEN_OT_generate,
    SHELLGEN_OT_reset,
    VIEW3D_PT_shell_generator,  
)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.shellgen_props = bpy.props.PointerProperty(type=ShellGenProperties)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.shellgen_props

if __name__ == "__main__":
    register()
