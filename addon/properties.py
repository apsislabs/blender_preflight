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

#
# Custom Property Groups
#


class PreflightMeshGroup(bpy.types.PropertyGroup):
    """Property group of mesh names."""

    obj_name = bpy.props.StringProperty(
        name="Object Name",
        description="Name of the object to export. Note: If the object name changes, the reference will be lost.",
        default=""
    )


class PreflightExportGroup(bpy.types.PropertyGroup):
    """Property group of export options."""

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
    """Parent property group for preflight."""

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

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)