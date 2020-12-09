import json
import math
import pprint
from typing import List, Tuple, Union

import ezdxf
import networkx as nx
import shapely
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

from centre_lines import CentreLine
from pillarplus.math import (directed_points_on_line, find_angle,
                             find_distance, find_intersection_point_1,
                             find_mid_point, find_rotation,
                             get_nearest_lines_from_a_point, is_between,
                             find_perpendicular_point)

# from test_clean_wall_lines import centre_lines, msp, dwg
edges = [((328, 537), (528, 537)), ((328, 537), (328, 981)), ((528, 537), (528, 546)), ((588, 537), (614, 537)), ((588, 537), (588, 546)), ((614, 537), (614, 441)), ((337, 546), (528, 546)), ((337, 546), (337, 823)), ((588, 546), (614, 546)), ((614, 546), (614, 645)), ((614, 441), (642, 441)), ((642, 441), (642, 390)), ((646, 441), (661, 441)), ((646, 441), (646, 399)), ((661, 441), (661, 450)), ((718, 441), (775, 441)), ((718, 441), (718, 450)), ((775, 441), (775, 399)), ((619, 450), (661, 450)), ((619, 450), (619, 645)), ((718, 450), (775, 450)), ((775, 450), (775, 640)), ((661, 640), (679, 640)), ((661, 640), (661, 645)), ((679, 640), (679, 718)), ((709, 640), (775, 640)), ((709, 640), (709, 645)), ((614, 645), (619, 645)), ((661, 645), (674, 645)), ((674, 645), (674, 723)), ((709, 645), (775, 645)), ((775, 645), (775, 718)), ((679, 718), (754, 718)), ((754, 718), (754, 723)), ((772, 718), (775, 718)), ((772, 718), (772, 723)), ((674, 723), (746, 723)), ((746, 723), (746, 741)), ((751, 723), (754, 723)), ((751, 723), (751, 741)), ((772, 723), (775, 723)), ((775, 723), (775, 741)), ((554, 823), (559, 823)), ((554, 823), (554, 876)), ((559, 823), (559, 981)), ((784, 390), (770, 390)), ((784, 390), (784, 741)), ((784, 981), (601, 981)), ((784, 981), (784, 759)), ((642, 390), (651, 390)), ((646, 399), (651, 399)), ((651, 390), (651, 399)), ((775, 399), (770, 399)), ((775, 777), (772, 777)), ((775, 777), (775, 759)), ((751, 764), (751, 777)), ((751, 764), (746, 764)), ((751, 777), (754, 777)), ((746, 764), (746, 777)), ((746, 777), (674, 777)), ((775, 781), (775, 882)), ((775, 781), (772, 781)), ((775, 882), (737, 882)), ((775, 886), (775, 972)), ((775, 886), (737, 886)), ((775, 972), (601, 972)), ((674, 777), (674, 781)), ((674, 781), (703, 781)), ((703, 781), (703, 823)), ((703, 823), (601, 823)), ((703, 828), (703, 912)), ((703, 828), (601, 828)), ((703, 912), (703, 939)), ((707, 781), (707, 912)), ((707, 781), (754, 781)), ((707, 912), (706, 912)), ((737, 882), (737, 886)), ((559, 981), (505, 981)), ((601, 823), (601, 828)), ((554, 876), (517, 876)), ((554, 880), (554, 972)), ((554, 880), (517, 880)), ((554, 972), (505, 972)), ((601, 981), (601, 972)), ((505, 981), (505, 972)), ((487, 981), (482, 981)), ((487, 981), (487, 876)), ((482, 981), (482, 876)), ((464, 981), (328, 981)), ((464, 981), (464, 972)), ((464, 972), (337, 972)), ((337, 972), (337, 948)), ((772, 781), (772, 777)), ((754, 781), (754, 777)), ((337, 823), (512, 823)), ((337, 828), (512, 828)), ((337, 828), (337, 948)), ((482, 876), (487, 876)), ((517, 880), (517, 876)), ((512, 823), (512, 828)), ((700, 450), (700, 441)), ((700, 450), (691, 450)), ((700, 441), (691, 441)), ((770, 390), (770, 399)), ((703, 939), (706, 939)), ((706, 912), (706, 939)), ((775, 759), (784, 759)), ((775, 741), (784, 741)), ((746, 741), (750, 741)), ((750, 741), (751, 741)), ((691, 450), (691, 441))]


graph = nx.Graph()
graph.add_edges_from(edges)
print('graph creation success.', len(graph.edges))

