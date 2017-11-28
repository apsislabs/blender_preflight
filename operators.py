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


class AddPreflightObjectOperator(bpy.types.Operator):
    bl_idname = "preflight.add_object_to_group"
    bl_label = "Add Object"
    bl_description = "Add an object to this export group."

    group_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None:
            context.scene.preflight_props.fbx_export_groups[
                self.group_idx].obj_names.add()

        return {'FINISHED'}


class RemovePreflightObjectOperator(bpy.types.Operator):
    bl_idname = "preflight.remove_object_from_group"
    bl_label = "Remove Object"
    bl_description = "Remove object from this export group."

    group_idx = bpy.props.IntProperty()
    object_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None and self.object_idx is not None:
            context.scene.preflight_props.fbx_export_groups[
                self.group_idx].obj_names.remove(self.object_idx)

        return {'FINISHED'}


class AddPreflightExportGroupOperator(bpy.types.Operator):
    bl_idname = "preflight.add_export_group"
    bl_label = "Add Export Group"
    bl_description = "Add an export group. Each group will be exported to its own .fbx file with all selected objects."

    def execute(self, context):
        groups = context.scene.preflight_props.fbx_export_groups
        new_group = groups.add()
        new_group.name = "Export Group {0}".format(str(len(groups)))
        return {'FINISHED'}


class RemovePreflightExportGroupOperator(bpy.types.Operator):
    bl_idname = "preflight.remove_export_group"
    bl_label = "Remove Export Group"
    bl_description = "Remove an export group."

    group_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None:
            context.scene.preflight_props.fbx_export_groups.remove(
                self.group_idx)

        return {'FINISHED'}


class ExportMeshGroupsOperator(bpy.types.Operator):
    bl_idname = "preflight.export_groups"
    bl_label = "Export All Groups"
    bl_description = "Export all export groups to the chosen export destination."

    # Poll for ability to perform export. Only return
    # true if there is at least 1 group, and all objects
    # in export groups are set.
    @classmethod
    def poll(cls, context):
        groups = context.scene.preflight_props.fbx_export_groups

        if len(groups) < 1:
            return False

        for group in groups:
            if len(group.obj_names) < 1:
                return False

            for obj in group.obj_names:
                if not obj.obj_name:
                    return False

        return True

    def execute(self, context):
        # Sanity Check
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "File must be saved before exporting.")
            return {'CANCELLED'}

        # iterate through groups
        groups = context.scene.preflight_props.fbx_export_groups

        if self.groups_contain_duplicate_names(groups):
            self.report({'WARNING'},
                        "Cannot export with duplicate group names.")
            return {'CANCELLED'}

        if len(groups) < 1:
            self.report({'WARNING'},
                        "Must have at least 1 export group to export files.")
            return {'CANCELLED'}

        for group_idx, group in enumerate(groups):
            try:
                self.export_group(group, context)
                self.report({'INFO'},
                            "Exported Group {0} of {1} Successfully.".format(
                                group_idx, len(groups)))
            except Exception as e:
                print(e)
                self.report({'ERROR'},
                            "There was an error while exporting: {0}.".format(
                                group.name))
                return {'CANCELLED'}

        self.report({'INFO'}, "Exported {0} Groups Successfully.".format(
            len(groups)))

        if context.scene.preflight_props.export_animations:
            self.export_animations(context)

        return {'FINISHED'}

    def export_group(self, group, context):
        """
        Export an export group according to its options and
        included objects.
        """

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Validate that we have objects
        if len(group.obj_names) < 1:
            self.report({'WARNING'}, "Must have at least 1 mesh to export group.")
            return {'CANCELLED'}

        # Validate export path
        export_path = self.export_path_for_string(group.name, context.scene)
        self.ensure_export_path(export_path)

        # Export files
        objects = [context.scene.objects.get(obj.obj_name) for obj in group.obj_names]
        self.export_objects(
            objects=objects,
            filepath=export_path,
            use_mesh_modifiers=group.apply_modifiers,
            include_animations=group.include_animations)

    def export_animations(self, context):
        """
        Export each armature in the current context with all
        animations attached.
        """

        for obj in context.scene.objects:
            if obj.type != 'ARMATURE':
                continue

            export_path = self.export_path_for_string(
                obj.name, context.scene, suffix="@animations")
            self.ensure_export_path(export_path)
            self.export_objects(
                [obj],
                export_path,
                include_armatures=True,
                include_animations=True,
                object_types={'ARMATURE'})

    def groups_contain_duplicate_names(self, groups):
        group_names = [group.name for group in groups]
        return len(group_names) != len(set(group_names))

    def select_armatures_for_object_names(self, obj_names, scene):
        for name in obj_names:
            obj = scene.objects.get(name)
            if (obj.type == "MESH"):
                armature = obj.find_armature()
                if armature is not None:
                    armature.select = True

    def ensure_export_path(self, export_path):
        export_dir = os.path.dirname(export_path)
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

    def export_path_for_string(self, s, scene, suffix=""):
        """Determine the export path for an export group."""
        filename = self.filename_for_string(s, suffix=suffix)
        directory = bpy.path.abspath(scene.preflight_props.export_location)

        return os.path.join(directory, filename)

    def filename_for_string(self, s, suffix=""):
        filepath = bpy.data.filepath
        filename = os.path.splitext(os.path.basename(filepath))[0]

        return "{0}-{1}{2}.fbx".format(
            to_camelcase(filename), to_camelcase(s), suffix)

    def export_objects(self, objects, filepath, **kwargs):
        bpy.ops.object.select_all(action='DESELECT')

        self.select_objects(objects)

        # Change settings for include_animations
        include_armatures = kwargs.pop('include_armatures', None)
        include_anim = kwargs.pop('include_animations', None)
        if include_anim is not None:
            kwargs['bake_anim'] = bool(include_anim)
            kwargs['use_anim'] = bool(include_anim)

        # Do Export
        export_opts = {**defaults_for_unity(), **kwargs}
        export_opts['filepath'] = filepath

        bpy.ops.export_scene.fbx(**export_opts)

        # Deselect Objects
        bpy.ops.object.select_all(action='DESELECT')

    def select_objects(self, objects):
        """
        Select all objects, raise an error if the object
        does not exist.
        """
        for obj in objects:
            if obj is not None:
                obj.select = True
            else:
                message = error_message_for_obj_name(obj.name)
                self.report({'ERROR'}, message)
                raise ValueError(message)

        return True



def error_message_for_obj_name(self, obj_name=""):
    """
    Determine the error message for a given object name.

    Keyword arguments:
    obj_name -- name of the object for error message (default "")
    """

    if not obj_name:
        return "Cannot export empty object."
    else:
        return 'Object "{0}" could not be found.'.format(obj_name)

def defaults_for_unity():
    return {
        'axis_forward': '-Z',
        'axis_up': 'Y',
        'use_selection': True,
        'bake_space_transform': True,
        'object_types': {'ARMATURE', 'MESH'},
        'use_armature_deform_only': True,
        'use_mesh_modifiers': True,
        'use_mesh_modifiers_render': False,
        'bake_anim': True,
        'use_anim': True
    }


def to_camelcase(s):
    """
    Return the given string converted to camelcase. Remove all spaces. 
    """
    words = re.split("[^a-zA-Z0-9]+", s)
    return "".join(
        w.lower() if i is 0 else w.title() for i, w in enumerate(words))
