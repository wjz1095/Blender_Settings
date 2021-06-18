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
from . import grid_modeler


use_exact = False


class Vert:
    def __init__(self, v1=None):
        if v1 != None:
            self.co = v1.co.copy()
        

class Edge:
    def __init__(self, e1=None):
        if e1 != None:
            self.verts = [Vert(e1.verts[0]), Vert(e1.verts[1])]            
            self.link_faces = [f1.select for f1 in e1.link_faces]        

    def calc_length(self):
        return (self.verts[1].co - self.verts[0].co).length

    
class Face:
    def __init__(self, f1=None):
        if f1 != None:
            self.edges = [Edge(e1) for e1 in f1.edges]
            self.verts = [Vert(v1) for v1 in f1.verts]
            self.normal = f1.normal.copy()
            self.center = f1.calc_center_median()        
        
    def calc_center_median(self):
        return self.center      


class Projection:
    def __init__(self):        
        self.current = None        
        self.face = None  

    def vert(self, v1):        
        v2 = Vert()
        v2.co = v1
        return v2

    def edge(self, pv1, pv2):
        e1 = Edge()
        e1.verts = [pv1, pv2]
        e1.link_faces = [True, False]
        return e1

    def vector(self, v1):
        return Vector(v1[0])


    def create_projection(self, cen, sn, ve1, ve2, ve3, ve4):
        pv1 = self.vert(ve1)
        pv2 = self.vert(ve2)
        pv3 = self.vert(ve3)
        pv4 = self.vert(ve4)        
        pe1 = self.edge(pv1, pv2)
        pe2 = self.edge(pv2, pv3)
        pe3 = self.edge(pv3, pv4)
        pe4 = self.edge(pv4, pv1)
        f1 = Face()
        f1.edges = [pe1, pe2, pe3, pe4]
        f1.verts = [pv1, pv2, pv3, pv4]
        f1.center = cen
        f1.normal = sn        
        self.face = f1



    def calc_edge(self, p1, p2, offset, normal):
        sn = normal
        sn.normalized()
        #off2 = sn * 0.1        
        mid = (p1 + p2)/2
        e2 = p2 - p1
        elen = e2.length        
        height = e2.cross(sn).normalized()

        h1 = mid + (height * elen /2)
        h2 = mid - (height * elen /2)
        ve1 = h2 + (p2-mid)
        ve2 = h1 + (p2-mid)
        ve3 = h1 + (p1-mid)
        ve4 = h2 + (p1-mid)
        self.create_projection(mid, sn, ve1, ve2, ve3, ve4)


    def calc_space(self, ax, quad, length):
        x, y, z = ax
        ve1, ve2, ve3, ve4 = quad
        cen = (ve1 + ve2 + ve3 + ve4)/4
        sn = z.normalized()
        self.create_projection(cen, sn, ve1, ve2, ve3, ve4)



    def get_orient(self, center, pos):        
        mat = Matrix.Identity(4)
        mat = Matrix.Translation(center * -1) @ mat
        pos2 = pos - center
        rot = Vector((0,0,1.0)).rotation_difference(pos2).to_matrix().to_4x4()
        mat = rot @ mat
        mat = Matrix.Translation(center) @ mat
        return mat, pos2.normalized()

        
        


def get_bm(context):
    obj = bpy.context.edit_object    
    me = obj.data    
    # Get a BMesh representation
    bm = bmesh.from_edit_mesh(me)    
    return bm


def same_direction(p1, p2):
    if p1.angle(p2) < 0.03:
        return True
    else:
        return False


def vs_center(vs):
    p = Vector()
    for v1 in vs:
        p += v1.co
    p /= len(vs)
    return p



def create_bevel(front, back, p2, dis, cut):
    e1 = (front-p2).normalized()
    e2 = (back-p2).normalized()
    vn = dis * ((e1+e2)/2).normalized()
    cir = p2 + vn
    pe1 = vn.project(e1)
    pe2 = vn.project(e2)        
    f1 = pe1 - vn
    f2 = pe2 - vn
    p4 = []
    p4.append(cir + f2)
    rot = f2.rotation_difference(f1)
    rot2 = Quaternion(rot.axis, rot.angle / cut)
    for i in range(cut):
        f2.rotate(rot2)                
        p4.append(cir + f2)
    return p4
    
