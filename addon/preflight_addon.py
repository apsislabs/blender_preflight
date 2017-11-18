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

        for group_idx, group in enumerate(context.scene.fbx_export_groups):
            self.layout_export_group(group_idx, group, layout, context)
    
        layout.operator("preflight.add_export_group", text="Add Export Group", icon="ZOOMIN")

        layout.separator()

        export_row = layout.row()
        export_row.scale_y = 1.5
        export_row.operator("preflight.add_export_group", text="Export All", icon="EXPORT")

    def layout_export_group(self, group_idx, group, layout, context):
        group_box = layout.box()

        # Header Row
        row = group_box.row()
        row.prop(group, "name", text="")
        removeGroupButton = row.operator("preflight.remove_export_group", text="", icon="X")
        removeGroupButton.group_idx = group_idx

        # Mesh Collection
        mesh_column = group_box.column(align=True)
        for mesh_idx, mesh in enumerate(group.mesh_names):
            self.layout_mesh_row(mesh_idx, group_idx, mesh, mesh_column, context)
        
        # Add Mesh Button
        addMeshButton = mesh_column.operator("preflight.add_mesh_to_group", text="Add Mesh", icon="ZOOMIN")
        addMeshButton.group_idx = group_idx

        # Export Options
        group_box.prop(group, "include_armatures", text="Include Armatures")
        group_box.prop(group, "include_animations", text="Include Animations")

    def layout_mesh_row(self, mesh_idx, group_idx, mesh, layout, context):
        mesh_row = layout.row(align=True)
        mesh_row.prop_search( mesh, "mesh_name", context.scene, "objects", text="", icon="OBJECT_DATA")

        # Remove Mesh Button
        removeMeshButton = mesh_row.operator("preflight.remove_mesh_from_group", text="", icon="X")
        removeMeshButton.group_idx = group_idx
        removeMeshButton.object_idx = mesh_idx

#
# Custom Property Groups
#

class PreflightMeshGroup(bpy.types.PropertyGroup):
    mesh_name = bpy.props.StringProperty(name="Mesh Name", default="Unknown")

class PreflightExportGroup(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Test Prop", default="Unknown")
    include_armatures = bpy.props.BoolProperty(name="Include Armatures", default=True)
    include_animations = bpy.props.BoolProperty(name="Include Animations", default=False)
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