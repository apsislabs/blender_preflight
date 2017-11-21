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
import os

LARGE_BUTTON_SCALE_Y = 1.5


class PreflightPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Pre-Flight FBX"
    bl_context = "objectmode"
    bl_category = "Pre-Flight FBX"

    def draw(self, context):
        layout = self.layout
        groups = context.scene.preflight_props.fbx_export_groups

        # Export Groups
        layout.operator("preflight.add_export_group",
                        text="Add Export Group", icon="ZOOMIN")
        for group_idx, group in enumerate(groups):
            self.layout_export_group(group_idx, group, layout, context)

        layout.separator()

        layout.prop(context.scene.preflight_props, "export_location",
                    icon="LIBRARY_DATA_DIRECT", text="")
        layout.prop(context.scene.preflight_props, "export_animations")

        layout.separator()

        # Export Button
        export_row = layout.row()
        export_row.scale_y = LARGE_BUTTON_SCALE_Y
        exportButton = export_row.operator(
            "preflight.export_groups",
            icon="EXPORT")

    def layout_export_group(self, group_idx, group, layout, context):
        group_box = layout.box()

        # Header Row
        row = group_box.row()

        row.prop(
            group,
            "is_collapsed",
            icon="TRIA_RIGHT" if group.is_collapsed else "TRIA_DOWN",
            icon_only=True,
            emboss=False
        )

        row.prop(group, "name", text="")

        remove_group_button = row.operator(
            "preflight.remove_export_group",
            text="",
            icon="X"
        )

        remove_group_button.group_idx = group_idx

        if group.is_collapsed is False:
            # Mesh Collection
            group_box.label("Objects to Export:",
                            icon="OUTLINER_OB_GROUP_INSTANCE")
            mesh_column = group_box.column(align=True)
            for mesh_idx, mesh in enumerate(group.obj_names):
                self.layout_mesh_row(mesh_idx, group_idx,
                                     mesh, mesh_column, context)

            # Add Mesh Button
            add_mesh_button = mesh_column.operator(
                "preflight.add_object_to_group", text="Add Object", icon="ZOOMIN")
            add_mesh_button.group_idx = group_idx

            # Export Options
            group_box.separator()
            options_column = group_box.column(align=True)
            options_column.prop(group, "include_armatures")
            options_column.prop(group, "include_animations")
            options_column.prop(group, "apply_modifiers")

    def layout_mesh_row(self, mesh_idx, group_idx, mesh, layout, context):
        mesh_row = layout.row(align=True)
        mesh_row.prop_search(mesh, "obj_name", context.scene,
                             "objects", text="", icon="OBJECT_DATA")

        # Remove Mesh Button
        removeMeshButton = mesh_row.operator(
            "preflight.remove_object_from_group", text="", icon="ZOOMOUT")
        removeMeshButton.group_idx = group_idx
        removeMeshButton.object_idx = mesh_idx


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
