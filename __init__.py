# # ##### BEGIN GPL LICENSE BLOCK #####
# #
# #  This program is free software; you can redistribute it and/or
# #  modify it under the terms of the GNU General Public License
# #  as published by the Free Software Foundation; either version 2
# #  of the License, or (at your option) any later version.
# #
# #  This program is distributed in the hope that it will be useful,
# #  but WITHOUT ANY WARRANTY; without even the implied warranty of
# #  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #  GNU General Public License for more details.
# #
# #  You should have received a copy of the GNU General Public License
# #  along with this program; if not, write to the Free Software Foundation,
# #  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# #
# # ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "FBX Preflight",
    "author": "Apsis Labs",
    "version": (2, 0, 0),
    "blender": (2, 80, 0),
    "category": "Import-Export",
    "description": "Define export groups to be output as FBX files."
}

# load and reload submodules
##################################

from . import developer_utils
import importlib

importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(
    __path__, __name__, "bpy" in locals())


# register
##################################
import bpy
import traceback

addon_keymaps = []


def register_keymaps():
    global addon_keymaps
    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
        km = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi_mnu = km.keymap_items.new("wm.call_menu", "M", "PRESS", alt=True)
        kmi_mnu.properties.name = PF_MT_preflight_menu.bl_idname
        addon_keymaps.append((km, kmi_mnu))


def unregister_keymaps():
    global addon_keymaps
    for km, shortcut in addon_keymaps:
        km.keymap_items.remove(shortcut)

    addon_keymaps.clear()


from . properties import PreflightMeshGroup
from . properties import PreflightExportGroup
from . properties import PreflightExportOptionsGroup
from . properties import PreflightOptionsGroup
from . menus import PF_MT_preflight_menu
from . menus import PF_MT_remove_export_group_menu
from . menus import PF_MT_add_selection_menu
from . operators import PF_OT_add_selection_to_preflight_group
from . operators import PF_OT_create_preflight_group_from_selection
from . operators import PF_OT_add_preflight_object_operator
from . operators import PF_OT_remove_preflight_object_operator
from . operators import PF_OT_add_preflight_export_group_operator
from . operators import PF_OT_remove_preflight_export_group_operator
from . operators import PF_OT_export_mesh_group_operator
from . operators import PF_OT_export_mesh_groups_operator
from . operators import PF_OT_reset_export_options_operator
from . operators import PF_OT_export_group_move_slot
from . panels import PF_PT_preflight_panel
from . panels import PF_PT_preflight_export_options_panel
from . ui import PF_UL_export_object_ui_list


classes = (
    PreflightMeshGroup,
    PreflightExportGroup,
    PreflightExportOptionsGroup,
    PreflightOptionsGroup,
    PF_MT_preflight_menu,
    PF_MT_remove_export_group_menu,
    PF_MT_add_selection_menu,
    PF_OT_add_selection_to_preflight_group,
    PF_OT_create_preflight_group_from_selection,
    PF_OT_add_preflight_object_operator,
    PF_OT_remove_preflight_object_operator,
    PF_OT_add_preflight_export_group_operator,
    PF_OT_remove_preflight_export_group_operator,
    PF_OT_export_mesh_group_operator,
    PF_OT_export_mesh_groups_operator,
    PF_OT_reset_export_options_operator,
    PF_OT_export_group_move_slot,
    PF_PT_preflight_panel,
    PF_PT_preflight_export_options_panel,
    PF_UL_export_object_ui_list,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    register_keymaps()
    bpy.types.Scene.preflight_props = bpy.props.PointerProperty(type=PreflightOptionsGroup)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    unregister_keymaps()


if __name__ == "__main__":
    register()
