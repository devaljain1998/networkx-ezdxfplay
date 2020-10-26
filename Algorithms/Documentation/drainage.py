"""
drainage.py
====================================

This Module includes functions to draw drainage drawings.


Packages used:
1. ezdxf
2. networkx
3. math

Global variables
1. _dwg : the auto cad file read through ezdxf
2. _msp : modelspace created on the autocad file
3. _joints_dwg: auto cad file of joints block


To Do:
Add arrows (done only blocks not placed)
Layers and colors (done for joints and connection)
different depth place block (done but not tested)
side trim implementation (done)

"""

import ezdxf
from ezdxf.addons import Importer
from ezdxf.lldxf.const import DXFTableEntryError
import networkx as nx
import math
from pillarplus.blocks import place_block_at_location
import pillarplus.math
from pillarplus.data import create_size_mapping_dict
import pillarplus.boq.drainage_boq as boq
from texting import add_text_to_chamber,add_text_to_connection,add_text_to_location
_dwg = None
_msp = None
_joints_dwg = None

# stores static data of boq


def set_msp(file_name):
	"""
	create the msp and dwg global objects used by functions from the file passed in as parameter

	Parameters:
	file_name (string): the name of the file from which msp should be created
	"""
	global _msp, _dwg
	_dwg = ezdxf.readfile(file_name)
	_msp = _dwg.modelspace()

def create_hash(type, number):
	"""
	returns hash values for nodes of the graph
	"""
	if type == 'Entity':
		return 'E'+str(number)
	elif type == 'Joint':
		return 'J'+str(number)
	else:
		return str(number)

def create_graph(connections, joints_dict, entities_dict=None):
	"""
	Creates a undirected graph from connections and joints/etites read from json. Store there properties as atrributes in dictionary of nodes and connections

	Parameters:
	connection - JSON fromat connections
	joints_dict - joints dictionary with key as joint_number and value as JSON joints
	entities_dict - joints dictionary with key as entity_number and value as JSON entities

	Returns:
	networkx directed graph of connections and joints

	Dependencies:
	uses create hash function to make hashable nodes as they can be of either joints or entities type

	"""
	graph = nx.Graph()
	for connection in connections:
		source_number = connection['source_number']
		target_number = connection['target_number']
		source_type = connection['source_type']
		target_type = connection['target_type']
		source_dict = entities_dict[source_number] if source_type=='Entity' else joints_dict[source_number]
		target_dict = entities_dict[target_number] if target_type=='Entity' else joints_dict[target_number]

		graph.add_node(create_hash(source_type,source_number), **source_dict)
		graph.add_node(create_hash(target_type,target_number), **target_dict)
		graph.add_edge(create_hash(source_type,source_number), create_hash(target_type,target_number), **connection)

	return graph

def to_directed_dfs(graph,head,visited,directed_graph,reverse):
	if visited[head]!=0:
		return None
	visited[head]=1
	for i in graph.adj[head]:
		j=to_directed_dfs(graph,i,visited,directed_graph,reverse)
		if j!=None:
			directed_graph.add_node(head,**graph.nodes[head])
			directed_graph.add_node(j,**graph.nodes[j])
			if reverse:
				directed_graph.add_edge(j,head,**graph[j][head])
			else:
				directed_graph.add_edge(head,j,**graph[j][head])
	return head

def get_directed_graph(graph,priority_list,reverse=False):
	'''
    Take a directed graph and list from which directioin should start or end depending on reverse true or false respectively.

	Return: networkx.DiGraph

	Dependencies: to_directed_dfs in this module
	'''
	visited = {}
	directed_graph = nx.DiGraph()
	for i in graph.nodes:
		visited[i] = visited.get(i,0)
		
	for priority_list_item in priority_list:
		for i in graph.nodes:
			if graph.nodes[i]['type'] == priority_list_item and visited[i]==0:
				to_directed_dfs(graph,i,visited,directed_graph,reverse)
			
	for i in graph.nodes:
		if visited[i] == 0:
			to_directed_dfs(graph,i,visited,directed_graph,reverse)

	return directed_graph

