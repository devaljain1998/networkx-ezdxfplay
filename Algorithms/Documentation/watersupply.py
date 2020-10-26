"""
watersupply.py
====================================

This Module includes functions to draw watersupply drawings.


Packages used:
1. ezdxf
2. networkx
3. math

Global variables
1. _dwg : the auto cad file read through ezdxf
2. _msp : modelspace created on the autocad file
3. _joints_dwg: auto cad file of joints block
4. connection_to_layer


To Do:
Add arrows (done only blocks not placed)
HCV values
BOQ
Texting

"""
import ezdxf
from ezdxf.addons import Importer
from ezdxf.lldxf.const import DXFTableEntryError
import networkx as nx
import math
from pillarplus.blocks import place_block_at_location
import pillarplus.math
from pillarplus.data import create_size_mapping_dict
from texting import add_text_to_wall,add_text_to_connection
import pillarplus.boq.watersupply_boq as wboq

_dwg = None
_msp = None
_joints_dwg = None

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

		source_node = create_hash(source_type,source_number)
		target_node = create_hash(target_type,target_number)
		graph.add_node(source_node, **source_dict)
		graph.add_node(target_node, **target_dict)
		graph.add_edge(source_node, target_node, **connection)

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
				directed_graph.add_edge(head,j,**graph[head][j])
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



def update_graph_properties(graph):                                         # specific to water supply
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
        source = graph.nodes[source_node]
        target = graph.nodes[target_node]

        source_location = source['location'] if connection['category']!='e' else source['elevation_location']
        target_location = target['location'] if connection['category']!='e' else target['elevation_location']

        #Mostly Entity in water supply but if not entity
        if graph.in_degree(source_node) == 0: # source is root node
            if source_node[0] == 'J':
                source['rotation'] = pillarplus.math.find_rotation(source_location,target_location)
                source['mirror'] = False
                if source['size'] == None:
                    source['size'] = connection['size']
                if source['type'] == None:
                    print('giving cold tap by default to '+str(source_node)+' as no type is given')
                    source['type'] = 'cold tap'


        # Assuming from here that target is a joint and not entity in ws (entity do not have rotation)
        target['rotation'] = pillarplus.math.find_rotation(source_location,target_location)
        if 'size' in target.keys():
            if target['size'] == None:
                target['size'] = connection['size']
        else:
            target['size'] = connection['size']
        # --:WARNING:-- (ensures size(conn) is not null)
		#  do this earlier while making graph

        child_nodes = list(graph.successors(target_node))
        if len(child_nodes) == 1:
            #Bend 90 or valve tap or upbend or coupler or pump
            child_node = child_nodes[0]
            child = graph.nodes[child_node]
            child_location = child['location'] if child['category']!='e' else child['elevation_location']
            if target['category'] != 'b' and target['type']==None:
                in_angle = find_angle(child_location, target_location, source_location)
                if math.pi/2 - 0.1 < in_angle < math.pi/2 + 0.1 or 3/2 * math.pi - 0.1 < in_angle < 3/2 * math.pi + 0.1:
                    target['type'] = 'Bend 90'
                else:
                    print('joint type valve or coupler or tap not given ', target_node)
                    target['type'] = 'Coupler' # coupler by default

            #reducer check
            in_size = connection['size']
            out_size = graph[target_node][child_node]['size']


            if (in_size != out_size):
                reducer = ('reducer', in_size, out_size)
                # if ljoint reducer exist of the size then add property to target else add property to connection 
                graph[target_node][child_node]['reducer'] = reducer						#--: WARNING :-- currently not adding reducer to any joint;

            if (target['type'] == 'Bend 90'):
                #mirror check
                target['mirror'] = pillarplus.math.is_inverted(target_location, source_location, child_location)

        elif len(child_nodes) == 2:
            # assuming that a two child node can only be 'Single tee'
            if target['type'] == None:
                target['type'] = 'Single tee'
            child_node_1 = graph.nodes[child_nodes[0]]
            child_node_2 = graph.nodes[child_nodes[1]]
            child_location_1 = child_node_1['location'] if child_node_1['category']!='e' else child_node_1['elevation_location']
            child_location_2 = child_node_2['location'] if child_node_2['category']!='e' else child_node_2['elevation_location']
            # decide child node, equals to non-180 degree node
            if math.pi - 0.1 < find_angle(child_location_1,target_location,source_location) < math.pi + 0.1:
                child_node = child_nodes[1]
                child = graph.nodes[child_node]
                child_location = child['location'] if child['category']!='e' else child['elevation_location']
            elif math.pi - 0.1 < find_angle(child_location_2,target_location,source_location) < math.pi + 0.1:
                child_node = child_nodes[0]
                child = graph.nodes[child_node]
                child_location = child['location'] if child['category']!='e' else child['elevation_location']
            else: #none of the child at 180
                target['type'] = 'sp single tee'
                child_node = child_nodes[0]
                child = graph.nodes[child_node]
                child_location = child['location'] if child['category']!='e' else child['elevation_location']

            #check reducer

            # if tjoint reducer exist of the size then add property to target else add property to connections
            # --:WARNING:-- currently this is adding reducer to both the child connections
            for child_node in child_nodes:
                in_size = connection['size']
                out_size = graph[target_node][child_node]['size']
                if (in_size!=out_size):
                    reducer = ('reducer',in_size,out_size)
                    graph[target_node][child_node]['reducer'] = reducer

            #check mirror
            target['mirror'] = pillarplus.math.is_inverted(target_location, source_location, child_location)
            if target['type']=='sp single tee':
                target['mirror'] = False

        elif len(child_nodes) == 3:
            if target['type']==None:
                target['type'] = 'Cross tee'
            for child_node in child_nodes:
                in_size = connection['size']
                out_size = graph[target_node][child_node]['size']
                if (in_size!=out_size):
                    reducer = ('reducer',in_size,out_size)
                    graph[target_node][child_node]['reducer'] = reducer
        elif len(child_nodes) == 0:
            if target['type'] == None:
                target['type'] = 'cold tap' # give cold tap by default
                print('a node with no child have type equals to None', target['number'], 'given cold tap by default')

        else:
            #a node have more then 3 childrens
            pass
    return graph

    
