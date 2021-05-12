import bpy
import os

bl_info = {
	"name": "Anti-Seam",
	"category": "Node",
	"author": "Tim Crellin (Thatimst3r)",
	"blender": (2,81,0),
	"location": "Node Editor Toolbar",
	"description": "Make any image seamless",
	"warning": "",
	"wiki_url":"",
	"tracker_url": "https://www.thatimster.com/contact.html",
	"version":('1', '1')
}

class REMOVE_OT_antiseam(bpy.types.Operator):
	bl_idname = "remove.antiseam"
	bl_label = "Remove"
	bl_description = "Remove Anti-Seam from selected images"

	@classmethod
	def poll(cls, context):
		return cls.poll_helper(context)

	@classmethod
	def poll_helper(cls, context):
		valid = False
		if context.object and context.object.type == "MESH":
			has_mat = context.object.data.materials
			if len(has_mat) > 0:
				active_mat = has_mat[context.object.active_material_index]
				if active_mat.node_tree:
					iter_list = [list(active_mat.node_tree.nodes)]
					while iter_list:
						nodes = iter_list.pop()
						for check in nodes:
							if check.type == "GROUP" and check.select and check.node_tree.name.lower().startswith("anti-seam_"):
								valid = True
								break
							elif check.type == "GROUP" and check.select:
								iter_list.append(list(check.node_tree.nodes))
						if valid:
							break
		return valid

	def fetch_grps(self, context):
		traverse = []
		active_mat = context.object.data.materials[context.object.active_material_index]
		iter_list = [(active_mat.node_tree,list(active_mat.node_tree.nodes))]
		while iter_list:
			tree, nodes = iter_list.pop()
			for check in nodes:
				if check.type == "GROUP" and check.select and check.node_tree.name.lower().startswith("anti-seam_"):
					traverse.append((tree, check))
				elif check.type == "GROUP" and check.select:
					iter_list.append((check.node_tree, list(check.node_tree.nodes)))
		return traverse

	def execute(self, context):
		to_remove = self.fetch_grps(context)
		img_ref = None
		
		for tree, remove_group in to_remove:

			for node in remove_group.node_tree.nodes:
				if node.type == "TEX_IMAGE":
					img_ref = node
					break
			
			n_node = tree.nodes.new("ShaderNodeTexImage")
			n_node.image = img_ref.image
			n_node.interpolation = img_ref.interpolation
			n_node.projection = img_ref.projection
			n_node.projection_blend = img_ref.projection_blend

			if img_ref.image_user:
				n_node.image_user.frame_current = img_ref.image_user.frame_current
				n_node.image_user.frame_duration = img_ref.image_user.frame_duration
				n_node.image_user.frame_offset = img_ref.image_user.frame_offset
				n_node.image_user.frame_start = img_ref.image_user.frame_start
				n_node.image_user.tile = img_ref.image_user.tile
				n_node.image_user.use_auto_refresh = img_ref.image_user.use_auto_refresh
				n_node.image_user.use_cyclic = img_ref.image_user.use_cyclic
			
			if remove_group.inputs[0].links:
				prev = remove_group.inputs[0].links[0]
				tree.links.new(prev.from_node.outputs[prev.from_socket.name], n_node.inputs[0])
			if remove_group.outputs[0].links:
				next_node = remove_group.outputs[0].links[0]
				tree.links.new(next_node.to_node.inputs[next_node.to_socket.name], n_node.outputs[0])

			n_node.location = remove_group.location
			tree.nodes.remove(remove_group)

		for rm_grp in bpy.data.node_groups:
			if rm_grp.name.lower().startswith("anti-seam"):
				if rm_grp.users == 0:
					bpy.data.node_groups.remove(rm_grp)
		#2nd pass
		for rm_grp_2 in bpy.data.node_groups:
			if rm_grp_2.name.lower().startswith("anti-seam") or rm_grp_2.name.lower().startswith("sine blend"):
				if rm_grp_2.users == 0:
					bpy.data.node_groups.remove(rm_grp_2)

		return {"FINISHED"}

