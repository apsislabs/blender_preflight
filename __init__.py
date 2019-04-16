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

from . properties import PreflightOptionsGroup
from . menus import PF_MT_preflight_menu
import traceback
import bpy
from . import developer_utils
import importlib

bl_info = {
    "name": "FBX Preflight",
    "author": "Apsis Labs",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "category": "Import-Export",
    "description": "Define export groups to be output as FBX files."
}

# load and reload submodules
##################################

importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(
    __path__, __name__, "bpy" in locals())


# register
##################################


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


def register():
    try:
        bpy.utils.register_module(__name__)
    except:
        traceback.print_exc()

    register_keymaps()
    bpy.types.Scene.preflight_props = bpy.props.PointerProperty(
        type=PreflightOptionsGroup)
    print("Registered {} with {} modules".format(
        bl_info["name"], len(modules)))


def unregister():
    try:
        bpy.utils.unregister_module(__name__)
    except:
        traceback.print_exc()

    unregister_keymaps()

    print("Unregistered {}".format(bl_info["name"]))