centre_lines = [{'end_point': (332.5, 823.0),
                 'number': 1,
                 'screen_end_point': (332.5, 823.0),
                 'screen_start_point': (332.5, 823.0),
                 'start_point': (332.5, 546.0),
                 'width': 9.0},
                {'end_point': (332.5, 948.0),
                 'number': 2,
                 'screen_end_point': (332.5, 948.0),
                 'screen_start_point': (332.5, 948.0),
                 'start_point': (332.5, 828.0),
                 'width': 9.0},
                {'end_point': (332.5, 948.0),
                 'number': 3,
                 'screen_end_point': (332.5, 948.0),
                 'screen_start_point': (332.5, 948.0),
                 'start_point': (332.5, 972.0),
                 'width': 9.0},
                {'end_point': (473.0, 972.0),
                 'number': 4,
                 'screen_end_point': (473.0, 972.0),
                 'screen_start_point': (473.0, 972.0),
                 'start_point': (473.0, 981.0),
                 'width': 18.0},
                {'end_point': (484.5, 876.0),
                 'number': 5,
                 'screen_end_point': (484.5, 876.0),
                 'screen_start_point': (484.5, 876.0),
                 'start_point': (484.5, 981.0),
                 'width': 5.0},
                {'end_point': (496.0, 972.0),
                 'number': 6,
                 'screen_end_point': (496.0, 972.0),
                 'screen_start_point': (496.0, 972.0),
                 'start_point': (496.0, 981.0),
                 'width': 18.0},
                {'end_point': (556.5, 876.0),
                 'number': 7,
                 'screen_end_point': (556.5, 876.0),
                 'screen_start_point': (556.5, 876.0),
                 'start_point': (556.5, 823.0),
                 'width': 5.0},
                {'end_point': (556.5, 972.0),
                 'number': 8,
                 'screen_end_point': (556.5, 972.0),
                 'screen_start_point': (556.5, 972.0),
                 'start_point': (556.5, 880.0),
                 'width': 5.0},
                {'end_point': (616.5, 450.0),
                 'number': 9,
                 'screen_end_point': (616.5, 450.0),
                 'screen_start_point': (616.5, 450.0),
                 'start_point': (616.5, 537.0),
                 'width': 5.0},
                {'end_point': (616.5, 645.0),
                 'number': 10,
                 'screen_end_point': (616.5, 645.0),
                 'screen_start_point': (616.5, 645.0),
                 'start_point': (616.5, 546.0),
                 'width': 5.0},
                {'end_point': (644.0, 399.0),
                 'number': 11,
                 'screen_end_point': (644.0, 399.0),
                 'screen_start_point': (644.0, 399.0),
                 'start_point': (644.0, 441.0),
                 'width': 4.0},
                {'end_point': (646.5, 399.0),
                 'number': 12,
                 'screen_end_point': (646.5, 399.0),
                 'screen_start_point': (646.5, 399.0),
                 'start_point': (646.5, 390.0),
                 'width': 9.0},
                {'end_point': (651.5, 441.0),
                 'number': 13,
                 'screen_end_point': (651.5, 441.0),
                 'screen_start_point': (651.5, 441.0),
                 'start_point': (651.5, 441.0),
                 'width': 19.0},
                {'end_point': (648.5, 399.0),
                 'number': 14,
                 'screen_end_point': (648.5, 399.0),
                 'screen_start_point': (648.5, 399.0),
                 'start_point': (648.5, 399.0),
                 'width': 5.0},
                {'end_point': (653.5, 441.0),
                 'number': 15,
                 'screen_end_point': (653.5, 441.0),
                 'screen_start_point': (653.5, 441.0),
                 'start_point': (653.5, 441.0),
                 'width': 15.0},
                {'end_point': (667.5, 645.0),
                 'number': 16,
                 'screen_end_point': (667.5, 645.0),
                 'screen_start_point': (667.5, 645.0),
                 'start_point': (667.5, 645.0),
                 'width': 13.0},
                {'end_point': (670.0, 645.0),
                 'number': 17,
                 'screen_end_point': (670.0, 645.0),
                 'screen_start_point': (670.0, 645.0),
                 'start_point': (670.0, 640.0),
                 'width': 18.0},
                {'end_point': (676.5, 718.0),
                 'number': 18,
                 'screen_end_point': (676.5, 718.0),
                 'screen_start_point': (676.5, 718.0),
                 'start_point': (676.5, 645.0),
                 'width': 5.0},
                {'end_point': (695.5, 441.0),
                 'number': 19,
                 'screen_end_point': (695.5, 441.0),
                 'screen_start_point': (695.5, 441.0),
                 'start_point': (695.5, 450.0),
                 'width': 9.0},
                {'end_point': (709.0, 441.0),
                 'number': 20,
                 'screen_end_point': (709.0, 441.0),
                 'screen_start_point': (709.0, 441.0),
                 'start_point': (709.0, 450.0),
                 'width': 18.0},
                {'end_point': (705.0, 823.0),
                 'number': 21,
                 'screen_end_point': (705.0, 823.0),
                 'screen_start_point': (705.0, 823.0),
                 'start_point': (705.0, 781.0),
                 'width': 4.0},
                {'end_point': (704.5, 912.0),
                 'number': 22,
                 'screen_end_point': (704.5, 912.0),
                 'screen_start_point': (704.5, 912.0),
                 'start_point': (704.5, 912.0),
                 'width': 3.0},
                {'end_point': (705.0, 912.0),
                 'number': 23,
                 'screen_end_point': (705.0, 912.0),
                 'screen_start_point': (705.0, 912.0),
                 'start_point': (705.0, 828.0),
                 'width': 4.0},
                {'end_point': (704.5, 939.0),
                 'number': 24,
                 'screen_end_point': (704.5, 939.0),
                 'screen_start_point': (704.5, 939.0),
                 'start_point': (704.5, 912.0),
                 'width': 3.0},
                {'end_point': (705.0, 912.0),
                 'number': 25,
                 'screen_end_point': (705.0, 912.0),
                 'screen_start_point': (705.0, 912.0),
                 'start_point': (705.0, 912.0),
                 'width': 4.0},
                {'end_point': (706.5, 912.0),
                 'number': 26,
                 'screen_end_point': (706.5, 912.0),
                 'screen_start_point': (706.5, 912.0),
                 'start_point': (706.5, 912.0),
                 'width': 1.0},
                {'end_point': (748.5, 741.0),
                 'number': 27,
                 'screen_end_point': (748.5, 741.0),
                 'screen_start_point': (748.5, 741.0),
                 'start_point': (748.5, 723.0),
                 'width': 5.0},
                {'end_point': (750.0, 723.0),
                 'number': 28,
                 'screen_end_point': (750.0, 723.0),
                 'screen_start_point': (750.0, 723.0),
                 'start_point': (750.0, 723.0),
                 'width': 8.0},
                {'end_point': (748.5, 777.0),
                 'number': 29,
                 'screen_end_point': (748.5, 777.0),
                 'screen_start_point': (748.5, 777.0),
                 'start_point': (748.5, 764.0),
                 'width': 5.0},
                {'end_point': (750.0, 777.0),
                 'number': 30,
                 'screen_end_point': (750.0, 777.0),
                 'screen_start_point': (750.0, 777.0),
                 'start_point': (750.0, 777.0),
                 'width': 8.0},
                {'end_point': (752.5, 723.0),
                 'number': 31,
                 'screen_end_point': (752.5, 723.0),
                 'screen_start_point': (752.5, 723.0),
                 'start_point': (752.5, 723.0),
                 'width': 3.0},
                {'end_point': (752.5, 777.0),
                 'number': 32,
                 'screen_end_point': (752.5, 777.0),
                 'screen_start_point': (752.5, 777.0),
                 'start_point': (752.5, 777.0),
                 'width': 3.0},
                {'end_point': (763.0, 723.0),
                 'number': 33,
                 'screen_end_point': (763.0, 723.0),
                 'screen_start_point': (763.0, 723.0),
                 'start_point': (763.0, 718.0),
                 'width': 18.0},
                {'end_point': (763.0, 777.0),
                 'number': 34,
                 'screen_end_point': (763.0, 777.0),
                 'screen_start_point': (763.0, 777.0),
                 'start_point': (763.0, 781.0),
                 'width': 18.0},
                {'end_point': (772.5, 399.0),
                 'number': 35,
                 'screen_end_point': (772.5, 399.0),
                 'screen_start_point': (772.5, 399.0),
                 'start_point': (772.5, 399.0),
                 'width': 5.0},
                {'end_point': (777.0, 399.0),
                 'number': 36,
                 'screen_end_point': (777.0, 399.0),
                 'screen_start_point': (777.0, 399.0),
                 'start_point': (777.0, 390.0),
                 'width': 14.0},
                {'end_point': (773.5, 718.0),
                 'number': 37,
                 'screen_end_point': (773.5, 718.0),
                 'screen_start_point': (773.5, 718.0),
                 'start_point': (773.5, 718.0),
                 'width': 3.0},
                {'end_point': (773.5, 723.0),
                 'number': 38,
                 'screen_end_point': (773.5, 723.0),
                 'screen_start_point': (773.5, 723.0),
                 'start_point': (773.5, 723.0),
                 'width': 3.0},
                {'end_point': (778.0, 723.0),
                 'number': 39,
                 'screen_end_point': (778.0, 723.0),
                 'screen_start_point': (778.0, 723.0),
                 'start_point': (778.0, 718.0),
                 'width': 12.0},
                {'end_point': (773.5, 777.0),
                 'number': 40,
                 'screen_end_point': (773.5, 777.0),
                 'screen_start_point': (773.5, 777.0),
                 'start_point': (773.5, 777.0),
                 'width': 3.0},
                {'end_point': (773.5, 781.0),
                 'number': 41,
                 'screen_end_point': (773.5, 781.0),
                 'screen_start_point': (773.5, 781.0),
                 'start_point': (773.5, 781.0),
                 'width': 3.0},
                {'end_point': (778.0, 777.0),
                 'number': 42,
                 'screen_end_point': (778.0, 777.0),
                 'screen_start_point': (778.0, 777.0),
                 'start_point': (778.0, 781.0),
                 'width': 12.0},
                {'end_point': (779.5, 399.0),
                 'number': 43,
                 'screen_end_point': (779.5, 399.0),
                 'screen_start_point': (779.5, 399.0),
                 'start_point': (779.5, 441.0),
                 'width': 9.0},
                {'end_point': (779.5, 640.0),
                 'number': 44,
                 'screen_end_point': (779.5, 640.0),
                 'screen_start_point': (779.5, 640.0),
                 'start_point': (779.5, 450.0),
                 'width': 9.0},
                {'end_point': (779.5, 718.0),
                 'number': 45,
                 'screen_end_point': (779.5, 718.0),
                 'screen_start_point': (779.5, 718.0),
                 'start_point': (779.5, 645.0),
                 'width': 9.0},
                {'end_point': (779.5, 741.0),
                 'number': 46,
                 'screen_end_point': (779.5, 741.0),
                 'screen_start_point': (779.5, 741.0),
                 'start_point': (779.5, 723.0),
                 'width': 9.0},
                {'end_point': (779.5, 759.0),
                 'number': 47,
                 'screen_end_point': (779.5, 759.0),
                 'screen_start_point': (779.5, 759.0),
                 'start_point': (779.5, 777.0),
                 'width': 9.0},
                {'end_point': (779.5, 882.0),
                 'number': 48,
                 'screen_end_point': (779.5, 882.0),
                 'screen_start_point': (779.5, 882.0),
                 'start_point': (779.5, 781.0),
                 'width': 9.0},
                {'end_point': (779.5, 972.0),
                 'number': 49,
                 'screen_end_point': (779.5, 972.0),
                 'screen_start_point': (779.5, 972.0),
                 'start_point': (779.5, 886.0),
                 'width': 9.0},
                {'end_point': (528.0, 541.5),
                 'number': 50,
                 'screen_end_point': (528.0, 541.5),
                 'screen_start_point': (528.0, 541.5),
                 'start_point': (337.0, 541.5),
                 'width': 9.0},
                {'end_point': (464.0, 976.5),
                 'number': 51,
                 'screen_end_point': (464.0, 976.5),
                 'screen_start_point': (464.0, 976.5),
                 'start_point': (337.0, 976.5),
                 'width': 9.0},
                {'end_point': (512.0, 825.5),
                 'number': 52,
                 'screen_end_point': (512.0, 825.5),
                 'screen_start_point': (512.0, 825.5),
                 'start_point': (337.0, 825.5),
                 'width': 5.0},
                {'end_point': (554.0, 976.5),
                 'number': 53,
                 'screen_end_point': (554.0, 976.5),
                 'screen_start_point': (554.0, 976.5),
                 'start_point': (505.0, 976.5),
                 'width': 9.0},
                {'end_point': (554.0, 878.0),
                 'number': 54,
                 'screen_end_point': (554.0, 878.0),
                 'screen_start_point': (554.0, 878.0),
                 'start_point': (517.0, 878.0),
                 'width': 4.0},
                {'end_point': (614.0, 541.5),
                 'number': 55,
                 'screen_end_point': (614.0, 541.5),
                 'screen_start_point': (614.0, 541.5),
                 'start_point': (588.0, 541.5),
                 'width': 9.0},
                {'end_point': (703.0, 825.5),
                 'number': 56,
                 'screen_end_point': (703.0, 825.5),
                 'screen_start_point': (703.0, 825.5),
                 'start_point': (601.0, 825.5),
                 'width': 5.0},
                {'end_point': (775.0, 976.5),
                 'number': 57,
                 'screen_end_point': (775.0, 976.5),
                 'screen_start_point': (775.0, 976.5),
                 'start_point': (601.0, 976.5),
                 'width': 9.0},
                {'end_point': (642.0, 445.5),
                 'number': 58,
                 'screen_end_point': (642.0, 445.5),
                 'screen_start_point': (642.0, 445.5),
                 'start_point': (619.0, 445.5),
                 'width': 9.0},
                {'end_point': (661.0, 445.5),
                 'number': 59,
                 'screen_end_point': (661.0, 445.5),
                 'screen_start_point': (661.0, 445.5),
                 'start_point': (646.0, 445.5),
                 'width': 9.0},
                {'end_point': (651.0, 394.5),
                 'number': 60,
                 'screen_end_point': (651.0, 394.5),
                 'screen_start_point': (651.0, 394.5),
                 'start_point': (646.0, 394.5),
                 'width': 9.0},
                {'end_point': (674.0, 642.5),
                 'number': 61,
                 'screen_end_point': (674.0, 642.5),
                 'screen_start_point': (674.0, 642.5),
                 'start_point': (661.0, 642.5),
                 'width': 5.0},
                {'end_point': (746.0, 720.5),
                 'number': 62,
                 'screen_end_point': (746.0, 720.5),
                 'screen_start_point': (746.0, 720.5),
                 'start_point': (679.0, 720.5),
                 'width': 5.0},
                {'end_point': (746.0, 732.0),
                 'number': 63,
                 'screen_end_point': (746.0, 732.0),
                 'screen_start_point': (746.0, 732.0),
                 'start_point': (746.0, 732.0),
                 'width': 18.0},
                {'end_point': (703.0, 779.0),
                 'number': 64,
                 'screen_end_point': (703.0, 779.0),
                 'screen_start_point': (703.0, 779.0),
                 'start_point': (674.0, 779.0),
                 'width': 4.0},
                {'end_point': (746.0, 779.0),
                 'number': 65,
                 'screen_end_point': (746.0, 779.0),
                 'screen_start_point': (746.0, 779.0),
                 'start_point': (707.0, 779.0),
                 'width': 4.0},
                {'end_point': (746.0, 770.5),
                 'number': 66,
                 'screen_end_point': (746.0, 770.5),
                 'screen_start_point': (746.0, 770.5),
                 'start_point': (746.0, 770.5),
                 'width': 13.0},
                {'end_point': (754.0, 720.5),
                 'number': 67,
                 'screen_end_point': (754.0, 720.5),
                 'screen_start_point': (754.0, 720.5),
                 'start_point': (751.0, 720.5),
                 'width': 5.0},
                {'end_point': (700.0, 445.5),
                 'number': 68,
                 'screen_end_point': (700.0, 445.5),
                 'screen_start_point': (700.0, 445.5),
                 'start_point': (691.0, 445.5),
                 'width': 9.0},
                {'end_point': (751.0, 772.5),
                 'number': 69,
                 'screen_end_point': (751.0, 772.5),
                 'screen_start_point': (751.0, 772.5),
                 'start_point': (746.0, 772.5),
                 'width': 17.0},
                {'end_point': (754.0, 779.0),
                 'number': 70,
                 'screen_end_point': (754.0, 779.0),
                 'screen_start_point': (754.0, 779.0),
                 'start_point': (751.0, 779.0),
                 'width': 4.0},
                {'end_point': (775.0, 642.5),
                 'number': 71,
                 'screen_end_point': (775.0, 642.5),
                 'screen_start_point': (775.0, 642.5),
                 'start_point': (709.0, 642.5),
                 'width': 5.0},
                {'end_point': (775.0, 445.5),
                 'number': 72,
                 'screen_end_point': (775.0, 445.5),
                 'screen_start_point': (775.0, 445.5),
                 'start_point': (718.0, 445.5),
                 'width': 9.0},
                {'end_point': (775.0, 884.0),
                 'number': 73,
                 'screen_end_point': (775.0, 884.0),
                 'screen_start_point': (775.0, 884.0),
                 'start_point': (737.0, 884.0),
                 'width': 4.0},
                {'end_point': (751.0, 770.5),
                 'number': 74,
                 'screen_end_point': (751.0, 770.5),
                 'screen_start_point': (751.0, 770.5),
                 'start_point': (751.0, 770.5),
                 'width': 13.0},
                {'end_point': (751.0, 732.0),
                 'number': 75,
                 'screen_end_point': (751.0, 732.0),
                 'screen_start_point': (751.0, 732.0),
                 'start_point': (751.0, 732.0),
                 'width': 18.0},
                {'end_point': (775.0, 394.5),
                 'number': 76,
                 'screen_end_point': (775.0, 394.5),
                 'screen_start_point': (775.0, 394.5),
                 'start_point': (770.0, 394.5),
                 'width': 9.0},
                {'end_point': (775.0, 720.5),
                 'number': 77,
                 'screen_end_point': (775.0, 720.5),
                 'screen_start_point': (775.0, 720.5),
                 'start_point': (772.0, 720.5),
                 'width': 5.0},
                {'end_point': (775.0, 732.0),
                 'number': 78,
                 'screen_end_point': (775.0, 732.0),
                 'screen_start_point': (775.0, 732.0),
                 'start_point': (775.0, 732.0),
                 'width': 18.0},
                {'end_point': (775.0, 779.0),
                 'number': 79,
                 'screen_end_point': (775.0, 779.0),
                 'screen_start_point': (775.0, 779.0),
                 'start_point': (772.0, 779.0),
                 'width': 4.0},
                {'end_point': (775.0, 768.0),
                 'number': 80,
                 'screen_end_point': (775.0, 768.0),
                 'screen_start_point': (775.0, 768.0),
                 'start_point': (775.0, 768.0),
                 'width': 18.0},
                {'end_point': (784.0, 750.0),
                 'number': 81,
                 'screen_end_point': (784.0, 750.0),
                 'screen_start_point': (784.0, 750.0),
                 'start_point': (775.0, 750.0),
                 'width': 18.0}]