def process_bevel2(p, line_only, dis, cut):
    ret = []
    if line_only:
        if len(p) < 2:
            return None
        firsta, firstb = p[0]
        lasta, lastb = p[-1]
        p2 = [a for (a, b) in p] + [lastb]
        pbevel = p2[1:-1]
        front = p2[2:]
        back = p2[:-2]
        p4 = []
        for ip, ifront, iback in zip(pbevel, front, back):
            ires = create_bevel(ifront, iback, ip, dis, cut)
            p4 += ires
        p4 = [firsta] + p4 + [lastb]                
        p5 = p4[1:] + [p4[0]]
        ret = [(a, b) for a, b in zip(p4, p5)]
        ret = ret[:-1]
    else:
        if len(p) < 3:
            return None
        p2 = [a for (a, b) in p]
        front = p2[1:] + [p2[0]]
        back = [p2[-1]] + p2[0:-1]
        p4 = []
        for ip, ifront, iback in zip(p2, front, back):
            ires = create_bevel(ifront.co, iback.co, ip.co, dis, cut)
        p4 += ires
        p5 = p4[1:] + [p4[0]]
        ret = [(a, b) for a, b in zip(p4, p5)]  
    return ret


def process_bevel(p, line_only, dis, cut):
    ret = []
    if line_only:
        if len(p) < 2:
            return None
        firsta = p[0]
        lastb = p[-1]
        p2 = p
        pbevel = p2[1:-1]
        front = p2[2:]
        back = p2[:-2]
        p4 = []
        for ip, ifront, iback in zip(pbevel, front, back):
            ires = create_bevel(ifront.co, iback.co, ip.co, dis, cut)
            p4 += ires
        p4 = [firsta.co] + p4 + [lastb.co]        
        ret = [grid_modeler.SPoint(a) for a in p4]
    else:
        if len(p) < 3:
            return None
        p2 = p
        front = p2[1:] + [p2[0]]
        back = [p2[-1]] + p2[0:-1]
        p4 = []
        for ip, ifront, iback in zip(p2, front, back):
            ires = create_bevel(ifront.co, iback.co, ip.co, dis, cut)
            p4 += ires        
        ret = [grid_modeler.SPoint(a) for a in p4]
    return ret


def bevel_vert(item, idx, dis, cut):    
    loop = item.loop
    total = len(loop)    
    backi = (idx - 1) % total
    fronti = (idx + 1) % total
    pb = loop[backi]
    a1 = loop[idx]    
    pf = loop[fronti]
    ires = create_bevel(pf.co, pb.co, a1.co, dis, cut)
    ires2 = [grid_modeler.SPoint(p) for p in ires]
    last = item.loop[-1]
    item.loop.pop(idx)
    item.loop[idx:idx] = ires2
    #res2 = ires[1:] + [ires[0]]
    #ins = [(a, b) for a, b in zip(ires, res2)]    
    #insert_points(ins, item.loop, idx)


def insert_points(ins, loop, idx):    
    total = len(loop)    
    backi = (idx - 1) % total
    fronti = (idx + 1) % total
    pb,_ = loop[backi]
    pf,_ = loop[fronti]
    ins[-1] = (ins[-1][0], pf.copy())
    loop[backi] = (pb, ins[0][0].copy())
    loop.pop(idx)
    loop[idx:idx] = ins



def create_edges(context, bm, loops):
    es = []
    for item in loops:
        loop = item.loop
        selected = item.select
        pos = [p1.co for p1 in loop]
        vs = []
        for p in pos:
            if p == None:
                continue
            v1 = bm.verts.new(p)
            vs.append(v1)            
        vs2 = vs[1:] + [vs[0]]
        pair1 = list(zip(vs, vs2))
        
        if item.line_only:
            pair1.pop()

        for v1, v2 in pair1:
            e1 = bm.edges.new((v1, v2))
            es.append(e1)
        
    bm.verts.index_update()
    bm.edges.index_update()
    bm.normal_update()
    bmesh.update_edit_mesh(context.edit_object.data)    
    return es