def find_text_rotatioin(p1,p2):
	'''
	find the angle for text to rotate

	Parameters: takes two points (location) (list or tuple)
	
	Return: angle in degrees

	Dependencies: find_rotation function in pillarplus.math
	'''
	rotation = pillarplus.math.find_rotation(p1,p2)
	if (abs(rotation)>90):
		rotation += 180
	return rotation

def get_room_wall_id(location, walls_dict, units_conversion_factor):
    """
    Returns id of the associated room and wall

    Parameters:
                    location ((x,y,z)): Location of block target point in msp,
                    walls_dict (dict): key contains wall id, value contains wall dictionary
                    units_conversion_factor

    Returns:
                    room_id: Associated Room number
                    wall_id: Associated Wall number            
    """
    wall_dist_dict = {}
    for wall_id, wall in walls_dict.items():
        corners = wall['corners']
        # Find perpendicular point and lies on it
        per_point = pillarplus.math.find_perpendicular_point(location, corners[0], corners[1])

        if pillarplus.math.is_between(per_point, corners[0], corners[1]):
            dist = pillarplus.math.find_distance(location, per_point)
            wall_dist_dict[dist] = wall

    if len(wall_dist_dict.keys()) == 0:
        return None,None
    min_dist = min(wall_dist_dict.keys())
    if (min_dist > 1800*units_conversion_factor):
        return None,None
    wall = wall_dist_dict[min_dist]

    wall_id = wall['number']
    room_id = wall['room_number']

    return room_id, wall_id

def find_angle(p1,p2,p3):
	'''
	find the angle at p2 formed by p1 and p3

	Return: angle p1 p2 p3 in radians ranges from (0 to 2 pi)

	Dependencies: math
	
	Also note that angle is anti clock starting from edge p1,p2 to p2,p3 e.g.
	p1 = (0,-1);
	p2 = (0,0);
	p3 = (-2,0);
	gives angle = 4.7123 = 2/3 * pi = 270(degree)
	'''

	angle1 = math.atan2(p3[1]-p2[1], p3[0]-p2[0])
	angle2 = math.atan2(p1[1]-p2[1], p1[0]-p2[0])
	angle = angle1 - angle2

	if (angle < 0):
		angle += 2 * math.pi

	return angle