centre_lines = list(map(lambda centre_line_dict: CentreLine(**centre_line_dict), centre_lines))

try:
    with open('dxfFilesIn/identification_json/sample2.json') as identification_json_file:
        identification_json = json.load(identification_json_file)
        print('Success in reading the JSON file.')
except Exception:
    print('Failed to open identification JSON.')

windows = list(filter(lambda entity: entity['type']=='window' and entity['category'] == 'p', identification_json['entities']))
doors = list(filter(lambda entity: entity['type']=='door' and entity['category'] == 'p', identification_json['entities']))

# DEBUG:
def __debug_location(msp, point, name: str = 'debug', radius = 2, color:int = 2, char_height=0.5):
    msp.add_circle(point, radius, dxfattribs={'color': color, 'layer': 'debug'})
    mtext = msp.add_mtext(name, dxfattribs = {'layer': 'debug'})
    mtext.set_location(point)
    mtext.dxf.char_height = char_height



print('windows:', len(windows))

print('doors:', len(doors))

# all_doors = list(filter(lambda entity: entity['type']=='door', identification_json['entities']))
def debug_display_all_windows_and_doors():
    dwg = ezdxf.new()
    msp = dwg.modelspace()
    
    # Adding edges from the graph
    for edge in graph.edges:
        msp.add_line(edge[0], edge[1], dxfattribs={'layer': 'walls'})
    
    for window in windows:
        window_location = window['location']
        msp.add_circle(window_location, radius=1, dxfattribs={'color':2})
        window_text = msp.add_mtext(f'W{window["category"]}')
        window_text.set_location(window_location)
        window_text.dxf.char_height = 0.3

    for door in doors: #all_doors
        door_location = door['location']
        msp.add_circle(door_location, radius=1, dxfattribs={'color':2})
        door_text = msp.add_mtext(f'D{door["category"]}')
        door_text.set_location(door_location)
        door_text.dxf.char_height = 0.3
        
    dwg.saveas('dxfFilesOut/sample2/debug_dxf/extended_wall_lines/only_windows_and_doors_points.dxf')
    print('Windows and doors file saved at:', 'dxfFilesOut/sample2/debug_dxf/extended_wall_lines/only_windows_and_doors_points.dxf')
    exit()
