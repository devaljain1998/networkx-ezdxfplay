import ezdxf
import random

dwg = ezdxf.new()
msp = dwg.modelspace()


points = []
polylines = None

with open('wall_point_data_file.txt') as wall_point_data_file:
    wall_point_data = wall_point_data_file.read()
    polylines = eval(wall_point_data)
    # polylines = list(map(lambda polyline: polyline[0], polylines))
    # print(polylines)
    # wall_point_data = str(polylines)
    
# print(wall_point_data_file)
# with open('wall_point_data_file2.txt', 'w') as wall_point_data_file:
#     wall_point_data_file.write(wall_point_data)

print(len(polylines))
print(polylines)

if polylines is None: 
    raise IOError('Polylines is None. Error in reading file.')
# else:
#     from pprint import pprint
#     pprint(polylines)

dwg.layers.new('IP-LAYER')
# for polyline in polylines:
#     print('polyline: ', polyline)
msp.add_lwpolyline(polylines, dxfattribs = {'layer': 'IP-LAYER',}) # 'color': random.randint(1, 7)


dwg.saveas('test-polyline.dxf')