def create_face(context, bm, source, other, loops, viewer, merge):
    #self.source = self.get_tagged(context)
    source.select = False
    for f1 in other:
        f1.select = False

    fs = []
    for item in loops:
        loop = item.loop
        selected = item.select
        pos = [p1.co for p1 in loop]
        verts = []
        for p in pos:
            if p == None:
                continue
            v1 = bm.verts.new(p)
            verts.append(v1)
        bm.verts.index_update()
        f1 = bm.faces.new(verts)
        #f1.select = True
        f1.select = False            
        fs.append(f1)
    bm.faces.index_update()
    bm.normal_update()
    #bmesh.update_edit_mesh(context.edit_object.data, loop_triangles=True, destructive=True)         
    #bpy.ops.mesh.normals_make_consistent(inside=False)    

    for f1 in fs:
        #print(f1.normal, self.source.normal)
        if viewer == None:
            if same_direction(f1.normal, source.normal) == False:
                f1.select = True
        else:
            if f1.normal.angle(viewer) > (f1.normal * -1).angle(viewer):
                f1.select = True

    bm.select_flush(False)
    bm.select_flush(True)
    bpy.ops.mesh.flip_normals()

    for f1 in fs:
        f1.select = True

    bm.select_flush(True)
    bmesh.update_edit_mesh(context.edit_object.data)    

    if merge:
        bpy.ops.mesh.remove_doubles()

    return fs



def cut_face(context, bm, source, other, loops, dissolve, viewer, merge):
    #self.source = self.get_tagged(context)
    source2 = [source] + other

    #es = [e for e in self.source.edges]
    es = [e1 for f1 in source2 for e1 in f1.edges]
    es = [e1 for e1 in es if not all(f1.select for f1 in e1.link_faces)]
    fs = create_face(context, bm, source, other, loops, viewer, merge)

    bmesh.ops.delete(bm, geom=source2, context='FACES')
    #bmesh.update_edit_mesh(context.edit_object.data, loop_triangles=True, destructive=True)                
    #bmesh.update_edit_mesh(context.edit_object.data, loop_triangles=True, destructive=True)
    
    for f1 in fs:
        #es += f1.edges
        for e1 in f1.edges:
            if e1 not in es:
                es.append(e1)
    

    bmesh.ops.triangle_fill(bm, use_beauty=False, use_dissolve=dissolve, edges=es)
    
    #bmesh.ops.triangle_fill(bm, use_beauty=False, use_dissolve=True, edges=es)
    bmesh.update_edit_mesh(context.edit_object.data, loop_triangles=True, destructive=True)        

    for e1 in bm.edges:
        e1.select = False
    for f1 in fs:
        f1.select = True
    

def boolean_item(context, bm, f1, source, other, grid_len, propdepth, propoffset):
    # not need
    #bmesh.update_edit_mesh(context.edit_object.data, loop_triangles=True, destructive=True)        
    ext = bmesh.ops.extrude_face_region(bm, geom=[f1])
    verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)]

    depth = source.normal.normalized() * -1 * grid_len * propdepth
    bmesh.ops.translate(bm, vec=depth, verts=verts)

    f1.select = True
    #new
    bm.select_flush(False)
    bm.select_flush(True)
    bmesh.update_edit_mesh(context.edit_object.data)

    bpy.ops.mesh.select_linked()
    vs = [v1 for v1 in bm.verts if v1.select]
    scale = (propoffset / 5.0) + 1.0
    cen = vs_center(vs)
    for v1 in vs:
        v1.co -= cen
        v1.co *= scale
        v1.co += cen

    return [f1 for f1 in bm.faces if f1.select]