# debug_display_all_windows_and_doors()

### HELPER FUNCTION:
centre_line_tree = None
def fill_str_tree(centre_lines):
    lines = []
    for centre_line in centre_lines:
        line = LineString([centre_line.start_point, centre_line.end_point])
        lines.append(line)
    global centre_line_tree
    centre_line_tree = STRtree(lines)
    print('Tree builded.')

def is_angle_is_180_or_0_degrees(angle: Union[float, int]) -> bool:
    from math import pi
    if type(angle) == int:
        return 179 <= angle <= 181 or -1 <= angle <= 1
    return (pi - 0.1) <= angle <= (pi + 0.1) or 0.1 <= angle <= -0.1

def break_edge_into_two_edges(edge, node, graph):
    # Fetch points from edge
    p1, p2 = edge
    # Create new edges
    new_edges = [(p1, node), (node, p2)]
    graph.add_edges_from(new_edges)
    # Delete the current edge
    graph.remove_edge(edge[0], edge[1])
    return


def get_nearest_centre_lines_from_a_point(
        point: tuple, centre_lines: List["CentreLine"], entity_location: tuple) -> List["CentreLine"]:
    """
    The function returns nearest centre_lines to a point.
    """
    centre_line_dict = {(centre_line.start_point, centre_line.end_point):centre_line for centre_line in centre_lines}
    nearest_lines = get_nearest_lines_from_a_point(point = point, lines = list(centre_line_dict.keys()))

    index = 0
    # DEBUG
    conversion_factor = 0.0393701
    DISTANCE_FOR_WALL_WITH_ENTITY = 20 * conversion_factor
    query = Point(entity_location).buffer(DISTANCE_FOR_WALL_WITH_ENTITY)
    # Check whether the starting lines are not too close for the entity_location    
    close_lines_to_the_entity_location = centre_line_tree.query(query)
    if len(close_lines_to_the_entity_location) > 0:
        for close_line in close_lines_to_the_entity_location:
            print(f"counter: {counter}", "increasing the index and neglecting the close centre_line")
            close_line_coords = tuple(close_line.coords)
            item_index = nearest_lines.index(close_line_coords)
            index = item_index + 1
    
    # Now map the nearest lines to the values of centrelines:
    nearest_lines = list(map(lambda nearest_line: centre_line_dict[nearest_line], nearest_lines))
    
    # DEBUG:
    import ezdxf
    _dwg = ezdxf.new()
    _msp = _dwg.modelspace()
    _msp.add_circle(entity_location, radius=0.2, dxfattribs={'layer': 'entity_location'})
    loc_text = _msp.add_mtext(f'{int(entity_location[0])}, {int(entity_location[1])}', dxfattribs={'layer':'debug'})
    loc_text.set_location(entity_location)
    loc_text.dxf.char_height = 0.2
    
    for idx, line in enumerate(nearest_lines):
        _msp.add_line(line.start_point, line.end_point, dxfattribs={'layer':'centrelines'})
        mtext = _msp.add_mtext(str(idx), dxfattribs={'layer':'centrelines'})
        mtext.set_location(find_mid_point(line.start_point, line.end_point))
        mtext.dxf.char_height = 0.3
    for edge in graph.edges:
        _msp.add_line(edge[0], edge[1], dxfattribs={'layer':'wall'})
    
    # label the chosen lines:
    n1, n2 = nearest_lines[index], nearest_lines[index+1]
    for n in (n1, n2):
        mtext = _msp.add_mtext('chosen', dxfattribs={
                              'layer': 'chosen_line', 'color': 3})
        mtext.set_location(find_mid_point(n.start_point, n.end_point))
        mtext.dxf.char_height = 0.5
    
    _dwg.saveas(f'dxfFilesOut/sample2/debug_dxf/extended_wall_lines/nearest_centre_lines_{counter}.dxf')
    print('Done saving nearest line', f'dxfFilesOut/sample2/debug_dxf/extended_wall_lines/nearest_centre_lines_{counter}.dxf')
    # import sys
    # sys.exit(1)    
    
    return nearest_lines[index], nearest_lines[index + 1]

