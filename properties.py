# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

#
# Custom Property Groups
#


class PreflightMeshGroup(bpy.types.PropertyGroup):
    """Property group of mesh names."""

    obj_pointer: bpy.props.PointerProperty(
        name="Object Pointer",
        type=bpy.types.Object,
        description="Object to Export")

    obj_name: bpy.props.StringProperty(
        name="Object Name",
        description="Name of the object to export. Note: If the object name changes, the reference will be lost.",
        default="")


class PreflightExportGroup(bpy.types.PropertyGroup):
    """Property group of export options."""

    is_collapsed: bpy.props.BoolProperty(
        name="Collapse Group",
        description="Collapse the display of this export group.",
        default=False)
    name: bpy.props.StringProperty(
        name="Export Group Name",
        description="File name for this export group. Will be converted to camel case. Duplicate names will cause an error.",
        default="")
    include_animations: bpy.props.BoolProperty(
        name="Include Animations",
        description="Include animations along with the armatures in this export group.",
        default=False)
    apply_modifiers: bpy.props.BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers while performing this export.",
        default=True)
    obj_names: bpy.props.CollectionProperty(type=PreflightMeshGroup)
    obj_idx: bpy.props.IntProperty(name="Object Index", default=0)

    export_location: bpy.props.StringProperty(
        name="Export To",
        description="Choose an export location. Relative to the base export location set in the Export Options.",
        default="",
        maxlen=1024)


class PreflightExportOptionsGroup(bpy.types.PropertyGroup):
    allowed_keys = [
        "bake_space_transform",
        "use_selection",
        "object_types",
        "add_leaf_bones",
        "primary_bone_axis",
        "secondary_bone_axis",
        "use_armature_deform_only",
        "bake_anim",
        "use_mesh_modifiers"
    ]

    axis_enum = [
        ('X', 'X Axis', ''),
        ('Y', 'Y Axis', ''),
        ('Z', 'Z Axis', ''),
        ('-X', '-X Axis', ''),
        ('-Y', '-Y Axis', ''),
        ('-Z', '-Z Axis', ''),
    ]

    object_types_enum = [
        ('MESH', "Meshes", "Export Meshes"),
        ('ARMATURE', "Armatures", "Export Armatures"),
        ('EMPTY', "Empty", ""),
        ('OTHER', "Other", "Other geometry types, like curve, metaball, etc. (converted to meshes)")
    ]

    def as_dict(self):
        return {key: getattr(self, key) for key in dict(self).keys()}

    def reset(self, options):
        for key, value in options:
            if hasattr(self, key):
                setattr(self, key, value)

    def defaults_for_unity(self, **overrides):
        defaults = dict(
            bake_space_transform=True,
            use_selection=True,
            object_types={'MESH', 'ARMATURE', 'EMPTY', 'OTHER'},
            add_leaf_bones=False,
            primary_bone_axis='X',
            secondary_bone_axis='Y',
            use_armature_deform_only=True
        )

        return {**defaults, **overrides}

    def get_options_dict(self, **overrides):
        """return all options, filtered to valid selections"""
        opts = {**self.defaults_for_unity(), **self.as_dict(), **overrides}
        return dict((k, opts[k]) for k in self.allowed_keys if k in opts)

    # Axis Properties
    object_types: bpy.props.EnumProperty(name="Object Types", items=object_types_enum, default={
                                          'ARMATURE', 'MESH', 'EMPTY', 'OTHER'}, options={'ENUM_FLAG'})
    axis_up: bpy.props.EnumProperty(name="Up", items=axis_enum, default="Y")
    axis_forward: bpy.props.EnumProperty(
        name="Forward", items=axis_enum, default="-Z")
    use_anim: bpy.props.BoolProperty(name="Use Animations", default=True)

    separate_animations: bpy.props.BoolProperty(
        name="Export Animations to Separate File",
        description="Include all animations in a separate animations file.",
        default=True)

    export_location: bpy.props.StringProperty(
        name="Export To",
        description="Choose an export location. Relative location prefixed with '//'.",
        default="//",
        maxlen=1024,
        subtype='DIR_PATH')


class PreflightOptionsGroup(bpy.types.PropertyGroup):
    """Parent property group for preflight."""

    export_options: bpy.props.PointerProperty(
        type=PreflightExportOptionsGroup)
    fbx_export_groups: bpy.props.CollectionProperty(type=PreflightExportGroup)
