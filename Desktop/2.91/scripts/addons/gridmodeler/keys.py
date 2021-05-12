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


txt = '''

This is Basic Usage Guide.
For more functions and details, please visit : 
https://www.kushirocg.com/gridmodeler


After drawing shapes, the keys to execute operation are:

1 key : Cut and n-gon fill

2 key : Cut and triangle fill

3 key : Create new face

4 key : Boolean cut

5 key : Boolean slice

9 key : Edge Pipe

0 key : Construction line cut (special function)


==================================

Modes : 
There are two modes in Grid Modeler (switch by Right Click):

1.  Normal Mode : drawing shapes, by line or circle tool

2.  Selection Mode : select shapes, copy and paste, rotate, 
flip, bevel, array, etc

=================================


Normal Mode
(When you select a face and run the tool, you are in Normal Mode)

Mouse Left Click : draw lines

Mouse Right Click : switch to Selection Mode

Ctrl + Mouse wheel scroll : increase / decrease number of grids

Alt + Mouse wheel scroll : increase / decrease the size of grid plane

Q key / Enter key : quick commit operation, cut the mesh

A key : Switch between Absolute Size Mode / Relative Size mode


Ctrl + Z : undo the draw

U key : Turn off grid snapping (press again to turn on)

P key : Rotate grid plane at the location of last drawn point

Ctrl + P key : Rotate grid plane by 90 degree, based on alignment edge 
(set by Ctrl + click)

In U key mode (snapping off) : Hold left mouse button down and draw : 
free-hand drawing

Y key : Construction Line mode (press again to turn off)

W key : It will quick-switch into Selection mode, and select the last created shape automatically.


Ctrl + Left Click on an edge of selected faces :  This is the most important 
function, it change the alignment of the grids plane, align the grids to the 
edge, and center the lines to the middle of the edge. You need to use this 
function often.



C key : use Circle tool

In Circle tool> Left click : draw the center of circle

In Circle tool> Shift + Mouse wheel scroll : change the number of sides of 
circle, min is 3 (become a triangle), you can use 4 for square, 5 for pentagon.

In Circle tool> C key : turn off Circle tool

In Circle tool> Esc key : cancel


============================================
Selection Mode
Mouse Left Click : select a shape

Mouse Right Click : leave Selection Mode

U key : Turn off grid snapping (press again to turn on)

Q key / Enter key : commit the operation, cut the mesh

Mouse drag a yellow rectangle : select multiple shapes

Selected shapes > Ctrl + C : copy the shapes

Selected shapes > Ctrl + V : paste the shapes (Esc key cancel)

Selected shapes > Ctrl + X : cut the shapes

Selected shapes > G key : move the shapes (Esc key cancel)

Selected shapes > R key : rotate the shapes

Selected shapes > Rotating > Move mouse cursor : rotate (by 5 degree every step)

Selected shapes > Rotating > Left Click : confirm rotation

Selected shapes > Rotating > Input numbers, then R key : rotate by degree

Selected shapes > Rotating > Esc key : cancel

Selected shapes > T key : rotate the shapes by 90 degree

Selected shapes > B key : bevel the shapes

Selected shapes > I key : Inset/Outset the shapes. 
If it work on open-shape (not closed), it will convert lines into 
long rectangle shape.


Selected shapes (non-closed shape) > Ctrl + M key : Create symmetric on the opposite side. For creating non-closed shape, you can press spacebar key during drawing.

Selected shapes > E key : Enter edit mode of shape

Edit mode of shape > Click on the vertex of shape : Select the vertex point

Edit mode of shape > G key : Move the selected vertex points (click to confirm)

Edit mode of shape > B key : Bevel the selected vertex points (click to confirm, mouse scroll up and down to change number of bevel cut)

Edit mode of shape > DEL key : Delete the selected vertex points

Edit mode of shape > E key again / Esc key : Leave the edit mode



Selected shapes > Bevel tool > Mouse wheel scroll : change number of bevel cut

Selected shapes > Bevel tool > Left Click : Confirm

Selected shapes > D key : duplicate the shapes by array tool

Selected shapes > Array tool > Mouse wheel scroll : increase / decrease number 
of copies

Selected shapes > Array tool > Left Click : Confirm

Selected shapes > Array tool > C key : switch to Circular Array

Selected shapes > Array tool > Circular > Mouse wheel scroll : change number of 
copies

Selected shapes > X key : Change the pivot of selected shape (only first shape)

Selected shapes > Pivot change > Left click : confirm the new pivot point

Selected shapes > S key : resize the shapes

Selected shapes > M key and N key : flip the shapes horizontally or vertically



Mouse Wheel replacement :

If you do not have mouse wheel, you can press [ or ] key to act as mouse 
scrolling.

'''