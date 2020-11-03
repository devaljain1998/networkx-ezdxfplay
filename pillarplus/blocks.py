from ezdxf.math import OCS, Matrix44, Vector


class Block(object):
    """For processing the blocks.csv file. blocks.csv file is unique to a project.
    This is a class for INSERT entity types. Since blocks are collection
    of shapes, we need target points in the block coordinate system. This class
    stores this information about a block. These blocks are placed at various
    locations in the AutoCad file by the architect or by the PillarPlus team.

    .. image:: blocks.png

    Assume you're standing at the center and facing at the block rotation angle
    Then points behind your back are back and in front are front points.
    Similarly for left and right.

    Attributes:
        number (int): Reference number for each block name
        name (str): name of the block in AutoCAD file
        type (str): Items in the room - fan, tubelight, wash basin
        rotation (float): Rotation of block in block's coordinate in degrees
        scale (float): scale of first instance of it's entity in AutoCAD file
        base_point ((x,y,z)): Base point in block layout
        front_left ((x,y,z)): Extreme front left point in block layout
        front_right ((x,y,z)): Extreme front right point in block layout
        back_left ((x,y,z)): Extreme back left point in block layout
        back_right ((x,y,z)): Extreme back right point in block layout
        center ((x,y,z)): Center point in block layout
        height (float): To overwrite on default entity height
        breadth (float): To overwrite on default breadth height
    """

    def __init__(self, number, name, block_type, block_rotation, scale,
                 base_point, front_left, front_right, back_left, back_right,
                 center, height, breadth):
        super(Block, self).__init__()
        self.number = number
        self.name = name
        self.type = block_type
        self.rotation = block_rotation
        self.scale = scale  # Needed for placing a user given block
        self.base_point = base_point
        self.front_left = front_left
        self.front_right = front_right
        self.back_left = back_left
        self.back_right = back_right
        self.center = center
        self.height = height
        self.breadth = breadth

    def __str__(self):
        return f'''Details of block "{self.name}":
        number: {self.number}
        name: {self.name}
        type: {self.type}
        rotation: {self.rotation}
        scale: {self.scale}
        base_point: {self.base_point}
        center: {self.center}
        height: {self.height}
        breadth: {self.breadth}'''


class BlockDefaults(object):
    """For processing the joints.csv file. joints.csv file is set once.
    This contains fixed and default information about PillarPlus's blocks
    (blocks of joints and elevational blocks) used by draw programs to place
    the required blocks in the AutoCad file.

    Attributes:
        block_name (str): Name of joint
        display_name (str): Display name of joint
        auto_up (bool): Used to place a top bend joint
        mirror (bool): True or False, used to place blocks in AutoCad, not to be used for web app
        center ((x,y,z)): Target point in block
        intrim (float): To trim pipe going in
        outtrim (float): To trim pipe going out
        sidetrim (float): To trim pipe going to side
        short_name (str): Short name of joint
        service (str): drainage, water supply, controlling
        is_elevation (str): Is this a block only for elevation
        color (str): Display color of node for front-end
    """

    def __init__(self, block_name, block_type, auto_up, mirror, centerX,
                 centerY, centerZ, intrim, outtrim, sidetrim, short_name,
                 service, is_elevation, color):
        super(BlockDefaults, self).__init__()
        self.block_name = block_name
        self.type = block_type
        self.auto_up = auto_up
        self.mirror = mirror
        self.center = (centerX, centerY, centerZ)
        self.intrim = intrim
        self.outtrim = outtrim
        self.sidetrim = sidetrim
        self.short_name = short_name
        self.service = service
        self.is_elevation = is_elevation
        self.color = color


class AutoPlaceBlock(object):
    """For processing the autodistance.csv file. autodistance.csv file is set once.
    Class that contains information about automatic joints placement for an
    entity type. The automatic joint to be placed has a type, distances from
    center, height and a category specifing where would the user want the joint
    to appear.

    Attributes:
        entity_type (str): Name of the entity for which we are autoplacing joints
        center_dist (float): center distance from center towards behind to place a joint automatically
        behind_dist (float): behind distance from center to place a joint automatically
        left_dist (float): left distance from center to place a joint automatically
        right_dist (float): right distance from center to place a joint automatically
        center_joint_type (str): center joint type to be placed automatically
        behind_joint_type (str): behind joint type to be placed automatically
        left_joint_type (str): left joint type to be placed automatically
        right_joint_type (str): right joint type to be placed automatically
        center_height (float): Height of center joint type to be placed automatically
        behind_height (float): Height of behind joint type to be placed automatically
        left_height (float): Height of left joint type to be placed automatically
        right_height (float): Height of right joint type to be placed automatically
        center_category_joint_type (str): p, e - Floor plan or elevation
        behind_category_joint_type (str): p, e - Floor plan or elevation
        left_category_joint_type (str): p, e - Floor plan or elevation
        right_category_joint_type (str): p, e - Floor plan or elevation
    """

    def __init__(self, entity_type, center_dist, behind_dist, left_dist, right_dist,
                 center_joint_type, behind_joint_type, left_joint_type, right_joint_type,
                 center_height, behind_height, left_height, right_height, center_category_joint_type,
                 behind_category_joint_type, left_category_joint_type, right_category_joint_type):
        super(AutoPlaceBlock, self).__init__()
        self.entity_type = entity_type

        self.center_dist = center_dist
        self.behind_dist = behind_dist
        self.left_dist = left_dist
        self.right_dist = right_dist

        self.center_joint_type = center_joint_type
        self.behind_joint_type = behind_joint_type
        self.left_joint_type = left_joint_type
        self.right_joint_type = right_joint_type

        self.center_height = center_height
        self.behind_height = behind_height
        self.left_height = left_height
        self.right_height = right_height

        self.center_category_joint_type = center_category_joint_type
        self.behind_category_joint_type = behind_category_joint_type
        self.left_category_joint_type = left_category_joint_type
        self.right_category_joint_type = right_category_joint_type