def update_graph_properties(graph,size_mapping_dict,units_conversion_factor):                                         # specific to drainage
	""" 
	updates the properties if the graph (stored as attribs of nodes/connections) nodes and connections like, size, joint type, rotation, mirror etc.

	Parameter:
	graph - networkx DiGraph (created by create graph function in this module)
	size_mapping_dict - key:current unit sizes, value: mm sizes


	Returns:
	updated networkx DiGraph

	Dependencies:
	pillarplus.math
	find_angle function in this module
	"""

	for source_node, target_node, connection in graph.edges(data=True):
		source = graph.nodes[source_node]
		target = graph.nodes[target_node]

		if graph.out_degree(target_node) == 0: # target is leaf node
			#Mostly Entity in drainage but if not entity
			if target_node[0] == 'J':
				target['rotation'] = pillarplus.math.find_rotation(source['location'],target['location'])
				if target['size'] == None:
					target['size'] = connection['size']
				if target['type'] == None:
					print('Type not given where required!')
					target['type']='COP Ceiling'
				
		
		# print(source,target,'------------------------')
		source['rotation'] = pillarplus.math.find_rotation(source['location'],target['location'])
		
		if source_node[0] == 'J':
			if source['size'] == None:
				source['size'] = connection['size']                                                             # --:WARNING:-- (ensures size is not None)
		if graph.in_degree(source_node) == 0:
			if source['type'] == None:
				print('Type not given where required!')
				source['type'] = 'COP Ceiling'
		if 0<graph.in_degree(source_node)<3:	                                                                # handle this earlier while making graph
			parent_nodes = list(graph.predecessors(source_node))
			if len(parent_nodes) == 1:
				parent_node = parent_nodes[0]
				parent = graph.nodes[parent_node]
				if source['type'] == None:
					#Bend(90) or Shoe or  Coupler
					in_angle = find_angle(parent['location'], source['location'], target['location'])
					if math.pi/2 - 0.1 < in_angle < math.pi/2 + 0.1 or 3*math.pi/2 - 0.1 < in_angle < 3*math.pi/2 + 0.1:
						source['type'] = 'Bend(90)'
					elif math.pi - 0.1 < in_angle < math.pi + 0.1:
						source['type'] = 'Coupler'
					else:
						source['type'] = 'Shoe'

			elif len(parent_nodes) == 2:
				parent_location_1 = graph.nodes[parent_nodes[0]]['location']
				parent_location_2 = graph.nodes[parent_nodes[1]]['location']
				# decide parent node, equals to non-180 degree node
				if math.pi - 0.1 < find_angle(parent_location_1,source['location'],target['location']) < math.pi + 0.1:
					parent_node = parent_nodes[1]
					parent = graph.nodes[parent_node]
				else:
					parent_node = parent_nodes[0]
					parent = graph.nodes[parent_node]

				in_angle = find_angle(parent['location'],source['location'],target['location']) #always from perpendicular(or 45 degree/non 180 degree) parent

				in_size = graph[parent_node][source_node]['size']
				out_size = graph[source_node][target_node]['size']
				reducer = None
				if in_size!=out_size:
					in_str_mm = str(size_mapping_dict[in_size])
					out_str_mm = str(size_mapping_dict[out_size])
					reducer = ' reducer ' + out_str_mm + '-' + in_str_mm
					#reducer = ' reducer ' + str(out_size) + '-' + str(in_size)

	
				if graph[parent_node][source_node]['depth']!=graph[source_node][target_node]['depth']:
					#at different depth
					if source['type'] == None:
						#source type will be default to Ytee up
						source['type'] = 'Ytee up'
					else:
						#check source type and then give ytee up/ swept t up
						if source['type'] == 'Ytee':
							source['type'] = 'Ytee up'
						if source['type'] == 'Swept tee':
							source['type'] = 'Tee up'
				else:
					#at same depth
					if source['type'] == None:
						if  math.pi/2 - 0.1 < in_angle < math.pi/2 + 0.1 or 3*math.pi/2 - 0.1 < in_angle < 3*math.pi/2 + 0.1:
							source['type'] = 'Swept tee'
						else:
							source['type'] = 'Ytee'

					if reducer != None and source['type'] in ['Swept tee','Ytee','Single tee']: # only these joints can have reducers
						source['type'] += reducer
						source['size'] = 75 * units_conversion_factor # as scaling of joint will not be needed if a reducer joint

			# mirror type need not to to be decided for some joints (find a better approah for this)
			if (source['type'] != 'Coupler') and 'trap' not in source['type'] and source['type'] !='wb back' and 'up'!=source['type'][-2:]:	#--:WARNING:-- (bad code)
				source['mirror'] = not pillarplus.math.is_inverted(source['location'], parent['location'], target['location']) # 'not' will come due to drainage are opposite then others


		if graph.in_degree(source_node) == 3:
			if (source['type']==None):
				parent_nodes = list(graph.predecessors(source_node))
				parent_location_1 = graph.nodes[parent_nodes[0]]['location']
				parent_location_2 = graph.nodes[parent_nodes[1]]['location']
				parent_location_3 = graph.nodes[parent_nodes[2]]['location']
				#Double Y tee / Cross tee
				in_angle_1 = find_angle(parent_location_1,source['location'],target['location'])
				in_angle_2 = find_angle(parent_location_2,source['location'],target['location'])
				in_angle_3 = find_angle(parent_location_3,source['location'],target['location'])
				if math.pi/2 - 0.1 < in_angle_1 < math.pi/2 + 0.1 or math.pi/2 - 0.1 < in_angle_2 < math.pi/2 +0.1 or math.pi/2 - 0.1 < in_angle_3 < math.pi/2 +0.1:
					source['type'] = 'Cross tee'
				else :
					source['type'] = 'Double Y tee'
	return graph

