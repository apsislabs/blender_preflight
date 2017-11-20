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

bl_info = {
    "name": "FBX Preflight",
    "author": "Apsis Labs",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "category": "Import-Export",
    "description": "Define export groups to be output as FBX files."
}

import bpy
import addon_utils

from .properties import *
from .operators import *
from .preflight import PreflightPanel

# Reload all modules because blender doesn't do this.
# Sourced from: https://github.com/zeffii/mesh_tiny_cad
if "bpy" in locals():
    if 'Preflight' in locals():

        print('Preflight: detected reload event.')
        import importlib

        try:
            modules = (properties, operators, preflight)
            for m in modules:
                importlib.reload(m)
            print("Preflight: reloaded modules, all systems operational")

        except Exception as E:
            print('reload failed with error:')
            print(E)


def register():
    bpy.utils.register_module(__name__)
    addon_utils.enable("io_scene_fbx", default_set=True, persistent=True)
    bpy.types.Scene.preflight_props = bpy.props.PointerProperty(
        name="Preflight Properties",
        type=PreflightOptionsGroup
    )


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.preflight_props


if __name__ == "__main__":
    register()