connection_to_layer = {}
def create_layers():
	global _dwg
	global connection_to_layer

	LAYERS = [{																								#--: WARNING :-- (hcv)
	'name' : 'PP-CWS',
	'color' : 'blue',
	'linetype' : 'SOLID',
	'connection' : 'CWS'
	},
	{
	'name' : 'PP-HWS',
	'color' : 'red',
	'linetype' : 'SOLID',
	'connection' : 'HWS'
	},
	{
	'name' : 'PP-HWR',
	'color' : 'magenta',
	'linetype' : 'SOLID',
	'connection' : 'HRWS'
	},
	{
	'name' : 'PP-FWS',
	'color' : 'brown',
	'linetype' : 'SOLID',
	'connection' : 'FWP'
	},
	{
	'name' : 'DEFAULT',
	'color' : 'cyan',
	'linetype' : 'SOLID',
	'connection' : 'all'
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

	for layer in LAYERS:
		try:
			_dwg.layers.new(name=layer['name'], dxfattribs={'linetype': layer['linetype'], 'color': COLORS[layer['color']]})
		except DXFTableEntryError as e:
			print(e)
		connection_to_layer[layer['connection']] = layer['name']

def place_arrows(start_point,end_point,arrow_block,layer_name,conversion_factor,width):
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

def draw_double_lined_pipes(start_point,end_point,pipe_size,layer_name):
	global _msp

	angle = pillarplus.math.find_perpendicular_slope_angle(start_point,end_point)
	s1,s2 = pillarplus.math.directed_points_on_line(start_point,angle,pipe_size/2)
	e1,e2 = pillarplus.math.directed_points_on_line(end_point,angle,pipe_size/2)

	# draw pipe boundaries
	_msp.add_line(s1, e1, dxfattribs={'layer': layer_name})
	_msp.add_line(s2, e2, dxfattribs={'layer': layer_name})


def draw_reducer(point_list, layer_name):
	global _msp

	_msp.add_lwpolyline(point_list,dxfattribs={'layer': layer_name})


def draw_connections(graph, joints_defaults,params):
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
    connection_to_layer global dic in this module
    """
    global _msp
    global _dwg
    global _joints_dwg
    global connection_to_layer
    create_layers()
    TYPE_FOR_NOT_DRAWING = 'Joint'
    conversion_factor = params['Units conversion factor']
    try:
        key = 'arrow'       													# --:WARNING:-- (hcv)
        arrow_block = joints_defaults[key]
    except KeyError:
        print('Arrow joint not found')
        arrow_block = None

    for source_node,target_node,connection in graph.edges(data=True):
        source = graph.nodes[source_node]
        target = graph.nodes[target_node]
        if 'size' in source.keys():
            source['size'] = connection['size'] if source['size'] == None else source['size']
        else:
            source['size'] = connection['size']
        if connection['type'] in connection_to_layer.keys():
            layer_name = connection_to_layer[connection['type']]
        else:
            layer_name = connection_to_layer['all']
        if target_node[0] == 'J':
            # assuming always true as in water supply target will always be a joint and
            # source need to be drawn only when when its in-edges are zero and its a joint (handeled below)
            try:
                # print(target['number']);
                target['type'] = '' if target['type'] == None else target['type']
                key = target['type'] + str(' mirror' if target['mirror'] else '') + str(' E' if connection['category'] else '')
                if key not in joints_defaults.keys() and key[-1]=='E':
                    key = key[:-2] # This case comes when elevation and plan have same block
                joint_default = joints_defaults[key]
            except KeyError:
                joint_default = joints_defaults['Cross tee']
                print('key not found in joints_defaults_dict (for target) - ' + key)

            source_location = source['location'] if connection['category']!='e' else source['elevation_location']
            target_location = target['location'] if connection['category']!='e' else target['elevation_location']


            distance = pillarplus.math.find_distance(source_location,target_location)
            if target['size'] == None:
                target['size'] = connection['size']
            scale_factor = target['size']/75 #(no conversion required)
            # DRAW CONNECTION (get trims first)
            # blindly assume end_trim will be intrim of target joint
            # then get the parent edge if exist then decide start_trim accordingly
            in_trim = joint_default['intrim'] if joint_default['intrim'] else 0
            end_trim = in_trim * scale_factor

            if source_node[0] == 'J':
                try:
                    source['type'] = '' if source['type'] == None else source['type']
                    source_node_key = source['type'] + str(' mirror' if source['mirror'] else '') + str(' E' if connection['category'] else '')
                    if source_node_key not in joints_defaults.keys() and source_node_key[-1]=='E':
                        source_node_key = source_node_key[:-2] # This case comes when elevation and plan have same block
                    joint_default_source = joints_defaults[source_node_key]
                except KeyError :
                    joint_default_source = joints_defaults['Cross tee']
                    print('key not found in joints_defaults_dict (for source) - ' + source_node_key)
                parent_nodes = list(graph.predecessors(source_node))
                if (len(parent_nodes)!=0):
                    #parent edge exist
                    parent_node = parent_nodes[0] # as in ws a node can have only one parent
                    parent = graph.nodes[parent_node]
                    parent_edge = graph[parent_node][source_node]
                    parent_location = parent['location'] if parent_edge['category']=='p' else parent['elevation_location']
                    #above line is different from other's which are like these because its meant to be

                    if math.pi - 0.1 < find_angle(parent_location,source_location,target_location) < math.pi + 0.1: #180 degree child then out trim else side trim
                        start_trim = joint_default_source['outtrim'] * source['size']/75
                    else:
                        if 'sidetrim' in joint_default_source.keys():
                            joint_default_source['sidetrim'] = joint_default_source['outtrim'] if joint_default_source['sidetrim']==None else joint_default_source['sidetrim']
                            start_trim = joint_default_source['sidetrim'] * source['size']/75
                        else:
                            start_trim = joint_default_source['outtrim'] * source['size']/75
                else:
                    start_trim = joint_default_source['outtrim'] * source['size']/75
            else:
                start_trim = 0

            start_connection = pillarplus.math.find_directed_point(source_location,target_location, start_trim)
            end_connection = pillarplus.math.find_directed_point(target_location, source_location, end_trim)

            # For BOQ pipe length always in meter
            connection['pipe_length'] = pillarplus.math.find_distance(start_connection, end_connection)/conversion_factor * 100
            if connection['type'] == TYPE_FOR_NOT_DRAWING:
                connection['pipe_length'] = 0

            if 'reducer' in connection.keys() and connection['type'] != TYPE_FOR_NOT_DRAWING:
                reducer = connection['reducer']
                # HARDCODED VALUES GIVEN IN mm
                REDUCER_WIDTH = 30 * conversion_factor
                REDUCER_DISPLACEMENT = 10 * conversion_factor
                connection['pipe_length'] -= REDUCER_WIDTH
                # draw starting pipe (before reducer)
                temp_end_connection = pillarplus.math.find_directed_point(start_connection, end_connection, REDUCER_DISPLACEMENT)
                draw_double_lined_pipes(start_connection,temp_end_connection, reducer[1],layer_name)
                # set new start_connection
                start_connection = pillarplus.math.find_directed_point(start_connection, end_connection, REDUCER_WIDTH)
                # draw reducer
                angle = pillarplus.math.find_perpendicular_slope_angle(temp_end_connection,start_connection)
                s1,s2 = pillarplus.math.directed_points_on_line(temp_end_connection,angle,reducer[1]/2)
                e1,e2 = pillarplus.math.directed_points_on_line(start_connection,angle,reducer[2]/2)
                draw_reducer([s1,e1,e2,s2,s1],layer_name)

            if connection['type'] != TYPE_FOR_NOT_DRAWING:
                draw_double_lined_pipes(start_connection, end_connection, connection['size'],layer_name)
                place_arrows(start_connection,end_connection,arrow_block, layer_name, conversion_factor, connection['size'])


            #ADDING TEXT
            pipe_text = connection['text']
            if pipe_text != None:
                #add pipe_text
                add_text_to_connection(connection, start_connection, end_connection, params, _msp, layer_name)
                # pipe_text_location = pillarplus.math.find_directed_point(source_location,target_location,distance/2)
                # _msp.add_text(pipe_text,
                #                 dxfattribs={'height': 30*conversion_factor}).set_pos(pipe_text_location,								# --:WARNING:-- (hcv - text height)
                #                                              align='MIDDLE_CENTER')
            else:
                print("pipe text is null for connection no. "+ str(connection['number']))

            #PLACE JOINT
            block_name = joint_default['block_name']
            block_center = joint_default['center']
            if block_name is None:
                print('block name is none for ' + joint_default['type'])
                continue
            try:
                importer = Importer(_joints_dwg, _dwg)
                importer.import_block(block_name)
                importer.finalize()
            except:
                print(block_name + ' block not imported')
                importer = Importer(_joints_dwg, _dwg)
                importer.import_block('PP-CROSS TEE WS')
                importer.finalize()
            location = target_location
            rotation = target['rotation'] if target['rotation'] != None else 0
            place_block_at_location(block_name, location, scale_factor, rotation,
                                    block_center, layer_name, _msp)

            #check if on elevation and place there too
            if target['category'] == 'b':
                location = target['elevation_location']
                place_block_at_location(block_name, location, scale_factor, -90,
                                        block_center, layer_name, _msp)


        if graph.in_degree(source_node)==0 and source_node[0]=='J':
            try:
                key = source['type'] + str(' mirror' if source['mirror'] else '') + str(' E' if connection['category'] else '')
                if key not in joints_defaults.keys() and key[-1]=='E':
                    key = key[:-2] # This case comes when elevation and plan have same block
                joint_default = joints_defaults[key]
            except KeyError :
                print('key not found in joints_defaults_dict (for source) - ' + key)
                joint_default = joints_defaults['Cross tee']

            scale_factor = source['size']/75
            #place joint 
            block_name = joint_default['block_name']
            if block_name is None:
                print('block name is none for ' + joint_default['type'])
                continue
            try:
                importer = Importer(_joints_dwg, _dwg)
                importer.import_block(block_name)
                importer.finalize()
            except:
                print(block_name + ' block not imported')
                importer = Importer(_joints_dwg, _dwg)
                importer.import_block('PP-CROSS TEE WS')
                importer.finalize()
            location = source['location'] if source['category']=='p' else source['elevation_location']
            rotation = source['rotation'] if source['rotation'] else 0
            place_block_at_location(block_name, location, scale_factor, rotation,
                                    joint_default['center'], layer_name, _msp)

    return 'success'

def assign_joints_to_walls(graph,walls,rooms,conversion_factor):
    for node in graph:
        joint = graph.nodes[node]
        if joint['category'] == 'p':
            continue
        
        if joint['wall_number'] != None:
            continue
        
        joint_location = joint['elevation_location']
        
        flag = 1
        for wall in walls:
            for room in rooms:
                if wall['room_number'] == room['number']:
                    wall_height = room['height'] * conversion_factor
            x0,y0 = wall['wall_bottom_left'][0],wall['wall_bottom_left'][1]
            x1 = x0 + pillarplus.math.find_distance(wall['corners'][0], wall['corners'][1])
            y1 = y0 + wall_height
            
            if x0-10<=joint_location[0]<=x1+10 and y0-10<=joint_location[1]<=y1+10: #--:WARNING:-- (manual buffers for inside joint)
                flag = 0
                joint['wall_number'] = wall['number']
                break
        if flag:
            return 'Error: joint '+node+' is not inside any wall!'
    return 'success'
            
            
def draw_automatic_from_elevation(graph,walls,params,size_mapping_dict):
    global connection_to_layer
    conversion_factor = params['Units conversion factor']
    DISPLACEMENT = 50 * conversion_factor
    
    walls_dict = {}
    for wall in walls:
        walls_dict[wall['number']] = wall
    
    
    _dwg.linetypes.new('DASHEDown', dxfattribs={'description': 'dashed - - - - -', 'pattern': [0.5,0.4,-0.8]})
    
    for source_node,target_node,connection in graph.edges(data=True):
        if connection['category'] != 'e':
            continue
        
        source = graph.nodes[source_node]
        target = graph.nodes[target_node]
        
        source_location_x = source['elevation_location'][0]
        target_location_x = target['elevation_location'][0]
        
        wall = walls_dict[source['wall_number']]
        dis1 = source_location_x - wall['wall_bottom_left'][0]
        dis2 = target_location_x - wall['wall_bottom_left'][0]
        point1 = pillarplus.math.find_directed_point(wall['corners'][0],wall['corners'][1],dis1)
        point2 = pillarplus.math.find_directed_point(wall['corners'][0],wall['corners'][1],dis2)
        
        displacement = DISPLACEMENT
        
        if ('CWS' in connection['type']):
            displacement *= 1.5
        
        out_pair_point1 = pillarplus.math.directed_points_on_line(point1,wall['in_angle']*math.pi/180,displacement)
        out_pair_point2 = pillarplus.math.directed_points_on_line(point2,wall['in_angle']*math.pi/180,displacement)
        
        if connection['type'] in connection_to_layer.keys():
            layer_name = connection_to_layer[connection['type']]
        else:
            layer_name = connection_to_layer['all']
        
        if connection['method']=='Wall':
            out_point1 = out_pair_point1[0]
            out_point2 = out_pair_point2[0]
        else:
            out_point1 = out_pair_point1[1]
            out_point2 = out_pair_point2[1]

        
        _msp.add_line(out_point1,point1,dxfattribs={'layer': layer_name,'linetype':'DASHEDown'})
        _msp.add_line(out_point2,point2,dxfattribs={'layer': layer_name,'linetype':'DASHEDown'})
        _msp.add_line(out_point1,out_point2,dxfattribs={'layer': layer_name,'linetype':'DASHEDown'})
        
        taps = ['cold tap','hot tap']
        if graph.out_degree(target_node)==0 and target['type']!='up bend watersupply': # chase to
            text_temp = target['type']
            if text_temp not in taps:
                text_temp = text_temp.replace(taps[0],'')
                text_temp = text_temp.replace(taps[1],'')
            text = '⌀ '+ str(size_mapping_dict[connection['size']])+ params['Units'] +'\nRunning Through ' + str(connection['method']) + '\nChase To ' + text_temp
            add_text_to_wall(out_point2, text, wall, params, _msp, layer_name)
        if graph.out_degree(source_node)==0 and target['type']!='up bend watersupply': # chase from
            text_temp = target['type']
            if text_temp not in taps:
                text_temp = text_temp.replace(taps[0],'')
                text_temp = text_temp.replace(taps[1],'')
            text = '⌀ '+ str(size_mapping_dict[connection['size']]) + params['Units'] +'\nRunning Through ' + str(connection['method']) + '\nChase From ' + text_temp
            add_text_to_wall(out_point2, text, wall, params, _msp, layer_name)
            
        
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


    # JSON Reading
    with open(this_dir + params_dict['ProjectFolder'] + 'updated_identification.json') as json_file:
        data = json.load(json_file)

    joints_dict = {}
    for joint in data['joints']:
        if joint['service'] == 'watersupply':
            joints_dict[joint['number']] = joint

    entities_dict = {}
    for entity in data['entities']:
        if joint['service'] == 'watersupply':
            entities_dict[entity['number']] = entity


    connections = []

    for connection in data['connections']:
        if connection['service'] == 'watersupply':
            connections.append(connection)

    walls = []

    for wall in data['walls']:
        walls.append(wall)

    rooms = []

    for room in data['rooms']:
        rooms.append(room)

    conversion_factor = data['params']['Units conversion factor']

    # Creating and updating graph


    graph = create_graph(connections, joints_dict, entities_dict)
    graph = get_directed_graph(graph,['cold water pipe','hot water pipe','hot tap geyser','up bend watersupply'])

    #removing unnecessary edges
    edges_to_remove = []
    for source_node,target_node,connection in graph.edges(data=True):
        if connection['type'] == 'Joint':
            edges_to_remove.append((source_node,target_node))
    
    for source_node,target_node in edges_to_remove:
        graph.remove_edge(source_node,target_node)

    graph = update_graph_properties(graph)
    
    # Drawing graph

    autocad_file = this_dir + params_dict['ProjectFolder'] + 'updated_in.dxf'
    set_msp(autocad_file)
    joints_defaults_dict = {}
    service_to_include = ['watersupply','all','draw']
    for joint_default in data['joint_defaults']:
        if joint_default['service'] in service_to_include:
            key = joint_default['type'] + str(' mirror' if joint_default['mirror'] else '') + str(' E' if joint_default['is_elevation'] else '')
            joints_defaults_dict[key] = joint_default

            
    result = draw_connections(graph,joints_defaults_dict,data['params'])
    if result != 'success':
        result += '\n Error in drawing connection graph'
        print(result)

    # Assigning joints to walls
    result = assign_joints_to_walls(graph,walls,rooms,conversion_factor)
    if result != 'success':
        result += '\n Error in assigning joints to walls'
        print(result)

    #SIZE MAPPING CREATION
    current_unit = data['params']['Units']
    sizes_dict = data['sizes']['watersupply']
    size_mapping_dict = create_size_mapping_dict(sizes_dict,current_unit)

    # Drawing back lines from elevation to plan only if all joints are assigned to walls
    if result == 'success':
        result = draw_automatic_from_elevation(graph,walls,data['params'],size_mapping_dict)
        if result != 'success':
            result += '\n Error in drawing automatic pipes'
            print(result)


    save_dwg(this_dir +  params_dict['ProjectFolder'] + 'ws_output.dxf')

    #  BOQ

    # #calculate boq
    boq_data = wboq.calculate_boq(graph)
    #save boq json
    watersupply_boq_json = json.dumps(boq_data)
    f = open(this_dir +  params_dict['ProjectFolder'] + "watersupply_boq_json.json",'w')
    f.write(watersupply_boq_json)
    f.close()