def place_arrows(start_point,end_point,arrow_block,layer_name,conversion_factor, width):
	'''
	place_blocks in msp between start_point and end_point, number of arrows decided automatically using
	a const dict named 'arrows_from_distance' 

	Parameter:
	start_point - list or tuple of point
	end_point - list or tuple of point
	arrow_block - joint_default of arrow
	layer_name - string value of layer name to which arrows are added
	conversion_factor

	Dependencies:
	pillarplus.math
	find_angle function in this module
	place_block_atl_location function in pillarplus.blocks
	'''
	global _msp
	global _dwg
	global _joints_dwg
	arrows_from_distance = [600, 1000, 3000]
	distance = pillarplus.math.find_distance(start_point,end_point) / conversion_factor
	if distance < arrows_from_distance[0]:
		arrows_number = 0
	elif distance < arrows_from_distance[1]:
		arrows_number = 1
	elif distance < arrows_from_distance[2]:
		arrows_number = 2
	else:
		arrows_number = 3

	if (arrow_block == None):
		return

	# importing the block
	importer = Importer(_joints_dwg, _dwg)
	importer.import_block(arrow_block['block_name'])
	importer.finalize()
	# getting the angle of the pipe
	rotation = pillarplus.math.find_rotation(start_point, end_point)
	offset = arrow_block['center']
	block_name = arrow_block['block_name']
	scale_factor = width/75

	# placing the block
	if arrows_number==1 or arrows_number==3:
		#place in center
		mid_point = pillarplus.math.find_mid_point(start_point, end_point)
		place_block_at_location(block_name, mid_point, scale_factor, rotation,
							offset, layer_name, _msp)

	if arrows_number==2 or arrows_number==3:
		#place at ends
		shift = 250 * conversion_factor															#--:WARNING:-- (hcv)
		first_point = pillarplus.math.find_directed_point(start_point,end_point,shift)
		second_point = pillarplus.math.find_directed_point(end_point,start_point,shift)
		place_block_at_location(block_name, first_point, scale_factor, rotation,
							offset, layer_name, _msp)
		place_block_at_location(block_name, second_point, scale_factor, rotation,
							offset, layer_name, _msp)

def draw_double_lined_pipes(start_point,end_point,pipe_size,layer_name, conversion_factor):							

	global _msp
	angle = pillarplus.math.find_perpendicular_slope_angle(start_point,end_point)
	s1,s2 = pillarplus.math.directed_points_on_line(start_point,angle,pipe_size/2)
	e1,e2 = pillarplus.math.directed_points_on_line(end_point,angle,pipe_size/2)

	# draw pipe boundaries
	_msp.add_line(s1, e1, dxfattribs={'layer': layer_name})
	_msp.add_line(s2, e2, dxfattribs={'layer': layer_name})

