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
import networkx as nx
import math
from pillarplus.blocks import place_block_at_location
import pillarplus.math
from pillarplus.data import *
import drainage_boq as boq
_dwg = None
_msp = None
_joints_dwg = None

# stores static data of boq


def place_arrow(start_point, angle, arrow_block, frequency, required_gap, layer_name):
	"""
	Draws places the arrows in appropriate point and returns the starting point of the next
	segment

	Takes start point of a segment of the pipe, angle of pipe, arrow block, total number of arrows
	left to be made and the required spacing between each arrow as parameter, calculates the location
	of the arrow in the pipe and places the block. The fucntion works in the
	following manner,
	if there are 3 arrows to be made,
	The functions assumes 4 sections as
	----------------------------------
			||		||		||		||
	----------------------------------
	and places a pointer in the end of each segment till all the pointers are placed

	Parameters:
		start_point (tuple): staring point of the segment of the pipe
		angle (float): angle of inclination of the pipe in degrees
		arrow_block (json branch): branch having the information of the pointer block
		required_gap (float): gap of each segment of the pipe

	Returns:
		---------if all the pointers are not placed----------
		tuple: starting point of the next segment
		---------if all the pointers are placed---------
		string: success
	"""
	if frequency <= 0:
		return 'success'
	# getting the end point of the segment
	end = start_point[0] + math.cos(math.radians(angle))*required_gap, start_point[1] + math.sin(math.radians(angle))*required_gap
	_msp.add_circle(end, 10, dxfattribs={'color': 2})
	offset = arrow_block['center']
	rotation = angle
	block_name = arrow_block['block_name']
	place_block_at_location(block_name, end, 1, rotation,
							offset, layer_name, _msp)
	place_arrow(end, angle, arrow_block, frequency-1, required_gap, layer_name)


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
	Creates a directed graph from connections and joints/etites read from json. Store there properties as atrributes in dictionary of nodes and connections

	Parameters:
	connection - JSON fromat connections
	joints_dict - joints dictionary with key as joint_number and value as JSON joints
	entities_dict - joints dictionary with key as entity_number and value as JSON entities

	Returns:
	networkx directed graph of connections and joints

	Dependencies:
	uses create hash function to make hashable nodes as they can be of either joints or entities type

	"""
	graph = nx.DiGraph()
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

def update_graph_properties(graph):                                         # specific to drainage
	""" 
	updates the properties if the graph (stored as attribs of nodes/connections) nodes and connections like, size, joint type, rotation, mirror etc.

	Parameter:
	graph - networkx DiGraph (created by create graph function in this module)

	Returns:
	updated networkx DiGraph

	Dependencies:
	pillarplus.math
	find_angle function in this module
	"""

	for source_node, target_node, connection in graph.edges(data=True):
		try:
			source = graph.nodes[source_node]
			target = graph.nodes[target_node]

			if graph.out_degree(target_node) == 0: # target is leaf node
				#Mostly Entity in drainage but if not entity
				if target_node[0] == 'J':
					target['rotation'] = pillarplus.math.find_rotation(source['location'],target['location'])
					if target['size'] == None:
						target['size'] = connection['size']
			
			print(source,target,'------------------------')
			source['rotation'] = pillarplus.math.find_rotation(source['location'],target['location'])
			
			if source_node[0] == 'J':
				if source['size'] == None:
					source['size'] = connection['size']                                                             # --:WARNING:-- (ensures size is not None)
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
						reducer = ' reducer ' + str(out_size) + '-' + str(in_size)

		
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

						if reducer != None and 'reducer' not in source['type']:
							source['type'] += reducer
							source['size'] = 75 # as scaling of joint will not be needed if a reducer joint

				# mirror tyoe need not to to be decided for some joints (find a better approah for this)
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
		except:

			continue
	return graph


def draw_double_lined_pipes(start_point,end_point,pipe_size,layer_name, arrow_block,conversion_factor=1):							

	angle = pillarplus.math.find_perpendicular_slope_angle(start_point,end_point)
	s1,s2 = pillarplus.math.directed_points_on_line(start_point,angle,pipe_size/2)
	e1,e2 = pillarplus.math.directed_points_on_line(end_point,angle,pipe_size/2)

	# draw pipe boundaries
	_msp.add_line(s1, e1, dxfattribs={'layer': layer_name})
	_msp.add_line(s2, e2, dxfattribs={'layer': layer_name})
	distance = pillarplus.math.find_distance(start_point, end_point)
	arrows_from_distance = [600, 1000, 3000]

	#placing arrows

	distance = distance * conversion_factor
	if distance < arrows_from_distance[0]:
		arrows_number = 0
	elif distance < arrows_from_distance[1]:
		arrows_number = 1
	elif distance < arrows_from_distance[2]:
		arrows_number = 2
	else:
		arrows_number = 3
	'''
	if arrows_number==1 or arrows_number==3:
		#place in center
		pass;																					#--:WARNING:-- (not completed)

	if arrows_number==2 or arrows_number==3:
		#place at ends
		pass;																					#--:WARNING:-- (not completed)
	'''
	if (arrow_block == None):
		return

	# importing the block
	importer = Importer(_joints_dwg, _dwg)
	importer.import_block(arrow_block['block_name'])
	importer.finalize()
	# getting the required gap
	required_gap = distance/(arrows_number + 1)
	# getting the angle of the pipe
	angle = pillarplus.math.find_rotation(start_point, end_point)
	# placing the block
	place_arrow(start_point, angle, arrow_block, arrows_number, required_gap, layer_name)

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
		_dwg.layers.new(name=layer['name'], dxfattribs={'linetype': layer['linetype'], 'color': COLORS[layer['color']]})
		layers_created.append(layer['name'])
	return layers_created

	

def draw_connections(graph, joints_defaults, conversion_factor):
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

	for source_node,target_node,connection in graph.edges(data=True):
		try:
			#CREATE USEFUL VARIABLES
			source = graph.nodes[source_node]
			target = graph.nodes[target_node]
			layer_name = 'PP-' + connection['type']
			print(source,target,'------------------------')
			distance = pillarplus.math.find_distance(source['location'],target['location'])
			if 'size' in source.keys():
				scale_factor = source['size']/75 										#--:WARNING:-- (conversion not required)
			else:
				scale_factor = 1
			if layer_name not in layers:
				print('layer not created for pipe type : ' + layer_name + '... Default given! ')
				layer_name = "DEFAULT"

			# PLACE JOINT AND GET OUT TRIMS
			if source_node[0] == 'J':
				try:
					key = source['type'] + str(' mirror' if source['mirror'] else '')
					joint_default = joints_defaults[key]
				except KeyError:
					print('key not found in joints_defaults_dict (for source) - ' + key + 'source no: '+ source_node,'key')
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

				if 'trap' == source['type'][-4:]:
					if source['type']!='bottle trap':
						#place grid / grating
						grating_joint = joints_defaults['SS grating']
						importer = Importer(_joints_dwg, _dwg)
						importer.import_block(grating_joint['block_name'])
						importer.finalize()
						place_block_at_location(grating_joint['block_name'], location, 
												scale_factor * conversion_factor, 0, grating_joint['center'], layer_name, _msp)

					#place text for short name
					shift_margin = distance + 150 * conversion_factor
					text_location = pillarplus.math.find_directed_point(target['location'],source['location'],shift_margin)
					short_name = joint_default['short_name']
					if short_name!=None:
						_msp.add_text(short_name,
							dxfattribs={'height': 30, 'layer': '0'}).set_pos(text_location,				# --:WARNING:-- (hcv - text height,layer)
																align='MIDDLE_CENTER')
					else:
						print('short name is none for trap - ' + _type)
			else:
				outtrim = 0

			# DRAW CONNECTION
			if outtrim == None:
				outtrim = 0
			start_trim = outtrim * scale_factor * conversion_factor

			# GET IN TRIM FROM TARGET
			if target_node[0] == 'J':
				try:
					target_node_key = target['type'] + str(' mirror' if target['mirror'] else '')
					joint_default_target = joints_defaults[target_node_key]
				except KeyError :
					print('key not found in joints_defaults_dict (for target) - ' + target_node_key)
					joint_default_target = joints_defaults['Cross tee']
				end_trim = joint_default_target['intrim'] * target['size']/75 * conversion_factor

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
							end_trim = joint_default_target['sidetrim'] * target['size']/75 * conversion_factor
						else	:
							print('side trim not given for ' + joint_default_target['type'])
						pass
						#side trim is not required
			else:
				end_trim = 0

			start_connection = pillarplus.math.find_directed_point(source['location'],target['location'], start_trim)
			end_connection = pillarplus.math.find_directed_point(target['location'], source['location'], end_trim)
			

			pipe_length = pillarplus.math.find_distance(start_connection, end_connection)
			connection['pipe_length'] = pipe_length
			draw_double_lined_pipes(start_connection, end_connection, connection['size'], layer_name, arrow_block)

			# ADDING TEXT FOR PIPE
			pipe_text = connection['text']
			pipe_text_location = pillarplus.math.find_directed_point(source['location'],target['location'],distance/2)
			if pipe_text != None:
				#add pipe_text
				_msp.add_text(pipe_text,
								dxfattribs={'height': 30, 'layer':layer_name}).set_pos(pipe_text_location,				# --:WARNING:-- (hcv - text height)
															align='MIDDLE_CENTER')
			else:
				print("pipe text is None for connection no. "+ str(connection['number']))
			
			
			# PLACE THE LEAF TARGET IF ITS A JOINT
			if graph.out_degree(target_node)==0 and target_node[0]=='J':									#--:WARNING:-- (ensure 'type' is defined in graph)
				try:
					key = target['type'] + str(' mirror' if target['mirror'] else '')
					joint_default = joints_defaults[key]
				except KeyError:
					print('key not found in joints_defaults_dict (for target) - ' + key)
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

				place_block_at_location(block_name, location, scale_factor * conversion_factor, rotation,
										joint_default['center'], layer_name, _msp)
		except:
			continue		
	return 'success'

def draw_entities_data(entities,conversion_factor,**props):
	global _msp
	global _dwg
	global _joints_dwg
	for entity_number,entity in entities.items():
		# Add text to chamber
		if 'chamber' in entity['type']:
			text_to_add =  entity['display_name']
			text_to_add += "\nI.Lvl :"+str(entity['invert_level'])
			text_to_add += "\nDepth :"+str(entity['depth'])
			text_location = entity['location']
			try:
				text = _msp.add_mtext(text_to_add, dxfattribs={
														'char_height': 30,								# --:WARNING:-- (hcv - text height)
														'bg_fill': 2,
														'box_fill_scale': 1,
													})
				text.set_location(text_location)				
			except Exception as e:
				return "Error while adding text to chamber :-" + str(e)

		# Add gratting to traps
		if 'trap' in entity.keys() and entity['trap']!=None:
			grating_joint = props['grating_joint'] if 'grating_joint' in props.keys() else None

			if grating_joint==None:
				return "grating joint not passed to function as kwargs"


			importer = Importer(_joints_dwg, _dwg)
			importer.import_block(grating_joint['block_name'])
			importer.finalize()
			place_block_at_location(grating_joint['block_name'], entity['location'], 
									 conversion_factor, 0, grating_joint['center'], '0', _msp)		# --:WARNING:-- (layer_name - '0')


	return 'success'

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
					print(f'{row[0]} is {value}')
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

	# _dwg = ezdxf.new('R2010')                                                          #--:WARNING:-- (replace creation of new file with reading of file)
	# _msp = _dwg.modelspace()
	# FILE READING
	autocad_file = this_dir + params_dict['ProjectFolder'] + 'updated_in.dxf'
	set_msp(autocad_file)

# 'p-FF-Drainage - 1.0.0 (1).json' #test file of webapp
	with open(this_dir + params_dict['ProjectFolder'] + 'updated_identification.json') as json_file:
		data = json.load(json_file)

	joints_dict = {}
	for joint in data['joints']:
		# if joint['service'] == 'drainage':
		joints_dict[joint['number']] = joint

	for k,entity in joints_dict.items():
		if entity['location'] == None and entity['elevation_location'] == None:
			if entity['screen_location'] != None:
				location = list(get_autocad_location(entity['screen_location'], data['params']))
				entity['location'] = location
				#calculate screen_location

	entities_dict = {}
	for entity in data['entities']:
		# if entity['service'] == 'drainage':
		entities_dict[entity['number']] = entity

	for k,entity in entities_dict.items():
		if entity['location'] == None and entity['elevation_location'] == None:
			if entity['screen_location'] != None:
				location = list(get_autocad_location(entity['screen_location'], data['params']))
				entity['location'] = location
				#calculate screen_location

	
	connections = []

	for connection in data['connections']:
		if connection['service'] == 'drainage':
			connections.append(connection)

	conversion_factor = data['params']['Units conversion factor']


	graph = create_graph(connections, joints_dict, entities_dict)

	graph = update_graph_properties(graph)

	# for node in graph.nodes(data=True):
	#     print(node)

	# from json joints_defaut ---- key: display name, value: joint_default dict
	joints_defaults_dict = {}
	for joint_default in data['joint_defaults']:
		if joint_default['service'] == 'drainage' or joint_default['service'] == 'all':
			key = joint_default['type'] + str(' mirror' if joint_default['mirror'] else '')
			joints_defaults_dict[key] = joint_default

	# print(joints_defaults_dict,'dddd');

	result = draw_connections(graph,joints_defaults_dict,conversion_factor)
	if result != 'success':
		result += '\nError in drawing connection graph'
		print(result)


	# draw entities extra data
	result = draw_entities_data(entities_dict,conversion_factor,grating_joint=joints_defaults_dict['SS grating'])
	if result != 'success':
		result += '\nError in drawing entities data'
		print(result)


	save_dwg(this_dir + params_dict['ProjectFolder'] + 'drainage output.dxf')


	#calculate boq
	boq_data = boq.calculate_boq(graph,entities_dict)
	#save boq json
	drainage_boq_json = json.dumps(boq_data)
	f = open(this_dir + params_dict['ProjectFolder'] + "drainage_boq_json.json",'w')
	f.write(drainage_boq_json)
	f.close()
