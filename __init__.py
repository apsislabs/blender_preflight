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

from . panels import (PreflightPanel, PreflightExportOptionsPanel)
from . ui import (ExportObjectUIList)
from . operators import (
    AddPreflightObjectOperator,
    RemovePreflightObjectOperator,
    AddPreflightExportGroupOperator,
    RemovePreflightExportGroupOperator,
    ExportMeshGroupsOperator)
from . properties import (
    PreflightMeshGroup,
    PreflightExportGroup,
    PreflightOptionsGroup
)
from . import helpers
import addon_utils
import os
import bpy

bl_info = {
    "name": "FBX Preflight",
    "author": "Apsis Labs",
    "version": (0, 1, 2),
    "blender": (2, 79, 0),
    "category": "Import-Export",
    "description": "Define export groups to be output as FBX files."
}


# Updater

if 'bpy' in locals() and 'PreflightPanel' in locals():
    print("Reload Event Detected...")
    import importlib
    for m in (properties, operators, ui, panels, helpers):
        importlib.reload(m)


def register():
    bpy.utils.register_module(__name__)
    addon_utils.enable("io_scene_fbx", default_set=True, persistent=True)
    bpy.types.Scene.preflight_props = bpy.props.PointerProperty(
        type=PreflightOptionsGroup)


def unregister():
    del bpy.types.Scene.preflight_props
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
