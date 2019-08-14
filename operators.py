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
import re

from . import helpers
from . properties import PreflightExportGroup


class PF_OT_add_selection_to_preflight_group(bpy.types.Operator):
    bl_idname = "preflight.add_selection_to_group"
    bl_label = "Add Selection"
    bl_description = "Add Selection to an export group"

    group_idx: bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None:
            for idx, obj in enumerate(context.selected_objects):
                group_names = context.scene.preflight_props.fbx_export_groups[
                    self.group_idx].obj_names
                item = group_names.add()
                item.obj_pointer = obj

            helpers.redraw_properties()
        else:
            message = 'Group Index is not Set'
            self.report({'ERROR'}, message)
            raise ValueError(message)

        return {'FINISHED'}


class PF_OT_create_preflight_group_from_selection(bpy.types.Operator):
    bl_idname = "preflight.create_group_from_selection"
    bl_label = "Create Group from Selection..."
    bl_description = "Create an export group from the current selection."

    group_name: bpy.props.StringProperty(
        name="New Group Name",
        default="New Export Group"
    )

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)

    def draw(self, context):
        self.layout.prop(self, "group_name", text="")

    def execute(self, context):
        if self.group_name is not None:
            groups = context.scene.preflight_props.fbx_export_groups
            new_group = groups.add()
            new_group.name = self.group_name

            for idx, obj in enumerate(context.selected_objects):
                item = new_group.obj_names.add()
                item.obj_pointer = obj

            helpers.redraw_properties()
        else:
            message = 'Group Name is not Set'
            self.report({'ERROR'}, message)
            raise ValueError(message)

        return {'FINISHED'}


class PF_OT_add_preflight_object_operator(bpy.types.Operator):
    bl_idname = "preflight.add_object_to_group"
    bl_label = "Add Object"
    bl_description = "Add an object to this export group."

    group_idx: bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None:
            context.scene.preflight_props.fbx_export_groups[
                self.group_idx].obj_names.add()
            helpers.redraw_properties()

        return {'FINISHED'}


class PF_OT_remove_preflight_object_operator(bpy.types.Operator):
    bl_idname = "preflight.remove_object_from_group"
    bl_label = "Remove Object"
    bl_description = "Remove object from this export group."

    group_idx: bpy.props.IntProperty()
    object_idx: bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None and self.object_idx is not None:
            context.scene.preflight_props.fbx_export_groups[
                self.group_idx].obj_names.remove(self.object_idx)
            helpers.redraw_properties()

        return {'FINISHED'}


class PF_OT_add_preflight_export_group_operator(bpy.types.Operator):
    bl_idname = "preflight.add_export_group"
    bl_label = "Add Export Group..."
    bl_description = "Add an export group. Each group will be exported to its own .fbx file with all selected objects."

    group_name: bpy.props.StringProperty(
        name="New Group Name",
        default="New Export Group"
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)

    def draw(self, context):
        self.layout.prop(self, "group_name", text="")

    def execute(self, context):
        groups = context.scene.preflight_props.fbx_export_groups
        new_group = groups.add()
        new_group.name = self.group_name
        helpers.redraw_properties()
        return {'FINISHED'}


class PF_OT_remove_preflight_export_group_operator(bpy.types.Operator):
    bl_idname = "preflight.remove_export_group"
    bl_label = "Remove Export Group"
    bl_description = "Remove an export group."

    group_idx: bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None:
            context.scene.preflight_props.fbx_export_groups.remove(
                self.group_idx)
            helpers.redraw_properties()
        return {'FINISHED'}


