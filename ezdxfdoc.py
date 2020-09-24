import ezdxf
from ezdxf.math import Vector

print(dir(ezdxf))

# read a dxf file

filePathIn = 'dxfFilesIn/'
filePathOut = 'dxfFilesOut/'

dwg = ezdxf.readfile(filePathIn + 'in.dxf')

# dwg.layers, dwg.blocks
# use dwg.layers to get layers
# use dwg.blocks to get properties of the block
# blocks has dxftype()=='INSERT'

# modelspace contains all entities
msp = dwg.modelspace()

# add a new layer
dwg.layers.new(name='MyCircles', dxfattribs={'color': 7})
dwg.layers.new(name='WallDetection', dxfattribs={'color': 60})
dwg.layers.new(name='HVLines', dxfattribs={'color': 100})
# delete an entity from modelspace
# msp.delete_entity(entity)


# dxfattribs and properties accessed using .dxf
def print_entity(e):
    # properties common to all entities
    '''
    print(e.dxftype(), 'Type')
    print(e.dxf.layer, 'e.dxf.layer')
    print(e.dxf.handle, 'e.dxf.handle')
    print(e.dxf.linetype, 'e.dxf.linetype')
    print(e.dxf.ltscale, 'e.dxf.ltscale')
    '''
# all entities have certain properties according to their types
    if e.dxftype() == 'INSERT':  # block type
        print(e.dxf.name, 'e.dxf.name')

        # get OCS (coordinates)
        print(e.dxf.insert, 'e.dxf.insert')
        # get world coordinates (WCS)
        wcs_location = e.ocs().to_wcs(e.dxf.insert)
        print(wcs_location, 'WCS')

    if e.dxftype() == 'CIRCLE':
        print(e.dxf.center, 'e.dxf.center')
        print(e.dxf.radius, 'e.dxf.radius')

    if e.dxftype() == 'LWPOLYLINE':
        print(e.get_points(), 'e.dxf.points')

    if e.dxftype() == 'LINE':
        print(e.dxf.start, 'e.dxf.start')
        print(e.dxf.end, 'e.dxf.end')
        print(e.dxf.color, 'e.dxf.color')

    if e.dxftype() == 'ARC':
        # the arc goes from start_angle to end_angle
        # in counter clockwise direction
        print(e.dxf.center, 'e.dxf.center')
        print(e.dxf.radius, 'e.dxf.radius')
        print(e.dxf.start_angle, 'e.dxf.start_angle')
        print(e.dxf.end_angle, 'e.dxf.end_angle')

    if e.dxftype() == 'ELLIPSE':
        # the ellipse goes from start to end param
        # in counter clockwise direction
        # a full ellipse goes from 0 to 2*pi
        print(e.dxf.center, 'e.dxf.center')
        # endpoint of major axis, relative to the center
        print(e.dxf.major_axis, 'e.dxf.major_axis')
        print(e.dxf.ratio, 'e.dxf.ratio')
        print(e.dxf.start_param, 'e.dxf.start_param')
        print(e.dxf.end_param, 'e.dxf.end_param')

    if e.dxftype() == 'TEXT':
        print(e.dxf.text, 'e.dxf.text')		# returns a str
        print(e.dxf.insert, 'e.dxf.insert')
        print(e.dxf.height, 'e.dxf.height')
        print(e.dxf.rotation, 'e.dxf.rotation')
        print(e.dxf.width, 'e.dxf.width')

    if e.dxftype() == 'MTEXT':
        # To Do
        pass

    if e.dxftype() == 'SHAPE':
        print(e.dxf.name, 'e.dxf.name')
        print(e.dxf.insert, 'e.dxf.insert')
        print(e.dxf.size, 'e.dxf.size')
        print(e.dxf.rotation, 'e.dxf.rotation')

    if e.dxftype() == 'POLYLINE':
        print(e.dxf.elevation, 'e.dxf.elevation')
        print(e.dxf.flags, 'e.dxf.flags')
        print(e.dxf.m_count, 'e.dxf.m_count')
        print(e.dxf.n_count, 'e.dxf.n_count')

    if e.dxftype() == 'LWPOLYLINE':
        print(e.dxf.elevation, 'e.dxf.elevation')
        print(e.dxf.flags, 'e.dxf.flags')
        print(e.dxf.const_width, 'e.dxf.const_width')
        print(e.dxf.count, 'e.dxf.count')

    if e.dxftype() == 'SOLID' or e.dxftype() == 'TRACE':
        print(e.dxf.vtx0, 'e.dxf.vtx0')
        print(e.dxf.vtx1, 'e.dxf.vtx1')
        print(e.dxf.vtx2, 'e.dxf.vtx2')
        print(e.dxf.vtx3, 'e.dxf.vtx3')

    if e.dxftype() == 'HATCH':
        '''
        print(e.get_seed_points(),'e.get_seed_points()')
        print(e.dxf.pattern_name, 'e.dxf.pattern_name')		# returns a str
        print(e.dxf.solid_fill, 'e.dxf.solid_fill')
        print(e.dxf.pattern_angle, 'e.dxf.pattern_angle')
        '''
        with e.edit_boundary() as boundary:
            for p in boundary.paths:
                pass
                # To DO
                '''
				if isinstance(p, ezdxf.modern.hatch.PolylinePath):
					print(p.vertices, 'PolylinePath')
					print(p.is_closed, 'PolylinePath.is_closed')

				else:
					for edge in p.edges:
						if isinstance(edge, ezdxf.modern.hatch.LineEdge):
							print(edge.start, 'EdgePath start')
							print(edge.end, 'EdgePath end')
				'''