def extend_wall_lines_for_entity(entity: dict, centre_lines: List["CentreLine"], graph: "nx.Graph"):
    """This function extends the wall_lines(edges) and updates the graph by the extending the walls for that entity.
    
    Procedure:
        1. Do some exception handling to check the type of the entity is "door" or "window".
        2. Get entity location:
            entity_location = entity["location"]
        3. Get nearest centre lines to that entity:
            nearest_centre_lines = get_nearest_lines_to_a_point(point = entity_location, lines = centre_lines)
        4. For the first two nearest lines, extend the wall:
            extended_lines = get_extended_wall_lines_with_nearest_lines(graph, nearest_line1, nearest_line2)
        5. Adjust the extended lines:
            adjust_extend_lines(graph, entity_location, extended_lines)
        6. return

    Args:
        entity (dict: "Entity"): Either of type "door" or "wall".
        centre_lines (current centrelines): current centrelines generated from the graph.
        graph (nx.Graph): A networkx graph.
    """
    def get_extended_wall_lines_with_nearest_lines(
        entity_location: float, graph: 'nx.Graph', nearest_line1: "CentreLine", nearest_line2: "CentreLine") -> List[tuple]:
        """This function extends the walls by taking in the input two nearest lines.
        
        Procedure:
            1. label both the nearest lines as "parallel" or "perpendicular".
                1.1 by looping each line: nearest_line
                1.2 getting the closest point of the nearest line.
                1.3 find the angle from the point, closest_point, distant_point
                1.4 if the angle is approx(0 | 180) degree then label it is as "parallel"
                    otherwise "perpendicular".
            2. for parallel line: get_directed_points for width / 2 and those are the end points of the new lines, (rotation + 90) of the nearest line.
            3. for perpendicular line: 
                3.1 perp_point = get_directed_point for width / 2 which is near to the point
                3.2 end_points =  get_directed_points for width / 2, perp_point, rotation of the nearest_line
            4. now just match both the end points to form lines:
                end_points = match_both_the_end_points(l1, l2, r1, r2)
            5. return end_points
            
        Args:
            entity_location (float)
            graph (nx.Graph)
            nearest_line1 ("CentreLine"): nearest_line[0]
            nearest_line2 ("CentreLine"): nearest_line[1]
        """
        def match_both_end_points(left_point1, left_point2, right_point1, right_point2):
            """This function should take in the points and should return the end_points in the following order like:
            left_point1 ------------- right_point1
            left_point2 ------------- right_point2
            (forms a straight line).
            
            Procedure:
                1. Create a left_point_set = {left_end_point1, left_end_point2}
                2. Create a right_point_set = {right_end_point1, right_end_point2}
                3. Create a polygon out of those 4 points (using convex hull):
                    polygon = convex_hull([left_point1, left_point2, right_point1, right_point2])
                4. loops over the polygon coordinates, [Loop until len(end_points) == 2]
                    4.1 if the p1, p2 belong to the same set of points then reject
                    4.2 otherwise add it into the end_points 2
                5. return end_points

            Args:
                left_point1
                left_point2
                right_point1
                right_point2
            """
            
            # 1. Create a left_point_set = {left_point1, left_point2}
            left_point_set = {left_point1, left_point2}
            # 2. Create a right_point_set = {right_point1, right_point2}
            right_point_set = {right_point1, right_point2}
            # 3. Create a polygon out of those 4 points (using convex hull):
            #     polygon = convex_hull([left_point1, left_point2, right_point1, right_point2])
            from shapely.geometry import MultiPoint
            multi_point = MultiPoint([left_point1, left_point2, right_point1, right_point2])
            polygon = multi_point.convex_hull
            polygon_coordinates = list(polygon.exterior.coords)
            
            end_points = []
            for i in range(len(polygon_coordinates) - 1):
                # Exit condition:
                if len(end_points) == 2:
                    break
                # Logic
                point, next_point = polygon_coordinates[i], polygon_coordinates[i + 1]
                # 4.1 if the p1, p2 belong to the same set of points then reject

                if (point in left_point_set and next_point in left_point_set) or (point in right_point_set and next_point in right_point_set):
                    continue
                else:
                    end_points.append((point, next_point))
            
            # exception handling:
            if len(end_points) != 2:
                raise ValueError(
                    f"The points provided for the endpoints are not forming the endpoints or any polygons for the points: {(left_point1, left_point2, right_point1, right_point2)}.")
                
            # Cleaning endpoints before returning:
            # Converting them into int:
            end_points[0] = tuple(map(lambda point: (int(point[0]), int(point[1])), end_points[0]))
            end_points[1] = tuple(map(lambda point: (int(point[0]), int(point[1])), end_points[1]))

            return end_points
        
        # labels:
        PARALLEL = "PARALLEL"
        PERPENDICULAR = "PERPENDICULAR"
        
        # 1. label both the nearest lines as "parallel" or "perpendicular".
        # 1.1 by looping each line: nearest_line
        for nearest_line in (nearest_line1, nearest_line2):
            closest_point = nearest_line.get_closest_point(entity_location)
            distant_point = nearest_line.start_point if nearest_line.end_point == closest_point else nearest_line.start_point
            # angle between entity location and closest point
            angle = find_angle(entity_location, closest_point, distant_point)
            
            nearest_line.type = PARALLEL if is_angle_is_180_or_0_degrees(angle) else PERPENDICULAR
            
        # DEBUG:
        _dwg = ezdxf.new()
        _msp = _dwg.modelspace()
        for edge in graph.edges:
            _msp.add_line(edge[0], edge[1])
        __debug_location(
            msp = _msp, 
            point = find_mid_point(nearest_line1.start_point, nearest_line1.end_point),
            name= nearest_line1.type,
            radius=3,
            color=5
        )
        __debug_location(
            msp = _msp, 
            point = find_mid_point(nearest_line2.start_point, nearest_line2.end_point),
            name= nearest_line2.type,
            radius=3,
            color=5
        )
        _dwg.saveas(f'dxfFilesOut/sample2/debug_dxf/extended_wall_lines/parallel_or_perpendicular_{counter}.dxf')
        print('saved', f'parallel_or_perpendicular_{counter}.dxf')
            
        end_point_sets = []
        
        #DEBUG:
        _dwg = ezdxf.new()
        _msp = _dwg.modelspace();
        
        # 2. Now find the end_points of each nearest_line:
        for nearest_line in (nearest_line1, nearest_line2):
            closest_point = nearest_line.get_closest_point(entity_location)
            distant_point = nearest_line.start_point if nearest_line.end_point == closest_point else nearest_line.end_point
            rotation = find_rotation(closest_point, distant_point)
            
            if nearest_line.type == PARALLEL:
                # get the end_points:
                nearest_line_end_point_rotation = math.radians(rotation + 90)
                nearest_line_end_points = directed_points_on_line(
                    closest_point, nearest_line_end_point_rotation, nearest_line.width / 2)
                end_point_sets.append(set(nearest_line_end_points))
            # for perpendicular
            else:
                perpendicular_point_on_the_centre_line = find_perpendicular_point(
                                    center=entity_location, line_start=closest_point, line_end=distant_point)
                perp_points = directed_points_on_line(
                    perpendicular_point_on_the_centre_line, math.radians(rotation + 90), nearest_line.width / 2)
                closest_perp_point = perp_points[0] if \
                    find_distance(entity_location, perp_points[0]) <= find_distance(entity_location, perp_points[1]) else perp_points[1]
                nearest_line_end_points = directed_points_on_line(
                    closest_perp_point, math.radians(rotation), nearest_line.width / 2)
                end_point_sets.append(set(nearest_line_end_points))
                
                # DEBUG
                __debug_location(
                    msp=_msp,
                    point=perpendicular_point_on_the_centre_line,
                    name='PERPPOINT',
                    radius=1,
                    color=4,
                    char_height=0.3
                );
                __debug_location(
                    msp=_msp,
                    point=closest_perp_point,
                    name='CPP',
                    radius=0.2,
                    color=2,
                    char_height=0.3
                );                
                __debug_location(
                    msp=_msp,
                    point=nearest_line_end_points[0],
                    name='nlep1',
                    radius=0.2,
                    color=5,
                    char_height=0.3
                );                
                __debug_location(
                    msp=_msp,
                    point=nearest_line_end_points[1],
                    name='nlep2',
                    radius=0.2,
                    color=5,
                    char_height=0.3
                );                


        # mapping sets to int
        end_point_sets[0] = set(map(lambda point: (int(point[0]), int(point[1])), end_point_sets[0]))
        end_point_sets[1] = set(map(lambda point: (int(point[0]), int(point[1])), end_point_sets[1]))
        
        left_end_points = list(end_point_sets[0])
        right_end_points = list(end_point_sets[1])
        
        # DEBUG
        for edge in graph.edges:
            _msp.add_line(edge[0], edge[1])
        for loc in (left_end_points + right_end_points):
            _msp.add_circle(loc, radius=1, dxfattribs={'color':3})
        _dwg.saveas(f'dxfFilesOut/sample2/debug_dxf/extended_wall_lines/endpoints_{counter}.dxf')
        print('saved', f'endpoints_{counter}.dxf')

        
        
        end_points = match_both_end_points(
            left_end_points[0], left_end_points[1], right_end_points[0], right_end_points[1])
        
        # DEBUG:
        # for end_point in end_points
        
        return end_points
        
    
    def adjust_extended_lines(entity_location: float, graph: 'nx.Graph', extended_lines: List[tuple]):
        """This function adjusts the extended_lines from the entity.
        
        Procedure:
            1. loop on extended lines:
                for extended_line in extended_lines:
            2 check for the left side first:
                2.1 check the left point lies on which edge: (intersection.)
                left_edge = get_edge_for_point()
                    intersection
                        for edge in graph.edges:
                            return is_between(point, edge)
                2.2 check if any node if left_end_points are nodes of the edge:
                    is_left_end_point1_a_node = check if it is in any of the nodes of edge
                    is_left_end_point2_a_node = check if it is in any of the nodes of edge
                2.3 if both the points are node 
                    2.3.1 then simply remove the edge
                2.4 elif if one of the point is node:
                    break the line from edge partially using the function break edge into two using the node which is not on the edge.
                2.5 elif none of the node is forming the edge:
                    then make the deconstruct the line into sequence using the unary_union (shapely method):
                        Example:
                        Current Scenario:
                        A----(B)----(C)-----D, we have edges as (A-D), (B-C)
                        which means that edges B-C is overlapping upon the A-D.
                        we want a output like: edges: A-B, B-C, C-D
                        which will be fetched using the unary_union.
            3. Repeat the point 2 for the right end points.
            4. return
        Args:
            entity_location (float): [description]
            graph (nx.Graph): [description]
            extended_lines (List[tuple]): [description]

        Raises:
            ValueError: [description]
        """
        # DEBUG: Sorting the extended lines before:
        extended_lines[0] = list(extended_lines[0]); extended_lines[0].sort(); extended_lines[0] = tuple(extended_lines[0])
        extended_lines[1] = list(extended_lines[1]); extended_lines[1].sort(); extended_lines[1] = tuple(extended_lines[1])

        left_nodes = list(map(lambda extended_line: extended_line[0], extended_lines))
        right_nodes = list(map(lambda extended_line: extended_line[1], extended_lines))
                
        # FOR LEFT NODE:
        # 1. only choosing the first left node as if first node is found on an edge then most probably the second node will also be on the edge
        first_left_node, second_left_node = left_nodes[0], left_nodes[1]
        for edge in graph.edges():
            if is_between(point=first_left_node, line_start=edge[0], line_end=edge[1]) and is_between(point=second_left_node, line_start=edge[0], line_end=edge[1]):
                left_edge = edge
                break
        
        # 2.2 check if any node if left_end_points are nodes of the edge:
        #     is_left_end_point1_a_node = check if it is in any of the nodes of edge
        #     is_left_end_point2_a_node = check if it is in any of the nodes of edge
        is_left_end_point1_a_node = first_left_node in {left_edge[0], left_edge[1]}
        is_left_end_point2_a_node = second_left_node in {left_edge[0], left_edge[1]}
        
        # 2.3 if both the points are node 
        if is_left_end_point1_a_node and is_left_end_point2_a_node:
            # edge is to be removed:
            graph.remove_edge(left_edge[0], left_edge[1])
        # 2.4 elif if one of the point is node:
        elif is_left_end_point1_a_node or is_left_end_point2_a_node:
            node_to_be_broken = first_left_node if is_left_end_point1_a_node else second_left_node
            break_edge_into_two_edges(edge=left_edge, node=node_to_be_broken, graph=graph)
        # 2.5 None of the edge is a node of any other edge
        else:
            from shapely.geometry import LineString
            from shapely.ops import unary_union
            lines = [
                LineString([first_left_node, second_left_node]),
                LineString([left_edge[0], left_edge[1]]),
            ]
            line_segments = unary_union(lines)
            
            # EXCEPTION HANDLING:
            if len(list(line_segments)) != 3:
                print("EXCEPTION OCCURED, LENGTH OF LINE SEGMENT IS NOT 3!")
                print(f'line_segments: {line_segments.wkt}')
                print({"first_right_node": first_right_node, "second_right_node": second_right_node, "right_edge": {right_edge}})
                raise ValueError("LineSegments cannot be segregated.")            
            
            # Cleaning line segments:
            edges = []
            for line_segment in line_segments:
                coords = list(line_segment.coords)
                for coord in coords:
                    coord = tuple(map(int, coord))
                coords.sort()
                coords = tuple(coords)
                edges.append(coords)
            edges.sort()
            
            # Now remove the middle segment
            edges_to_be_added = (edges[0], edges[1])
            edges_to_be_removed = [edges[1]]
            
            # graph.remove_edges_from(edges_to_be_removed)
            graph.add_edges_from(edges_to_be_added)


        # FOR RIGHT NODE:
        # 1. only choosing the first right node as if first node is found on an edge then most probably the second node will also be on the edge
        first_right_node, second_right_node = right_nodes[0], right_nodes[1]
        for edge in graph.edges():
            if is_between(point=first_right_node, line_start=edge[0], line_end=edge[1]) and is_between(point=second_right_node, line_start=edge[0], line_end=edge[1]):
                right_edge = edge
                break
        
        # 2.2 check if any node if right_end_points are nodes of the edge:
        #     is_right_end_point1_a_node = check if it is in any of the nodes of edge
        #     is_right_end_point2_a_node = check if it is in any of the nodes of edge
        is_right_end_point1_a_node = first_right_node in {right_edge[0], right_edge[1]}
        is_right_end_point2_a_node = second_right_node in {right_edge[0], right_edge[1]}
        
        # 2.3 if both the points are node 
        if is_right_end_point1_a_node and is_right_end_point2_a_node:
            # edge is to be removed:
            graph.remove_edge(right_edge[0], right_edge[1])
        # 2.4 elif if one of the point is node:
        elif is_right_end_point1_a_node or is_right_end_point2_a_node:
            node_to_be_broken = first_right_node if is_right_end_point1_a_node else second_right_node
            break_edge_into_two_edges(edge=right_edge, node=node_to_be_broken, graph=graph)
        # 2.5 None of the edge is a node of any other edge
        else:
            from shapely.geometry import LineString
            from shapely.ops import unary_union
            lines = [
                LineString([first_right_node, second_right_node]),
                LineString([right_edge[0], right_edge[1]]),
            ]
            line_segments = unary_union(lines)
            
            # EXCEPTION HANDLING:
            if len(list(line_segments)) != 3:
                print("EXCEPTION OCCURED, LENGTH OF LINE SEGMENT IS NOT 3!")
                print(f'line_segments: {line_segments.wkt}')
                print({"first_right_node": first_right_node, "second_right_node": second_right_node, "right_edge": {right_edge}})
                raise ValueError("LineSegments cannot be segregated.")
            
            # Cleaning line segments:
            edges = []
            for line_segment in line_segments:
                coords = list(line_segment.coords)
                for coord in coords:
                    coord = tuple(map(int, coord))
                coords.sort()
                coords = tuple(coords)
                edges.append(coords)
            edges.sort()
            
            # Now remove the middle segment
            edges_to_be_added = (edges[0], edges[1])
            edges_to_be_removed = [edges[1]]
            
            # graph.remove_edges_from(edges_to_be_removed)
            graph.add_edges_from(edges_to_be_added)

        # finally adding both the lines edges:
        graph.add_edges_from(extended_lines)
        
        return

    # 1. Do some exception handling to check the type of the entity is "door" or "window".
    ENTITY_TYPES_FOR_WHICH_WALLS_SHOULD_BE_EXTENDED = ('door', 'window')
    if not entity['type'] in ENTITY_TYPES_FOR_WHICH_WALLS_SHOULD_BE_EXTENDED:
        raise ValueError(
            f'Only entities with types in {ENTITY_TYPES_FOR_WHICH_WALLS_SHOULD_BE_EXTENDED} can be extended.')
        
    # DEBUG
    fill_str_tree(centre_lines=centre_lines)
        
    # 2. Get entity location:
    entity_location = entity["location"]

    # 3. Get nearest centre lines to that entity:
    nearest_line1, nearest_line2 = get_nearest_centre_lines_from_a_point(
                point = entity_location, centre_lines = centre_lines, entity_location= entity_location)
    
    
    # DEBUG:
    print('Got nearest centre lines')
    
    # 4. For the first two nearest lines, extend the wall:
    # nearest_line1, nearest_line2 = nearest_centre_lines[1], nearest_centre_lines[2]    # DEBUG
    extended_lines = get_extended_wall_lines_with_nearest_lines(
                        entity_location, graph, nearest_line1, nearest_line2)
    print('got extended lines.', extended_lines)
    
    print('adjusting graph: ', len(graph.edges))
    adjust_extended_lines(graph=graph, extended_lines=extended_lines, entity_location=entity_location)
    print('adjusted graph', len(graph.edges))
    return