class EntityDefaults(object):
    """For processing the entitydefaults.csv file. entitydefaults.csv file is
    set once. Entity types are ceiling light, fan, wc floor, etc. This class
    contains fixed and default information about each entity type.

    Some entities might not have watt and breadth value.

    Attributes:
        type (str): Items in the room - fan, tubelight, wash basin
        short_name (str): Notation - FN (for fan), TB (for tubelight)
        height (float): Default height of the block
        breadth (float): Default breadth of the block
        elevation_block_name (str): Block to display in elevation
        dimensioning (int): 1 for both walls, 2 for same wall, else None
        category (str): p, e, b - Floor plan or elevation or both
        watt (int): Watt value for controlling entities
        service (str): drainage, water supply, controlling
        color (str): Display color of node for front-end
    """

    def __init__(self, entity_type, short_name, height, breadth,
                 elevation_block_name, dimensioning, category, watt, service,
                 color):
        super(EntityDefaults, self).__init__()
        self.type = entity_type
        self.short_name = short_name
        self.height = height
        self.breadth = breadth
        self.elevation_block_name = elevation_block_name
        self.dimensioning = dimensioning
        self.category = category
        self.watt = watt
        self.service = service
        self.color = color

    def __str__(self):
        return f'''Default details of entity "{self.type}":
        short_name: {self.short_name}
        height:{self.height}
        breadth:{self.breadth}
        elevation_block_name: {self.elevation_block_name}
        dimensioning:{self.dimensioning}
        category:{self.category}
        watt:{self.watt}
        service:{self.service}
        color:{self.color}'''

    def modified_dict(self):
        d = self.__dict__.copy()
        if self.watt is None:
            d.pop('watt')
        if self.breadth is None:
            d.pop('breadth')
        return d


