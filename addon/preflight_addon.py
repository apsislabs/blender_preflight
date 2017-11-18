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
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout

        for group_idx, group in enumerate(context.scene.fbx_export_groups):
            self.layout_export_group(group_idx, group, layout, context)
        
        layout.separator()
        layout.operator("preflight.add_export_group", text="Add Export Group")

    def layout_export_group(self, group_idx, group, layout, context):
        box = layout.box()

        # Header Row
        row = box.row()
        row.prop(group, "name", text="")
        removeGroupButton = row.operator("preflight.remove_export_group", text="", icon="X")
        removeGroupButton.group_idx = group_idx

        # Mesh Collection
        for mesh_idx, mesh in enumerate(group.mesh_names):
            self.layout_mesh_row(mesh_idx, group_idx, mesh, box, context)
        
        # Add Mesh Button
        addMeshButton = box.operator("preflight.add_mesh_to_group", text="Add Mesh", icon="PLUS")
        addMeshButton.group_idx = group_idx

    def layout_mesh_row(self, mesh_idx, group_idx, mesh, box, context):
        box_row = box.row(align=True)
        box_row.prop_search( mesh, "mesh_name", context.scene, "objects", text="", icon="OBJECT_DATA")

        # Remove Mesh Button
        removeMeshButton = box_row.operator("preflight.remove_mesh_from_group", text="", icon="X")
        removeMeshButton.group_idx = group_idx
        removeMeshButton.object_idx = mesh_idx

#
# Custom Property Groups
#

class PreflightMeshGroup(bpy.types.PropertyGroup):
    mesh_name = bpy.props.StringProperty(name="Mesh Name", default="Unknown")

class PreflightExportGroup(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Test Prop", default="Unknown")
    mesh_names = bpy.props.CollectionProperty(type=PreflightMeshGroup)

#
# Operators
#

class AddPreflightMeshOperator(bpy.types.Operator):
    bl_idname = "preflight.add_mesh_to_group"
    bl_label = "Add Mesh"

    group_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None:
            context.scene.fbx_export_groups[self.group_idx].mesh_names.add()
        
        return {'FINISHED'}

class RemovePreflightMeshOperator(bpy.types.Operator):
    bl_idname = "preflight.remove_mesh_from_group"
    bl_label = "Remove Mesh"

    group_idx = bpy.props.IntProperty()
    object_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None and self.object_idx is not None:
            context.scene.fbx_export_groups[self.group_idx].mesh_names.remove(self.object_idx)
        
        return {'FINISHED'}

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

def unregister():
    bpy.utils.unregister_class(Preflight)
    
    bpy.utils.unregister_class(PreflightMeshGroup)
    bpy.utils.unregister_class(PreflightExportGroup)
    
    bpy.utils.unregister_class(AddPreflightMeshOperator)
    bpy.utils.unregister_class(RemovePreflightMeshOperator)
    bpy.utils.unregister_class(AddPreflightExportGroupOperator)
    bpy.utils.unregister_class(RemovePreflightExportGroupOperator)

def init():
    bpy.types.Scene.fbx_export_groups = bpy.props.CollectionProperty(type=PreflightExportGroup)

if __name__ == "__main__":
    register()
    init()