def create_layers() :
	global _dwg

	LAYERS = [{																								#--: WARNING :-- (hcv)
	'name' : 'PP-SWP',
	'color' : 'red',
	'linetype' : 'SOLID'
	},
	{
	'name' : 'PP-WWP',
	'color' : 'green',
	'linetype' : 'SOLID'
	},
	{
	'name' : 'PP-RWP',
	'color' : 'blue',
	'linetype' : 'SOLID'
	},
	{
	'name' : 'PP-VENT',
	'color' : 'brown',
	'linetype' : 'SOLID'
	},
	{
	'name' : 'DEFAULT',
	'color' : 'cyan',
	'linetype' : 'SOLID'
	}
	]
	COLORS = {																							#--: WARNING :-- (hcv)
		"red": 1,
		"yellow": 2,
		"green": 3,
		"blue": 5,
		"magenta": 210,
		"cyan": 4,
		"grey": 8,
		"white": 7,
		"black": 0,
		"brown": 28
	}
	layers_created = []

	for layer in LAYERS:
		try:
			_dwg.layers.new(name=layer['name'], dxfattribs={'linetype': layer['linetype'], 'color': COLORS[layer['color']]})
		except DXFTableEntryError as e:
			print(e)
		layers_created.append(layer['name'])
	return layers_created

def draw_leader(start_point,angle,distance):
	global _msp
	leader_start_point = start_point
	leader_mid_point = pillarplus.math.directed_points_on_line(start_point,angle*math.pi/180,distance)[0]
	if (abs(angle)>90):
		distance *= -1
	leader_end_point = (leader_mid_point[0]+distance,leader_mid_point[1])
	_msp.add_leader([ leader_start_point, leader_mid_point, leader_end_point])
	return leader_end_point
	