class Entity(object):
    """For processing the in.dxf file. in.dxf file is unique to a project.
    This class contains all the information about the entites in the building.
    Each Entity object is represented by the occurance of a block in the
    AutoCAD file.

    This class also has attributes that represent the entity in elevational
    views

    Attributes:
        number (int): Unique for all entities
        type_number (int): Unique only among a particular entity type - 1st fan, 2nd fan
        short_name (str): Notation - FN (for fan), TB (for tubelight)
        display_name (str): Labelling - FN1, FN2, FN3, FN4 (for fan)
        block_name (str): Block name of the entity in AutoCAD file
        type (str): Type of the entity - fan, tubelight, wash basin
        location ((x,y,z)): Location of entity in AutoCAD file in floor plan in msp, not to be used for web app
        screen_location ((x,y,z)): Scaled location for web app in floor plan, not to be used for ezdxf
        room_number (int): Reference number for each room
        wall_number (int): Reference number for each wall
        rotation (float): Rotation of entity in AutoCAD file in degrees
        scale (float): scale of entity in AutoCAD file
        height (float): Height of the entity
        breadth (float): Breadth of the entity
        length (float): Length of the entity
        category (str): p, e, b - Floor plan or elevation or both
        watt (int): Watt value for entities in controlling service
        service (str): drainage, water supply, controlling
        wall_point ((x,y)): Perpendicular of location on nearest wall in AutoCad space, not to be used for web app
        elevation_point ((x,height)): Location of entity in elevational view with respect to wall left-bottom point in AutoCad msp, not to be used for web app
        elevation_location ((x,y,z)): Location of entity in elevational view in AutoCad msp, not to be used for web app
        screen_elevation_location ((x,y,z)): Location in elevational view in web app, not to be used for ezdxf
        elevation_block_name (str): Block to display in elevation
        invert_level (float): Invert level, only for IC, GT, RWC in drainage added while creating json
        finish_floor_level (float): Finish floor level, only for IC, GT, RWC in drainage added while creating json
        chamber_depth (float): Chamber depth, only for IC, GT, RWC in drainage added while creating json
        trap (str): BT, PT, bottle trap
        color (str): Display color of node for front-end
    """

    chambers_types = ['gully trap chamber',
                      'inspection chamber', 'rainwater chamber']

    def __init__(self, number, type_number, short_name, block, ent_type, location,
                 screen_location, room, wall, wall_point, elevation_point, elevation_location, elevation_screen_location,
                 rotation, scale, height, breadth, length, elevation_block_name, category, watt, service, trap, color):
        super(Entity, self).__init__()
        self.number = number
        self.type_number = type_number  # 1, 2 for CL only
        self.short_name = short_name
        # display_name of the entity
        self.display_name = f'{short_name}{type_number}'
        self.block_number = block.number
        self.block = block  # gets removed while creating json
        self.type = ent_type
        self.location = location  # Location in floor plan
        self.screen_location = screen_location  # Location in floor plan in web app
        self.room_number = room.number if room is not None else None
        self.wall_number = wall.number if wall is not None else None
        self.wall = wall  # None if no wall, it'll be an object, gets removed while creating json
        self.rotation = rotation
        self.scale = scale
        self.height = height
        self.breadth = breadth  # For door and window
        self.length = length
        self.category = category
        self.watt = watt
        self.service = service
        self.wall_point = wall_point
        self.elevation_point = elevation_point
        self.elevation_location = elevation_location
        self.elevation_screen_location = elevation_screen_location
        self.elevation_block_name = elevation_block_name

        self.invert_level = None
        self.finish_floor_level = None
        self.chamber_depth = None
        self.trap = trap
        self.color = color

        self.switchboard_data = None
        self.socket_data = None
        self.fixture_data = None

    def __str__(self):
        return f'''Details of entity "{self.display_name}":
        number: {self.number}
        type_number: {self.type_number}
        short_name: {self.short_name}
        display_name: {self.display_name}
        block_number: {self.block_number}
        location:{self.location}
        screen_location: {self.screen_location}
        rotation:{self.rotation}
        room_number: {self.room_number}
        wall_number: {self.wall_number}
        scale: {self.scale}
        height: {self.height}
        breadth: {self.breadth}
        length: {self.length}
        category: {self.category}
        wall_point: {self.wall_point}
        elevation_point: {self.elevation_point}
        elevation_location: {self.elevation_location}
        elevation_screen_location: {self.elevation_screen_location}
        elevation_block_name: {self.elevation_block_name}
        watt: {self.watt}
        service: {self.service}
        trap: {self.trap}
        color: {self.color}'''

    def modified_dict(self):
        d = self.__dict__.copy()
        d.pop('block')
        d.pop('wall')
        if self.type != 'switchboard':
            d.pop('switchboard_data')
            d.pop('socket_data')
            d.pop('fixture_data')
        if self.watt is None:
            d.pop('watt')
        if self.breadth is None:
            d.pop('breadth')
        if self.wall_number is None:
            d.pop('wall_point')
            d.pop('elevation_point')
            d.pop('elevation_location')
            d.pop('elevation_screen_location')
        if self.type not in Entity.chambers_types:
            d.pop('invert_level')
            d.pop('finish_floor_level')
            d.pop('chamber_depth')
        if self.trap is None:
            d.pop('trap')
        return d


def place_block_at_location(block_name, location, scale, rotation,
                            offset, layer, msp):
    """
    Places a block in the msp.

    Block of name block_name is placed in a given layer at location point in msp by
    calculating the block insert point in msp. offset is not given in ezdxf documentation.
    It is just a target point in block layout. It's used as a reference point
    using which we will place the collection of shapes called the block. 

    Parameters:
        block_name (str): Name of the block that needs to be placed
        location ((x,y,z)): Target location in msp
        scale (float): Required scale of the block
        rotation (float): Required rotation of the block in msp
        offset ((x,y,z)): Target point in the coordinate system of block
        layer (str): Required layer of the block in msp
        msp (msp object): msp of dxf file
    """
    offset = Vector(offset).rotate_deg(rotation) * scale
    block_location = location - offset  # (0, 0, 0) of block coordinate
    msp.add_blockref(block_name, block_location, dxfattribs={
                     'layer': layer,
                     'rotation': rotation,
                     'xscale': scale,
                     'yscale': scale
                     })


def get_location_of_block(e, offset, base_point):
    """
    Given an INSERT entity e, this function gives location of target point of
    the block e in msp. The target point is specifed using the offset.

    Block entity gives entity.dxf.insert point. Offset needs to be added to get
    location of target point. Offset needs to modified to account for rotation,
    positive scale, negative scale and mirroring.

    Parameters:
        e (Entity object): Required block entity
        offset ((x,y,z)): Point in the coordinate system of block
        base_point ((x,y,z)): Base point in block layout, generally (0, 0, 0)

    Returns:
        location (x,y,z): Target point of block in msp
    """
    ocs = OCS(e.dxf.extrusion)
    mat = Matrix44.chain(Matrix44.ucs(ocs.ux, ocs.uy, ocs.uz), Matrix44.scale(
        e.get_dxf_attrib('xscale', 1), e.get_dxf_attrib('yscale', 1), e.get_dxf_attrib('zscale', 1)))
    offset_ = mat.transform(offset)
    offset_2 = ocs.to_wcs(offset_)

    o = Vector(offset_2).rotate_deg(e.get_dxf_attrib('rotation', 0))
    return ocs.to_wcs(e.dxf.insert + o)