class ADD_OT_antiseam(bpy.types.Operator):
	bl_idname = 'add.antiseam'
	bl_description = 'Remove Seams'
	bl_category = 'Node'
	bl_label = 'Anti-Seam'

	@classmethod
	def poll(cls, context):
		return cls.poll_helper(context)
	
	@classmethod
	def poll_helper(cls, context):
		valid = False
		if context.object and context.object.type == "MESH":
			has_mat = context.object.data.materials
			if len(has_mat) > 0:
				active_mat = has_mat[context.object.active_material_index]
				if active_mat.node_tree:
					iter_list = [list(active_mat.node_tree.nodes)]
					while iter_list:
						nodes = iter_list.pop()
						for check in nodes:
							if check.type == "GROUP" and check.select and not check.node_tree.name.lower().startswith("anti-seam"):
								iter_list.append(list(check.node_tree.nodes))
							elif check.type == "TEX_IMAGE" and check.select and check.image:
								valid = True
								break
						if valid:
							break
		return valid

	def execute(self, context):
		mat_ref = {'Anti-Seam': ('Anti-seamexp', ['Group'])}
		select_mat_name = "Anti-Seam"
		select_mat = mat_ref[select_mat_name][0]
		file_loc= os.path.join(os.path.dirname(__file__), "data", "data.blend")
		if context.space_data.tree_type == "ShaderNodeTree" and context.space_data.shader_type == "OBJECT":
			active_mat = context.object.active_material
			current_nodes = active_mat.node_tree.nodes		
			select_images = [i for i in current_nodes if i.type=="TEX_IMAGE" and i.select]

			for selected in select_images:
				with bpy.data.libraries.load(file_loc) as (data_from, data_to):
					data_to.materials = [data_from.materials[data_from.materials.index(select_mat)]]
				
				target_tree = bpy.data.materials[select_mat] 
				target_nodes = [mn for mn in target_tree.node_tree.nodes if mn.name in mat_ref[select_mat_name][1]]
				for t in target_nodes:
					new_n = current_nodes.new(type=t.bl_idname)
					new_name = "Anti-Seam_" + selected.image.name

					new_n.location = selected.location
					new_n.width = 200
					t.node_tree.name = new_name
					new_n.node_tree = t.node_tree

					for n in new_n.node_tree.nodes:
						if n.label == "REF" and n.type == "TEX_IMAGE":
							n.image = selected.image
							n.interpolation = selected.interpolation
							n.projection = selected.projection
							n.projection_blend = selected.projection_blend
							if n.image_user:
								n.image_user.frame_current = selected.image_user.frame_current
								n.image_user.frame_duration = selected.image_user.frame_duration
								n.image_user.frame_offset = selected.image_user.frame_offset
								n.image_user.frame_start = selected.image_user.frame_start
								n.image_user.tile = selected.image_user.tile
								n.image_user.use_auto_refresh = selected.image_user.use_auto_refresh
								n.image_user.use_cyclic = selected.image_user.use_cyclic
					
					if selected.outputs[0].links:
						nt = active_mat.node_tree
						for l in selected.outputs[0].links:
							nt.links.new(new_n.outputs[0], l.to_node.inputs[l.to_socket.name])
					
					#sort out uv mapping
					img_coords = selected.inputs["Vector"].links
					if len(img_coords) == 0:
						tex_coords = [n for n in active_mat.node_tree.nodes if n.type == "TEX_COORD"]
						tex_coord = None
						if tex_coords:
							tex_coord = tex_coords[0]
						else:
							tex_coord = active_mat.node_tree.nodes.new(type="ShaderNodeTexCoord")
							tex_coord.location = (new_n.location.x-200, new_n.location.y-250)	
						active_mat.node_tree.links.new(tex_coord.outputs[2], new_n.inputs["Vector"])
					else:
						active_mat.node_tree.links.new(img_coords[0].from_node.outputs[img_coords[0].from_socket.name],new_n.inputs["Vector"])
					active_mat.node_tree.nodes.remove(selected)
						
				bpy.data.materials.remove(target_tree)
		return {"FINISHED"}

class OBJECT_PR_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        col = layout.column(align = True)
        row = col.row(align = True)
        row.scale_y = 1.5
        row.label(text=" ")
        row.operator(
                "wm.url_open", 
                text="YouTube Channel", 
                icon='TRIA_RIGHT',
        ).url = "https://www.youtube.com/channel/UCoMnKDkb9_v12qC_QMaZuSA"
        
        row.operator(
                "wm.url_open", 
                text="Support Me", 
                icon='SOLO_ON',
        ).url = "https://blendermarket.com/creators/thatimst3r"
        row.label(text=" ")
        row = layout.row()

class ANTISEAM_PT_panel(bpy.types.Panel):
	bl_space_type = 'NODE_EDITOR'
	bl_region_type = 'UI'
	bl_category = 'Texture-Tools'
	bl_label = 'Anti-Seam'

	@classmethod
	def poll(cls, context):
		if (context.space_data.tree_type == "ShaderNodeTree" and context.space_data.shader_type == "OBJECT"):
			return True
		else:
			return False

	def draw(self, context):
		layout = self.layout
		row = layout.row(align=True)
		if context.scene.render.engine not in ["CYCLES", "BLENDER_EEVEE"]:
			row.label(text="Only Cycles / Eevee supported")
		else:
			if context.space_data.tree_type == "ShaderNodeTree" and context.space_data.shader_type == "OBJECT":
				if not context.object:
					row.label(text="Select Object")
				elif not context.object.active_material:
					row.label(text="Add Material")
				elif not context.object.active_material.node_tree:
					row.label(text="Enable Nodes")
				else:
					row.scale_y = 1.5
					row.operator("add.antiseam", icon="MESH_GRID")
					row.operator("remove.antiseam", icon="X")


classes=(REMOVE_OT_antiseam,ADD_OT_antiseam,ANTISEAM_PT_panel,OBJECT_PR_preferences)
def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)
def unregister():
	from bpy.utils import unregister_class
	for cls in classes:
		unregister_class(cls)