def draw_connections(graph, joints_defaults, walls_dict, params):
	""" 
	draw in _msp using the graph provided all its pproperties are given correctly. Uses joints_defalus to place the block imported from _joints_dwg.

	Parameter:
	graph - networkx DiGraph (created by create graph function in this module)
	joints_defaults - dictinary with value as JSON joints_defaults and key is made up of type and mirror properties

	Returns:
	string - "success" if done propertly else err_str

	Dependencies:
	pillarplus.math
	draw_double_lined_pipes function in this module
	place_block_at_location from pillarplus.blocks
	"""
	global _msp
	global _dwg
	global _joints_dwg
	layers = create_layers()
	try:
		key = 'arrow' # display name arrow joint 													# --:WARNING:-- (hcv)
		arrow_block = joints_defaults[key]
	except KeyError:
		print('Arrow joint not found')
		arrow_block = None
	conversion_factor = params['Units conversion factor']
	for source_node,target_node,connection in graph.edges(data=True):
		#CREATE USEFUL VARIABLES
		source = graph.nodes[source_node]
		target = graph.nodes[target_node]
		layer_name = 'PP-' + connection['type']
		# print(source,target,'------------------------')
		if 'size' in source.keys():
			scale_factor = source['size']/75 	# conversion not required (input already converted)
		else:
			scale_factor = conversion_factor
		if layer_name not in layers:
			print('layer not created for pipe type : ' + layer_name + '... Default given! ')
			layer_name = "DEFAULT"

		# PLACE JOINT AND GET START TRIM ( the out trim of a joint)
		if source_node[0] == 'J':
			try:
				key = source['type'] + str(' mirror' if source['mirror'] else '')
				joint_default = joints_defaults[key]
			except KeyError:
				print('key not found in joints_defaults_dict (for source) - ' + key + 'source no: '+ source_node)
				joint_default = joints_defaults['Cross tee']

			outtrim = joint_default['outtrim']
			block_name = joint_default['block_name']
			_type = joint_default['type']

			#place joint
			importer = Importer(_joints_dwg, _dwg)
			importer.import_block(block_name)
			importer.finalize()
			location = source['location']
			rotation = source['rotation']

			place_block_at_location(block_name, location, scale_factor , rotation,
									joint_default['center'], layer_name, _msp)


		else:
			outtrim = 0

		if outtrim == None:
			outtrim = 0
		start_trim = outtrim * scale_factor



		# GET END TRIM (from target's intrim)
		if target_node[0] == 'J':
			try:
				target_node_key = target['type'] + str(' mirror' if target['mirror'] else '')
				joint_default_target = joints_defaults[target_node_key]
			except KeyError :
				print('key not found in joints_defaults_dict (for target\'s end trim) - ' + target_node_key + 'target no: '+ target_node)
				joint_default_target = joints_defaults['Cross tee']
			intrim = joint_default_target['intrim'] if joint_default_target['intrim']!=None else 0
			end_trim = intrim * target['size']/75

			child_node = list(graph.successors(target_node))
			if len(child_node)>0 and graph.in_degree(target_node)>1:
				#end trim can be side trim
				child = graph.nodes[child_node[0]]
				angle = find_angle(source['location'],target['location'],child['location']) 
				if (math.pi - 0.1 < angle < math.pi + 0.1):
					pass
				else :
					# print(angle,'---',source['location'],'$$',target['location'],'##',child['location'])
					if joint_default_target['sidetrim']!= None:
						end_trim = joint_default_target['sidetrim'] * target['size']/75
					else:
						print('side trim not given for ' + joint_default_target['type'])
					pass
					#side trim is not required
		else:
			end_trim = 0

		# DRAW TRAPS
		if 'trap' in source.keys() and source['trap'] != None:
			try:
				key = source['trap']
				joint_default = joints_defaults[key]
			except KeyError:
				print('key not found in joints_defaults_dict (for trap) - ' + key + ' source no: '+ source_node)
				joint_default = joints_defaults['Cross tee']

			block_name = joint_default['block_name']

			#place joint
			importer = Importer(_joints_dwg, _dwg)
			importer.import_block(block_name)
			importer.finalize()
			location = source['location']
			rotation = pillarplus.math.find_rotation(source['location'],target['location'])
			size = connection['size']/75

			place_block_at_location(block_name, location, size , rotation,
									joint_default['center'], layer_name, _msp)

			# updating start trim
			start_trim = joint_default['outtrim'] * scale_factor

			# Add gratting to traps
			try:
				grating_joint = joints_defaults['SS grating']
			except KeyError:
				print('Grating joint not found!!')
				grating_joint = None

			if grating_joint != None and source['trap']!='bottle trap':
				# find the room rotation
				wall_id = get_room_wall_id(source['location'], walls_dict, conversion_factor)[1]

				if wall_id != None:
					wall_rotation = walls_dict[wall_id]['in_angle']
				else:
					print('wall not found a grating joint - '+ source_node)
					wall_rotation = 0
				importer = Importer(_joints_dwg, _dwg)
				importer.import_block(grating_joint['block_name'])
				importer.finalize()
				place_block_at_location(grating_joint['block_name'], source['location'], size, 
										wall_rotation, grating_joint['center'], layer_name, _msp)
				
			# TRAP TEXTING
			rotation = pillarplus.math.find_rotation(target['location'],source['location'])
			text = joint_default['short_name']
			if text == None:
				text = 'None'
			location = source['location']
			displacement = 180 * conversion_factor
			add_text_to_location(location, text, rotation, displacement, params, _msp, layer_name)
		
		# COP TEXTING
		if 'COP' in source['type']:
			rotation = pillarplus.math.find_rotation(target['location'],source['location'])
			text = source['display_name']
			if text == None:
				text = 'None'
			location = source['location']
			if source['size']== None:
				print('hey there')
			displacement = 180 * conversion_factor
			add_text_to_location(location, text, rotation, displacement, params, _msp, layer_name)

		# DRAW CONNECTION
		start_connection = pillarplus.math.find_directed_point(source['location'],target['location'], start_trim)
		end_connection = pillarplus.math.find_directed_point(target['location'], source['location'], end_trim)
		

		pipe_length = pillarplus.math.find_distance(start_connection, end_connection)
		connection['pipe_length'] = pipe_length/conversion_factor * 1000 # in meter always for boq
		draw_double_lined_pipes(start_connection, end_connection, connection['size'], layer_name, conversion_factor)	
		#placing arrows
		place_arrows(start_connection, end_connection, arrow_block, layer_name, conversion_factor, connection['size'])

		# ADDING TEXT FOR PIPE
		add_text_to_connection(connection, start_connection, end_connection, params, _msp, layer_name)
		# TEXT_HEIGHT = 30 * conversion_factor
		# distance = pillarplus.math.find_distance(source['location'],target['location'])
		# pipe_text = connection['text']
		# pipe_text_location = pillarplus.math.find_directed_point(source['location'],target['location'],distance/2)
		# if pipe_text != None:
		# 	if pipe_text != '//':
		# 		pipe_rotation = find_text_rotatioin(start_connection,end_connection)
		# 		leader_flag = 0
		# 		#add leader if required
		# 		if pipe_length < 500 * conversion_factor:												#--:WARNING:-- (HCV)
		# 			#draw ledger and add text 
		# 			angle = 135																			#--:WARNING:-- (HCV)
		# 			dist = 200 * conversion_factor														#--:WARNING:-- (HCV)
		# 			pipe_text_location = draw_leader(pipe_text_location,angle,dist)
		# 			leader_flag = 1
		# 		# adding text
		# 		if leader_flag:
		# 			pipe_rotation = 0
		# 		_msp.add_text(pipe_text,
		# 						dxfattribs={'height': TEXT_HEIGHT, 'layer':layer_name, 'rotation':pipe_rotation}).set_pos(
		# 							pipe_text_location,align='MIDDLE_CENTER')				# --:WARNING:-- (hcv - text height)
		# else:
		# 	print("pipe text is None for connection no. "+ str(connection['number']))
		



		# PLACE THE LEAF TARGET IF ITS A JOINT
		if graph.out_degree(target_node)==0 and target_node[0]=='J':									#--:WARNING:-- (ensure 'type' is defined in graph)
			try:
				key = target['type'] + str(' mirror' if target['mirror'] else '')
				joint_default = joints_defaults[key]
			except KeyError:
				print('key not found in joints_defaults_dict (for target) - ' + key + 'target no: '+ target_node)
				continue

			scale_factor = target['size']/75
			#place joint 
			block_name = joint_default['block_name']
			if block_name is None:
				print('block name is none for ' + joint_default['type'])
				continue
			importer = Importer(_joints_dwg, _dwg)
			importer.import_block(block_name)
			importer.finalize()
			location = target['location']
			rotation = target['rotation']

			place_block_at_location(block_name, location, scale_factor, rotation,
									joint_default['center'], layer_name, _msp)
					
	return 'success'