def boolean_cut(context, bm, source, other, loops, grid_len, propdepth, propoffset):
    source.select = False
    for f1 in other:
        f1.select = False    
    fsall = []    
    for item in loops:
        if item.line_only and len(item.loop) < 3:
            continue
        loop = item.loop
        selected = item.select
        pos = [p1.co for p1 in loop]
        verts = []
        for p in pos:
            if p == None:
                continue
            v1 = bm.verts.new(p)
            verts.append(v1)
        bm.verts.index_update()
        f1 = bm.faces.new(verts)
        #f1.select = True
        f1.select = False
        bm.faces.index_update()
        bm.normal_update()
        fs = boolean_item(context, bm, f1, source, other, grid_len, propdepth, propoffset)
        fsall += fs
        for f in bm.faces:
            f.select = False        

    for f in fsall:
        f.select = True

    '''
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bmesh.update_edit_mesh(context.edit_object.data, loop_triangles=True, destructive=True)        
    '''
    bm.select_flush(False)
    bm.select_flush(True)    
    bmesh.update_edit_mesh(context.edit_object.data, loop_triangles=True, destructive=True)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    

    if bpy.app.version >= (2, 91, 0):
        if use_exact:
            bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE', solver='EXACT')
        else:
            bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE', solver='FAST')
    else:
        bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE')


def boolslice(context, bm, source, other, loops, grid_len, propdepth, propoffset):        
    source.select = False
    for f1 in other:
        f1.select = False    
    fsall = []    
    for item in loops:
        loop = item.loop
        selected = item.select
        pos = [p1.co for p1 in loop]
        verts = []
        for p in pos:
            if p == None:
                continue
            v1 = bm.verts.new(p)
            verts.append(v1)
        bm.verts.index_update()
        f1 = bm.faces.new(verts)
        #f1.select = True
        f1.select = False
        bm.faces.index_update()
        bm.normal_update()
        fs = boolean_item(context, bm, f1, source, other, grid_len, propdepth, propoffset)
        fsall += fs
        for f in bm.faces:
            f.select = False        

    for f in fsall:
        f.select = True

    bm.select_flush(False)
    bm.select_flush(True)    
    bmesh.update_edit_mesh(context.edit_object.data, loop_triangles=True, destructive=True)
    bpy.ops.mesh.normals_make_consistent(inside=False)    
    #bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE')    

    bm2 = bm.copy()


    if bpy.app.version >= (2, 91, 0):    
        if use_exact:
            bpy.ops.mesh.intersect_boolean(operation='INTERSECT', solver='EXACT')
        else:
            bpy.ops.mesh.intersect_boolean(operation='INTERSECT', solver='FAST')
    else:    
        bpy.ops.mesh.intersect_boolean(operation='INTERSECT' )

    #bpy.ops.mesh.intersect_boolean(operation='INTERSECT')
    bpy.context.object.update_from_editmode()

    df = []
    df = [f1 for f1 in bm.faces if f1.hide]
    bmesh.ops.delete(bm, geom=df, context='FACES')
    df = [f1 for f1 in bm.edges if f1.hide]
    bmesh.ops.delete(bm, geom=df, context='EDGES')
    df = [f1 for f1 in bm.verts if f1.hide]
    bmesh.ops.delete(bm, geom=df, context='VERTS')

    bmesh.update_edit_mesh(context.edit_object.data)
    
    bm3 = bm.copy()

    bpy.ops.object.editmode_toggle()
    bm2.to_mesh(bpy.context.object.data)
    bpy.ops.object.editmode_toggle()    


    if bpy.app.version >= (2, 91, 0):     
        if use_exact:
            bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE', solver='EXACT')
        else:
            bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE', solver='FAST')
    else:    
        bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE' )

    #bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE')
    bpy.context.object.update_from_editmode()

    bm3.from_mesh(bpy.context.object.data)

    bpy.ops.object.editmode_toggle()
    bm3.to_mesh(bpy.context.object.data)
    bpy.ops.object.editmode_toggle()

    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    for f1 in bm.faces:
        f1.select_set(False)    
    bm.select_flush(False)
    bmesh.update_edit_mesh(bpy.context.object.data)

















































































