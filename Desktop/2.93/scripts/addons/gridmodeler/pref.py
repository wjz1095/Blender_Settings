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

from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, FloatProperty, EnumProperty, FloatVectorProperty


class GridModelerPreferences(AddonPreferences):
    bl_idname = __package__

    textsize: IntProperty(
        name="Text Size",
        default=14,
    )

    text_pos_x: IntProperty(
        name="Text X position",
        default=90,
    )    

    default_operation_mode : EnumProperty(
                #(identifier, name, description, icon, number)
        items = [('triangles','Triangles','','',0), 
                 ('ngon','N-gon','','',1),
                 ('newface','Create face','','',2),
                 ('boolcut','Boolean Cut','','',3),
                 ],
        name = "Default Operation Mode",
        default = 'boolcut')

    bool_abs: BoolProperty(
        name="Use Absolute Mode",
        description="Default grid size mode",
        default=True
    )   

    bool_showkey: BoolProperty(
        name="Show pressed key on the screen",
        description="Show pressed key on the screen (for video recording)",
        default=False
    )       

    line_color: FloatVectorProperty(  
        name="Grid Line Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 0.2),
        min=0.0, max=1.0,
        description="Grid Line Color"
        )

    shape_color: FloatVectorProperty(  
        name="Shape Line Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        description="Shape Line Color"
        )    

    def draw(self, context):
        layout = self.layout
        layout.label(text="Text size for hints (left bottom)")
        row = layout.row()
        row.prop(self, "textsize")
        
        layout.label(text="Default operation mode")
        row = layout.row()
        row.prop(self, 'default_operation_mode', expand=True)

        layout.label(text="Default grid size mode")
        row = layout.row()
        row.prop(self, 'bool_abs' )

        layout.label(text="Show pressed key on the screen")
        row = layout.row()
        row.prop(self, 'bool_showkey' )    

        layout.label(text="Text X position")
        row = layout.row()
        row.prop(self, "text_pos_x")        

        layout.label(text="Colors Setting : ")
        row = layout.row()
        row.prop(self, "line_color")
        row = layout.row()
        row.prop(self, "shape_color")        



def get_pref():
    pe = {'textsize' : 14, 
        'default_ope': 'boolcut',
        'bool_abs' : True,
        'bool_showkey': False,
        'text_pos_x': 120, 
        'line_color': (1, 1, 1, 0.2),
        'shape_color': (1, 1, 1, 1)}

    try:
        addons = bpy.context.preferences.addons
        if __package__ in addons:
            this_addon = addons[__package__]            
            if hasattr(this_addon, 'preferences'):
                pre = this_addon.preferences                
                pe['textsize'] = pre.textsize
                pe['default_ope'] = pre.default_operation_mode
                pe['bool_abs'] = pre.bool_abs
                pe['bool_showkey'] = pre.bool_showkey
                pe['text_pos_x'] = pre.text_pos_x
                pe['line_color'] = pre.line_color
                pe['shape_color'] = pre.shape_color
                return pe

    except:
        print('pref error')
        pass
    return pe



        