def draw_entities_data(entities,params,**props):
	global _msp
	global _dwg
	global _joints_dwg

	conversion_factor = params['Units conversion factor']
	conversion_factor
	for entity in entities.values():
		# Add text to chamber
		if 'chamber' in entity['type']:
			try:
				add_text_to_chamber(_msp, entity, params, layer_name='Text Layer')
				pass
			except Exception as e:
				return "Error while adding text to chamber :-" + str(e)

		
	return 'success'

def draw_sleeves(joints,sleeve_joint,conversion_factor):
	global _msp
	global _dwg
	global _joints_dwg
	importer = Importer(_joints_dwg, _dwg)
	importer.import_block(sleeve_joint['block_name'])
	importer.finalize()
	for joint in joints.values():
		if joint['type'] == 'sleeve':
			if joint['size'] != None:
				size = joint['size']/75
			else:
				size = conversion_factor
			if joint['rotation'] != None:
				rotation = joint['rotation']
			else:
				rotation = 0
			place_block_at_location(sleeve_joint['block_name'], joint['location'], 
									size, rotation, sleeve_joint['center'], 'sleeves_layer', _msp)



def save_dwg(file_name):
	"""
	save the autocad file in the current directory with the file name given

	Parameters:
	file_name (string): the name of the file with which dwg should be saved
	"""
	global _dwg
	_dwg.saveas(file_name)