class PF_OT_export_mesh_group_operator(bpy.types.Operator):
    bl_idname = "preflight.export_single_group"
    bl_label = "Export Single Group"
    bl_description = "Export a single group to the chosen export destination."

    group_idx: bpy.props.IntProperty()

    def execute(self, context):
        # SANITY CHECK
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "File must be saved before exporting.")
            return {'CANCELLED'}

        if self.group_idx is None:
            self.report({'ERROR', "Must export a valid group."})
            return {'CANCELLED'}

        group = context.scene.preflight_props.fbx_export_groups[self.group_idx]

        # DO GROUP EXPORT
        try:
            self.export_group(group, context)
            self.report(
                {'INFO'}, "Exported Group {0} Successfully.".format(group.name))
            return {'FINISHED'}
        except Exception as e:
            print(e)
            self.report(
                {'ERROR'}, "There was an error while exporting: {0}.".format(group.name))
            return {'CANCELLED'}

    def select_objects(self, objects, append_selection=False):
        """
        Select all objects, raise an error if the object
        does not exist.
        """
        if not append_selection:
            bpy.ops.object.select_all(action='DESELECT')

        for obj in objects:
            if obj is not None:
                obj.select_set(True)
            else:
                message = error_message_for_obj_name(obj.name)
                self.report({'ERROR'}, message)
                raise ValueError(message)

        return True

    def toggle_hide_for_objects(self, objects, hide_state=False, values=[]):
        hidden_states = []

        for idx, obj in enumerate(objects):
            if obj is not None:
                hidden_states.insert(idx, obj.hide_viewport)
                new_state = values[idx] if idx < len(values) else hide_state
                obj.hide_viewport = new_state

        return hidden_states

    def export_objects(self, objects, filepath, **kwargs):
        # Unhide all objects and store their original hidden state
        original_hide_values = self.toggle_hide_for_objects(
            objects, hide_state=False)

        # Select Objects
        self.select_objects(objects)

        # Do Export
        export_opts = kwargs
        export_opts['filepath'] = filepath
        bpy.ops.export_scene.fbx(**export_opts)

        # Reset to original hide states
        self.toggle_hide_for_objects(objects, values=original_hide_values)

        # Deselect Objects
        bpy.ops.object.select_all(action='DESELECT')

    def export_group(self, group, context):
        """
        Export an export group according to its options and
        included objects.
        """

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Validate that we have objects
        if len(group.obj_names) < 1:
            message = "Must have at least 1 mesh to export group."
            self.report({'WARNING'}, message)
            raise ValueError(message)

        # Validate export path
        export_dir = context.scene.preflight_props.export_options.export_location
        export_path = export_path_for_string(
            group.name, export_dir, subdir=group.export_location)
        if not ensure_export_path(export_path):
            raise ValueError("Invalid Export Path")

        # Export files
        export_objects = [context.scene.objects.get(
            obj.obj_pointer.name) for obj in group.obj_names]

        export_options = context.scene.preflight_props.export_options.get_options_dict(
            bake_anim=group.include_animations,
            use_mesh_modifiers=group.apply_modifiers
        )

        self.export_objects(export_objects, export_path, **export_options)

    def export_animations(self, context):
        """
        Export each armature in the current context with all
        animations attached.
        """
        export_options = context.scene.preflight_props.export_options.defaults_for_unity(
            object_types={'ARMATURE'})

        for obj in context.scene.objects:
            if obj.type != 'ARMATURE':
                continue
            export_dir = context.scene.preflight_props.export_options.export_location
            export_path = export_path_for_string(
                obj.name, export_dir, suffix="@animations")
            if not ensure_export_path(export_path):
                raise ValueError("Invalid Export Path")
            self.export_objects([obj], export_path, **export_options)


