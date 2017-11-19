bl_info = {
    "name": "Preflight",
    "category": "Object",
}

import bpy

class Preflight(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Pre-Flight FBX"
    bl_context = "objectmode"
    bl_category = "Pre-Flight FBX"

    def draw(self, context):
        layout = self.layout
        groups = context.scene.fbx_export_groups

        # Export Groups
        for group_idx, group in enumerate(groups):
            self.layout_export_group(group_idx, group, layout, context)

        layout.operator("preflight.add_export_group", text="Add Export Group", icon="ZOOMIN")
        layout.separator()

        # Export Button
        export_row = layout.row()
        export_row.scale_y = 1.5
        # if len(groups) < 1: export_row.enable = False

        exportButton = export_row.operator("preflight.export_groups", text="Export All", icon="EXPORT")

    def layout_export_group(self, group_idx, group, layout, context):
        group_box = layout.box()

        # Header Row
        row = group_box.row()
        row.prop(group, "name", text="")
        removeGroupButton = row.operator("preflight.remove_export_group", text="", icon="X")
        removeGroupButton.group_idx = group_idx

        # Mesh Collection
        mesh_column = group_box.column(align=True)
        for mesh_idx, mesh in enumerate(group.obj_names):
            self.layout_mesh_row(mesh_idx, group_idx, mesh, mesh_column, context)
        
        # Add Mesh Button
        addMeshButton = mesh_column.operator("preflight.add_mesh_to_group", text="Add Mesh", icon="ZOOMIN")
        addMeshButton.group_idx = group_idx

        # Export Options
        group_box.prop(group, "include_armatures", text="Include Armatures")
        group_box.prop(group, "include_animations", text="Include Animations")

    def layout_mesh_row(self, mesh_idx, group_idx, mesh, layout, context):
        mesh_row = layout.row(align=True)
        mesh_row.prop_search( mesh, "obj_name", context.scene, "objects", text="", icon="OBJECT_DATA")

        # Remove Mesh Button
        removeMeshButton = mesh_row.operator("preflight.remove_mesh_from_group", text="", icon="ZOOMOUT")
        removeMeshButton.group_idx = group_idx
        removeMeshButton.object_idx = mesh_idx

#
# Custom Property Groups
#

class PreflightMeshGroup(bpy.types.PropertyGroup):
    obj_name = bpy.props.StringProperty(name="Mesh Name", default="")

class PreflightExportGroup(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Test Prop", default="Unknown")
    include_armatures = bpy.props.BoolProperty(name="Include Armatures", default=True)
    include_animations = bpy.props.BoolProperty(name="Include Animations", default=False)
    obj_names = bpy.props.CollectionProperty(type=PreflightMeshGroup)

#
# Operators
#

class AddPreflightMeshOperator(bpy.types.Operator):
    bl_idname = "preflight.add_mesh_to_group"
    bl_label = "Add Mesh"

    group_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None:
            context.scene.fbx_export_groups[self.group_idx].obj_names.add()
        
        return {'FINISHED'}

class RemovePreflightMeshOperator(bpy.types.Operator):
    bl_idname = "preflight.remove_mesh_from_group"
    bl_label = "Remove Mesh"

    group_idx = bpy.props.IntProperty()
    object_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None and self.object_idx is not None:
            context.scene.fbx_export_groups[self.group_idx].obj_names.remove(self.object_idx)
        
        return {'FINISHED'}

class ExportMeshGroupsOperator(bpy.types.Operator):
    bl_idname = "preflight.export_groups"
    bl_label = "Export Groups"

    # Poll for ability to perform export. Only return
    # true if there is at least 1 group, and all objects
    # in export groups are set.
    @classmethod
    def poll(cls, context):
        groups = context.scene.fbx_export_groups

        if len(groups) < 1: return False
        
        for group in groups:
            if len(group.obj_names:
                if not mesh.obj_name: return False
        
        return True

    def execute(self, context):
        # iterate through groups
        groups = context.scene.fbx_export_groups

        if len(groups) < 1:
            self.report({'ERROR'}, "Must have at least 1 export group to export files." )
            return {'CANCELED'}

        for group_idx, group in enumerate(groups):
            self.deselect_all()

            if len(group.obj_names) < 1:
                self.report({'ERROR'}, "Must have at least 1 mesh to export group." )
                return {'CANCELED'}
            
            # select correct items
            self.select_objects_by_name(group.obj_names, context.scene)
        # validate export path
        # export files
        return {'FINISHED'}

    def deselect_all(self):
        """Deselect all objects."""

        bpy.ops.object.select_all(action='DESELECT')

    def select_objects_by_name(self, obj_names, scene):
        """
        Given an array of object names, select them in the
        scene. Selection is additive, so sequential calls
        to this method will result in additional selections.

        Keyword arguments:
        obj_names   -- the names of the objects to select
        scene       -- the scene to select in
        """

        for mesh in obj_names:
            ob = scene.objects.get(mesh.obj_name)
            if ob is not None:
                ob.select = True
            else:
                self.report({'ERROR'}, self.error_message_for_obj_name(mesh.obj_name) )
                return {'CANCELLED'}
              
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

    def validate_export_path(self, export_path):
        return False

    def export_path_for_group(self, group):
        return False

class AddPreflightExportGroupOperator(bpy.types.Operator):
    bl_idname = "preflight.add_export_group"
    bl_label = "Add Export Group"

    def execute(self, context):
        context.scene.fbx_export_groups.add()
        return {'FINISHED'}

class RemovePreflightExportGroupOperator(bpy.types.Operator):
    bl_idname = "preflight.remove_export_group"
    bl_label = "Remove Export Group"

    group_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None:
            context.scene.fbx_export_groups.remove(self.group_idx)

        return {'FINISHED'}


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.

def register():
    bpy.utils.register_class(Preflight)

    bpy.utils.register_class(PreflightMeshGroup)
    bpy.utils.register_class(PreflightExportGroup)

    bpy.utils.register_class(AddPreflightMeshOperator)
    bpy.utils.register_class(RemovePreflightMeshOperator)
    bpy.utils.register_class(AddPreflightExportGroupOperator)
    bpy.utils.register_class(RemovePreflightExportGroupOperator)

    bpy.utils.register_class(ExportMeshGroupsOperator)

def unregister():
    bpy.utils.unregister_class(Preflight)
    
    bpy.utils.unregister_class(PreflightMeshGroup)
    bpy.utils.unregister_class(PreflightExportGroup)
    
    bpy.utils.unregister_class(AddPreflightMeshOperator)
    bpy.utils.unregister_class(RemovePreflightMeshOperator)
    bpy.utils.unregister_class(AddPreflightExportGroupOperator)
    bpy.utils.unregister_class(RemovePreflightExportGroupOperator)

    bpy.utils.unregister_class(ExportMeshGroupsOperator)

def init():
    bpy.types.Scene.fbx_export_groups = bpy.props.CollectionProperty(type=PreflightExportGroup)

if __name__ == "__main__":
    register()
    init()