#print(e.dxf.thickness, 'e.dxf.thickness')
#print(e.dxf.true_color, 'e.dxf.true_color')
#print(e.dxf.color_name, 'e.dxf.color_name')
    print('###########')


# iterate over all entities in model space
for e in msp:
    print_entity(e)

'''
# query: first the required entity or * for all entities 
# second the optional attribute query, enclosed in square brackets: 
# 'EntityQuery[AttributeQuery]' with and, or, !
# modelspace.query('*[layer=="construction" and linestyle!="DASHED"]')
# Returns EntityQuery Object, it isn't a list of entities

# all entities in layer WASH BASINS
washbasins = msp.query('*[layer=="WASH BASINS"]')
for e in washbasins:
	print_entity(e)
'''


# returns offset of center of the first circle from the
# base point of the block
# common value for all occurances of the block in modelspace
def get_first_circle_center(block_layout):
    block = block_layout.block
    base_point = Vector(block.dxf.base_point)

    # get all circles in the layout
    circles = block_layout.query('CIRCLE')
    if len(circles):
        circle = circles[0]  # take first circle
        center = Vector(circle.dxf.center)
        return center - base_point
    else:
        return Vector(0, 0, 0)


# iterate over blockss
# blockrefs is EntityQuery Object, it isn't a list of entities
blockrefs = msp.query('INSERT[layer=="A-LIGHT"]')
if len(blockrefs):
    for entity in blockrefs:

        print("Reading entity in a blockrefs")
        print(entity.dxf.xscale, 'xscale')
        print(entity.dxf.yscale, 'yscale')
        print(entity.dxf.rotation, 'rotation')
        print(entity.dxf.extrusion, 'extrusion')

        # location of an INSERT block
        print("insert", entity.dxf.insert)

        # iterate over all entities in the block
        # details about block will be in dwg.blocks
        # find the block by it's name
        block = dwg.blocks[entity.dxf.name]
        for block_entity in block:
            print_entity(block_entity)

        # find WCS location of an entity in a block
        # .get() to get block layout object by block name
        block_layout = dwg.blocks.get(entity.dxf.name)
        offset = get_first_circle_center(block_layout)  # common offset value

        scale = entity.get_dxf_attrib('xscale', 1)  # assume uniform scaling
        _offset = offset.rotate_deg(
            entity.get_dxf_attrib('rotation', 0)) * scale

    # find circle's exact location on modelspace by adding
    # the center's offset in block layout to block's location
        location = entity.dxf.insert + _offset
        print(location, 'location using _offset')
    # add circles at a location
        # 'extrusion': e.dxf.extrusion needs to be specified for OCS
        msp.add_circle(center=location,
                       radius=1,
                       dxfattribs={'layer': 'MyCircles', 'extrusion': entity.dxf.extrusion})

else:
    print("Found no blocks for the query")


# save dwg files as a dxf file
dwg.saveas(filePathOut + 'output.dxf')

####################################


# Create new dxf files
# create a new DXF R2010 drawing, official DXF version name: 'AC1024'
dwg = ezdxf.new('R2010')
msp = dwg.modelspace()

# add new layers
dwg.layers.new(name='MyLines', dxfattribs={'linetype': 'DASHED', 'color': 7})

# add new entities to the model space
# add a LINE entity
msp.add_line((0, 0), (10, 0), dxfattribs={'layer': 'MyLines'})

# INSERT entity is a block
# first create the block by name FLAG
flag = dwg.blocks.new(name='FLAG')

# add entities to the block named FLAG
flag.add_polyline2d([(0, 0), (0, 5), (4, 3), (0, 3)])
flag.add_circle((0, 0), .4, dxfattribs={'color': 2})

# parameters - block name, x, y, attributes: xscale, yscale, rotation
# dxfattribs is different from attribs. attribs are just text annotations
insertion_point = 5, 5
random_scale = 1
rotation = -15

msp.add_blockref('FLAG', insertion_point, dxfattribs={
    'xscale': random_scale,
    'yscale': random_scale,
    'rotation': rotation
})

# save dwg files as a dxf file
dwg.saveas(filePathOut + 'newdwg.dxf')