for counter, current_entity in enumerate(windows):
    # DEBUG
    print('COUNTER', counter)
    
    extend_wall_lines_for_entity(entity=current_entity, centre_lines=centre_lines, graph=graph)

    print('Now plotting on msp', counter)
    dwg = ezdxf.new()
    msp = dwg.modelspace()

    for edge in graph.edges():
        msp.add_line(edge[0], edge[1])
    msp.add_circle(current_entity['location'], radius=2)

    dwg.saveas(f'dxfFilesOut/sample2/debug_dxf/extended_wall_lines/extended_wall_lines_windows_{counter}.dxf')
    print('saved: ', f'dxfFilesOut/sample2/debug_dxf/extended_wall_lines/extended_wall_lines_windows_{counter}.dxf')

window_counter = counter   
print('WINDOWS COMPLETE!!\n')
for counter, current_entity in enumerate(doors):
    counter = window_counter + counter
    # DEBUG
    print('COUNTER', counter)
    
    extend_wall_lines_for_entity(entity=current_entity, centre_lines=centre_lines, graph=graph)

    print('Now plotting on msp', counter)
    dwg = ezdxf.new()
    msp = dwg.modelspace()

    for edge in graph.edges():
        msp.add_line(edge[0], edge[1])
    msp.add_circle(current_entity['location'], radius=2)

    dwg.saveas(f'dxfFilesOut/sample2/debug_dxf/extended_wall_lines/extended_wall_lines_windows_{counter}.dxf')
    print('saved: ', f'dxfFilesOut/sample2/debug_dxf/extended_wall_lines/extended_wall_lines_windows_{counter}.dxf')

print('Success.')
