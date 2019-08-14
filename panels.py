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
from . import helpers

LARGE_BUTTON_SCALE_Y = 1.5


class PF_PT_preflight_panel(bpy.types.Panel):
    bl_idname = "PF_PT_preflight_panel"
    bl_label = "FBX Preflight"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        groups = context.scene.preflight_props.fbx_export_groups

        # Export Groups
        if len(groups) == 0:
            nothing_box = layout.box()
            nothing_box.label(text="No groups to export...", icon="QUESTION")
        else:
            for group_idx, group in enumerate(groups):
                self.layout_export_group(group_idx, group, layout, context)

        layout.separator()

        # New Buttons
        new_row = layout.row(align=True)
        new_row.scale_y = LARGE_BUTTON_SCALE_Y
        new_button = new_row.operator(
            "preflight.add_export_group", icon="ADD")
        create_button = new_row.operator(
            "preflight.create_group_from_selection")

        # Export Button
        export_row = layout.row()
        export_row.scale_y = LARGE_BUTTON_SCALE_Y

        export_button = export_row.operator(
            "preflight.export_all_groups",
            icon="EXPORT")

    def layout_export_group(self, group_idx, group, layout, context):
        group_box = layout.box()

        # Header Row
        self.layout_header(group_box, group, group_idx)

        if group.is_collapsed is False:
            # Mesh Collection
            self.layout_object_list(group_box, group, group_idx)

            if group.obj_idx is not None and len(
                    group.obj_names) > group.obj_idx:
                selected_obj = group.obj_names[group.obj_idx]
                group_box.prop_search(
                    selected_obj,
                    "obj_pointer",
                    context.scene,
                    "objects",
                    text="")

            # Export Options
            group_box.separator()
            options_column = group_box.column()
            options_column.label(text="Export Location (optional)",
                                 icon="LIBRARY_DATA_DIRECT")
            options_column.prop(group, "export_location", text="")
            options_column.separator()
            options_column.prop(group, "include_animations")
            options_column.prop(group, "apply_modifiers")

    def layout_object_list(self, layout, group, group_idx):
        obj_list_row = layout.row()
        obj_list_row.template_list("PF_UL_export_object_ui_list", "obj_list", group,
                                   "obj_names", group, "obj_idx")

        obj_list_actions_col = obj_list_row.column(align=True)

        add_obj_button = obj_list_actions_col.operator(
            "preflight.add_object_to_group", text="", icon="ADD")
        add_obj_button.group_idx = group_idx

        remove_obj_button = obj_list_actions_col.operator(
            "preflight.remove_object_from_group", text="", icon="REMOVE")
        remove_obj_button.group_idx = group_idx
        remove_obj_button.object_idx = group.obj_idx

    def layout_header(self, layout, group, group_idx):
        header_row = layout.row()

        collapse_icon = "TRIA_RIGHT" if group.is_collapsed else "TRIA_DOWN"
        header_row.prop(
            group,
            "is_collapsed",
            icon=collapse_icon,
            icon_only=True,
            emboss=False)

        header_row.alert = not helpers.group_is_valid(group)
        header_row.prop(group, "name", text="")
        header_row.alert = False

        sort_column = header_row.row(align=True)
        up = sort_column.operator(
            "preflight.export_group_move_slot", icon='TRIA_UP', text="")
        up.group_idx = group_idx
        up.direction = "UP"

        down = sort_column.operator(
            "preflight.export_group_move_slot", icon='TRIA_DOWN', text="")
        down.group_idx = group_idx
        down.direction = "DOWN"

        header_row.operator(
            "preflight.export_single_group", icon="EXPORT", text="",
            emboss=False).group_idx = group_idx
        header_row.operator(
            "preflight.remove_export_group", icon="X", text="",
            emboss=False).group_idx = group_idx


class PF_PT_preflight_export_options_panel(bpy.types.Panel):
    bl_idname = "PF_PT_preflight_export_options_panel"
    bl_label = "Preflight Export Options"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "PF_PT_preflight_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        export_options = context.scene.preflight_props.export_options

        layout.label(text="Export Location", icon="LIBRARY_DATA_DIRECT")
        layout.prop(export_options, "export_location", text="")
        layout.separator()
        layout.label(text="Export Types", icon="EXPORT")
        layout.prop(export_options, "object_types")
        layout.separator()
        layout.prop(export_options, "axis_up")
        layout.prop(export_options, "axis_forward")
        layout.separator()
        layout.prop(export_options, "use_anim")
        layout.separator()
        layout.operator("preflight.reset_export_options")