if __name__ == '__main__':
	import json
	import os
	import csv

	this_dir = os.path.dirname(__file__)

	if this_dir != '':
		this_dir += '/'

	# Read parameters.csv (Generally common for most projects)
	try:
		params_dict = {}
		with open(this_dir + 'parameters.csv') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			line_count = 0
			for row in csv_reader:
				if line_count == 0:
					# print(f'Column names are {", ".join(row)}')
					line_count += 1
				else:
					value = row[1].strip()
					# print(f'{row[0]} is {value}')
					if value.isnumeric():
						value = float(value)
					elif value.lower() == 'yes':
						value = True
					elif value.lower() == 'no':
						value = False
					params_dict[row[0].strip()] = value
					line_count += 1
			# print(f'Processed {line_count} lines.')
	except FileNotFoundError:
		print(f'Parameters file "parameters.csv" is missing')
		exit()

	_joints_dwg = ezdxf.readfile(this_dir + 'setup/' + 'joints.dxf')  # joints dxf

	# FILE READING
	autocad_file = this_dir + params_dict['ProjectFolder'] + 'updated_in.dxf'
	set_msp(autocad_file)


	with open(this_dir + params_dict['ProjectFolder'] + 'updated_identification.json') as json_file:
		data = json.load(json_file)

	joints_dict = {}
	for joint in data['joints']:
		if joint['service'] == 'drainage':
			joints_dict[joint['number']] = joint


	entities_dict = {}
	for entity in data['entities']:
		if entity['service'] == 'drainage':
			entities_dict[entity['number']] = entity


	
	connections = []

	for connection in data['connections']:
		if connection['service'] == 'drainage':
			connections.append(connection)

	conversion_factor = data['params']['Units conversion factor']

	#SIZE MAPPING CREATION
	current_unit = data['params']['Units']
	sizes_dict = data['sizes']['drainage']
	size_mapping_dict = create_size_mapping_dict(sizes_dict,current_unit)

	# CREATING AND UPDATING GRAPH
	graph = create_graph(connections, joints_dict, entities_dict)

	priority_list = ["gt back","ic back","soil pipe","rain pipe","waste pipe","Bend(90)","wb back","urinal back","wc back"]

	graph = get_directed_graph(graph,priority_list,reverse=True)#reverse true only for drainage

	graph = update_graph_properties(graph,size_mapping_dict,conversion_factor)


	# from json joints_defaut ---- key: display name, value: joint_default dict
	services_included = ['drainage','draw','trap','all']
	joints_defaults_dict = {}
	for joint_default in data['joint_defaults']:
		if joint_default['service'] in services_included:
			key = joint_default['type'] + str(' mirror' if joint_default['mirror'] else '')
			joints_defaults_dict[key] = joint_default

	# print(joints_defaults_dict,'dddd');
	walls_dict = {}
	for wall in data['walls']:
		walls_dict[wall['number']] = wall

	result = draw_connections(graph,joints_defaults_dict,walls_dict,data['params'])
	if result != 'success':
		result += '\nError in drawing connection graph'
		print(result)


	# draw entities extra data
	result = draw_entities_data(entities_dict,data['params'],grating_joint=joints_defaults_dict['SS grating'])
	if result != 'success':
		result += '\nError in drawing entities data'
		print(result)

	# draw sleeve joints
	if 'sleeve' in joints_defaults_dict.keys():
		sleeve_joint = joints_defaults_dict['sleeve']
		draw_sleeves(joints_dict,sleeve_joint,conversion_factor)
	else:
		print('sleeves not drawn')

	save_dwg(this_dir + params_dict['ProjectFolder'] + 'drainage output.dxf')


	#calculate boq
	boq_data = boq.calculate_boq(graph,entities_dict)
	#save boq json
	drainage_boq_json = json.dumps(boq_data)
	f = open(this_dir + params_dict['ProjectFolder'] + "drainage_boq_json.json",'w')
	f.write(drainage_boq_json)
	f.close()
