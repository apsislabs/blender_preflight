bl_info = {
    "name": "Preflight",
    "category": "Object",
}

import bpy
import os
import re

LARGE_BUTTON_SCALE_Y = 1.5


class Preflight(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Pre-Flight FBX"
    bl_context = "objectmode"
    bl_category = "Pre-Flight FBX"

    def draw(self, context):
        layout = self.layout
        groups = context.scene.preflight.fbx_export_groups

        # Export Groups
        layout.operator("preflight.add_export_group",
                        text="Add Export Group", icon="ZOOMIN")
        for group_idx, group in enumerate(groups):
            self.layout_export_group(group_idx, group, layout, context)

        layout.separator()

        layout.prop(context.scene.preflight, "export_location")
        layout.prop(context.scene.preflight, "export_animations")

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
            group_box.label("Objects to Export:")
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
            group_box.prop(group, "include_armatures",
                           text="Include Armatures")
            group_box.prop(group, "include_animations",
                           text="Include Animations")

    def layout_mesh_row(self, mesh_idx, group_idx, mesh, layout, context):
        mesh_row = layout.row(align=True)
        mesh_row.prop_search(mesh, "obj_name", context.scene,
                             "objects", text="", icon="OBJECT_DATA")

        # Remove Mesh Button
        removeMeshButton = mesh_row.operator(
            "preflight.remove_object_from_group", text="", icon="ZOOMOUT")
        removeMeshButton.group_idx = group_idx
        removeMeshButton.object_idx = mesh_idx

#
# Custom Property Groups
#


class PreflightMeshGroup(bpy.types.PropertyGroup):
    obj_name = bpy.props.StringProperty(
        name="Object Name",
        description="Name of the object to export. Note: If the object name changes, the reference will be lost.",
        default=""
    )


class PreflightExportGroup(bpy.types.PropertyGroup):
    is_collapsed = bpy.props.BoolProperty(
        name="Collapse Group",
        description="Collapse the display of this export group.",
        default=False
    )
    name = bpy.props.StringProperty(
        name="Export Group Name",
        description="File name for this export group. Will be converted to camel case. Duplicate names will cause an error.",
        default=""
    )
    include_armatures = bpy.props.BoolProperty(
        name="Include Armatures",
        description="Autmatically include armatures for selected objects in this export.",
        default=True
    )
    include_animations = bpy.props.BoolProperty(
        name="Include Animations",
        description="Include animations along with the armatures in this export group.",
        default=False
    )
    obj_names = bpy.props.CollectionProperty(type=PreflightMeshGroup)


class PreflightOptionsGroup(bpy.types.PropertyGroup):
    fbx_export_groups = bpy.props.CollectionProperty(type=PreflightExportGroup)
    export_animations = bpy.props.BoolProperty(
        name="Export Animations to Separate File",
        description="Include all animations in a separate animations file.",
        default=True)
    export_location = bpy.props.StringProperty(
        name="Export To",
        description="Choose an export location. Relative location prefixed with '//'.",
        default="//preflight",
        maxlen=1024,
        subtype='DIR_PATH')


#
# Operators
#


class AddPreflightObjectOperator(bpy.types.Operator):
    bl_idname = "preflight.add_object_to_group"
    bl_label = "Add Object"
    bl_description = "Add an object to this export group."

    group_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None:
            context.scene.preflight.fbx_export_groups[self.group_idx].obj_names.add(
            )

        return {'FINISHED'}


class RemovePreflightObjectOperator(bpy.types.Operator):
    bl_idname = "preflight.remove_object_from_group"
    bl_label = "Remove Object"
    bl_description = "Remove object from this export group."

    group_idx = bpy.props.IntProperty()
    object_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None and self.object_idx is not None:
            context.scene.preflight.fbx_export_groups[self.group_idx].obj_names.remove(
                self.object_idx)

        return {'FINISHED'}


class AddPreflightExportGroupOperator(bpy.types.Operator):
    bl_idname = "preflight.add_export_group"
    bl_label = "Add Export Group"
    bl_description = "Add an export group. Each group will be exported to its own .fbx file with all selected objects."

    def execute(self, context):
        groups = context.scene.preflight.fbx_export_groups
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
            context.scene.preflight.fbx_export_groups.remove(self.group_idx)

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
        groups = context.scene.preflight.fbx_export_groups

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
        groups = context.scene.preflight.fbx_export_groups

        if self.groups_contain_duplicate_names(groups):
            self.report(
                {'WARNING'}, "Cannot export with duplicate group names.")
            return {'CANCELLED'}

        if len(groups) < 1:
            self.report(
                {'WARNING'}, "Must have at least 1 export group to export files.")
            return {'CANCELLED'}

        for group_idx, group in enumerate(groups):
            try:
                self.export_group(group, context)
                self.report({'INFO'}, "Exported Group {0} of {1} Successfully.".format(
                    group_idx, len(groups)))
            except Exception as e:
                print(e)
                self.report(
                    {'ERROR'}, "There was an error while exporting: {0}.".format(group.name))
                return {'CANCELLED'}

        self.report(
            {'INFO'}, "Exported {0} Groups Successfully.".format(len(groups)))

        if context.scene.preflight.export_animations:
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
            self.report(
                {'WARNING'}, "Must have at least 1 mesh to export group.")
            return {'CANCELLED'}

        # Validate export path
        export_path = self.export_path_for_string(group.name, context.scene)
        self.ensure_export_path(export_path)

        # Export files
        object_names = [g.obj_name for g in group.obj_names]
        self.export_objects_by_name(
            obj_names=object_names,
            context=context,
            export_path=export_path,
            include_animations=group.include_animations,
            include_armatures=group.include_armatures
        )

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
            self.export_objects_by_name(
                [obj.name], context, export_path, include_armatures=True, include_animations=True, object_types={'ARMATURE'})

    def groups_contain_duplicate_names(self, groups):
        group_names = [group.name for group in groups]
        return len(group_names) != len(set(group_names))

    def select_objects_by_name(self, obj_names, scene):
        """
        Given an array of object names, select them in the
        scene. Selection is additive, so sequential calls
        to this method will result in additional selections.

        Keyword arguments:
        obj_names   -- the names of the objects to select
        scene       -- the scene to select in
        """

        for name in obj_names:
            obj = scene.objects.get(name)
            if obj is not None:
                obj.select = True
            else:
                self.report(
                    {'ERROR'}, self.error_message_for_obj_name(name))
                return {'CANCELLED'}

    def select_armatures_for_object_names(self, obj_names, scene):
        for name in obj_names:
            obj = scene.objects.get(name)
            if (obj.type == "MESH"):
                armature = obj.find_armature()
                if armature is not None:
                    armature.select = True

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

    def ensure_export_path(self, export_path):
        export_dir = os.path.dirname(export_path)
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

    def export_path_for_string(self, s, scene, suffix=""):
        """Determine the export path for an export group."""
        filename = self.filename_for_string(s, suffix=suffix)
        directory = bpy.path.abspath(scene.preflight.export_location)

        return os.path.join(directory, filename)

    def filename_for_string(self, s, suffix=""):
        filepath = bpy.data.filepath
        filename = os.path.splitext(os.path.basename(filepath))[0]

        return "{0}-{1}{2}.fbx".format(
            to_camelcase(filename),
            to_camelcase(s),
            suffix
        )

    def export_objects_by_name(self, obj_names, context, export_path, include_armatures=False, include_animations=False, object_types={'ARMATURE', 'MESH'}):
        # Select Objects
        self.select_objects_by_name(obj_names, context.scene)

        if include_armatures:
            self.select_armatures_for_object_names(obj_names, context.scene)

        # Do Export
        bpy.ops.export_scene.fbx(
            filepath=export_path,
            axis_forward='-Z',
            axis_up='Y',
            use_selection=True,
            bake_space_transform=True,
            object_types=object_types,
            use_armature_deform_only=True,
            use_mesh_modifiers_render=False,
            bake_anim=include_animations,
            use_anim=include_animations
        )

        # Deselect Objects
        bpy.ops.object.select_all(action='DESELECT')


def to_camelcase(s):
    """
    Return the given string converted to camelcase. Remove all spaces. 
    """
    words = re.split("[^a-zA-Z0-9]+", s)
    return "".join(w.lower() if i is 0 else w.title() for i, w in enumerate(words))


def register():
    bpy.utils.register_class(Preflight)

    bpy.utils.register_class(PreflightMeshGroup)
    bpy.utils.register_class(PreflightExportGroup)
    bpy.utils.register_class(PreflightOptionsGroup)

    bpy.utils.register_class(AddPreflightObjectOperator)
    bpy.utils.register_class(RemovePreflightObjectOperator)
    bpy.utils.register_class(AddPreflightExportGroupOperator)
    bpy.utils.register_class(RemovePreflightExportGroupOperator)

    bpy.utils.register_class(ExportMeshGroupsOperator)


def unregister():
    bpy.utils.unregister_class(Preflight)

    bpy.utils.unregister_class(PreflightMeshGroup)
    bpy.utils.unregister_class(PreflightExportGroup)
    bpy.utils.unregister_class(PreflightOptionsGroup)

    bpy.utils.unregister_class(AddPreflightObjectOperator)
    bpy.utils.unregister_class(RemovePreflightObjectOperator)
    bpy.utils.unregister_class(AddPreflightExportGroupOperator)
    bpy.utils.unregister_class(RemovePreflightExportGroupOperator)

    bpy.utils.unregister_class(ExportMeshGroupsOperator)


def init():
    bpy.types.Scene.preflight = bpy.props.PointerProperty(
        type=PreflightOptionsGroup)


if __name__ == "__main__":
    register()
    init()
