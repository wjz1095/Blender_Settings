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
# Created by Kushiro



import bpy
#import bmesh
import blf
import bgl
from mathutils import Matrix, Vector, Quaternion
from mathutils import bvhtree
from bpy_extras import view3d_utils
import gpu
from gpu_extras.batch import batch_for_shader
import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
)
import bmesh


shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')


def ShowMessageBox(messages = "", title = "", icon = 'BLENDER'):
    def draw(self, context):
        for s in messages:
            self.layout.label(text=s)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


def draw_line(points, color, blend=False, smooth=False, width=1):
    global shader

    if blend:
        bgl.glEnable(bgl.GL_BLEND)
    else:
        bgl.glDisable(bgl.GL_BLEND)

    if smooth:
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
    else:
        bgl.glDisable(bgl.GL_LINE_SMOOTH)
    
    bgl.glLineWidth(width)

    shader.bind()
    shader.uniform_float("color", color)
    batch = batch_for_shader(shader, 'LINES', {"pos": points})
    batch.draw(shader)

    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_LINE_SMOOTH)
    bgl.glLineWidth(1)    


def draw_text(pos, text_size, text):    
    blf.color(0, 1, 1, 1, 1)
    blf.position(0, pos.x, pos.y, 0)
    blf.size(0, text_size, 72)
    blf.draw(0, text)    