class PF_OT_export_mesh_groups_operator(bpy.types.Operator):
    bl_idname = "preflight.export_all_groups"
    bl_label = "Export All Groups"
    bl_description = "Export all export groups to the chosen export destination."

    @classmethod
    def poll(cls, context):
        """
        Poll for ability to perform export. Only return
        true if there is at least 1 group, and all objects
        in export groups are set.
        """

        groups = context.scene.preflight_props.fbx_export_groups

        if len(groups) < 1:
            return False

        for group in groups:
            if len(group.obj_names) < 1:
                return False

            for obj in group.obj_names:
                if not obj.obj_pointer:
                    return False

        return True

    def execute(self, context):
        # SETUP
        groups = context.scene.preflight_props.fbx_export_groups

        # SAFETY CHECK
        if not helpers.groups_are_unique(groups):
            self.report(
                {'WARNING'}, "Cannot export with duplicate group names.")
            return {'CANCELLED'}

        if len(groups) < 1:
            self.report(
                {'WARNING'}, "Must have at least 1 export group to export files.")
            return {'CANCELLED'}

        # DO GROUP EXPORT
        for group_idx, group in enumerate(groups):
            try:
                bpy.ops.preflight.export_single_group(group_idx=group_idx)
                # self.export_group(group, context)
                self.report({'INFO'}, "Exported Group {0} of {1} Successfully.".format(
                    group_idx+1, len(groups)))
            except Exception as e:
                print(e)
                self.report(
                    {'ERROR'}, "There was an error while exporting: {0}.".format(group.name))
                return {'CANCELLED'}

        # DO ANIMATION EXPORT
        if context.scene.preflight_props.export_options.separate_animations:
            try:
                self.export_animations(context)
            except Exception as e:
                print(e)
                self.report(
                    {'ERROR'}, "There was an error while exporting animations")
                return {'CANCELLED'}

        # FINISH
        self.report(
            {'INFO'}, "Exported {0} Groups Successfully.".format(len(groups)))
        return {'FINISHED'}

    def export_animations(self, context):
        """
        Export each armature in the current context with all
        animations attached.
        """
        export_options = context.scene.preflight_props.export_options.defaults_for_unity(
            object_types={'ARMATURE'})

        for obj in context.scene.objects:
            if obj.type != 'ARMATURE':
                continue
            export_dir = context.scene.preflight_props.export_options.export_location
            export_path = export_path_for_string(
                obj.name, export_dir, suffix="@animations")
            if not ensure_export_path(export_path):
                raise ValueError("Invalid Export Path")
            self.export_objects([obj], export_path, **export_options)


class PF_OT_reset_export_options_operator(bpy.types.Operator):
    bl_idname = "preflight.reset_export_options"
    bl_label = "Reset Export Options"
    bl_description = "Reset all export options to default values."

    def execute(self, context):
        export_options = context.scene.preflight_props.export_options
        export_options.reset(export_options.defaults_for_unity().items())
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class PF_OT_export_group_move_slot(bpy.types.Operator):
    bl_idname = "preflight.export_group_move_slot"
    bl_label = "Move Export Group Slot"
    bl_description = "Move this Export Group up or down the list."

    group_idx: bpy.props.IntProperty()
    direction: bpy.props.StringProperty(default="UP")

    def execute(self, context):
        if self.direction == "UP":
            context.scene.preflight_props.fbx_export_groups.move(
                self.group_idx,  self.group_idx - 1)
        elif self.direction == "DOWN":
            context.scene.preflight_props.fbx_export_groups.move(
                self.group_idx,  self.group_idx + 1)
        return {'FINISHED'}


def ensure_export_path(export_path):
    try:
        export_dir = os.path.dirname(export_path)
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
    except:
        return False

    return True


def filename_for_string(s, suffix=""):
    """Determine Filename for String"""
    basename = bpy.path.clean_name("{0}{1}".format(s, suffix))
    return basename + ".fbx"


def export_path_for_string(s, dir, suffix="", subdir=""):
    """Determine the export path for an export group."""
    filename = filename_for_string(s, suffix=suffix)
    return bpy.path.abspath(os.path.join(dir, subdir, filename))


def error_message_for_obj_name(obj_name=""):
    """
    Determine the error message for a given object name.

    Keyword arguments:
    obj_name -- name of the object for error message (default "")
    """

    if not obj_name:
        return "Cannot export empty object."
    else:
        return 'Object "{0}" could not be found.'.format(obj_name)
