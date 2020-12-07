import shapely
import json
import pprint
from pillarplus.math import find_rotation, find_angle
# from test_clean_wall_lines import centre_lines, msp, dwg

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
try:
    with open('dxfFilesIn/identification_json/sample2.json') as identification_json_file:
        identification_json = json.load(identification_json_file)
        print('Success in reading the JSON file.')
except Exception:
    print('Failed to open identification JSON.')

windows = list(filter(lambda entity: entity['type']=='window', identification_json['entities']))
doors = list(filter(lambda entity: entity['type']=='door', identification_json['entities']))

print('windows:', len(windows))
pprint.pprint(windows)

print('doors:', len(doors))
pprint.pprint(doors)


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
                1.3 find the angle from the point, mid_point(point, closest_point), closest_point
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

    # 1. Do some exception handling to check the type of the entity is "door" or "window".
    ENTITY_TYPES_FOR_WHICH_WALLS_SHOULD_BE_EXTENDED = ('door', 'window')
    if not entity['type'] in ENTITY_TYPES_FOR_WHICH_WALLS_SHOULD_BE_EXTENDED:
        raise ValueError(
            f'Only entities with types in {ENTITY_TYPES_FOR_WHICH_WALLS_SHOULD_BE_EXTENDED} can be extended.')
        
    # 2. Get entity location:
    entity_location = entity["location"]

    # 3. Get nearest centre lines to that entity:
    nearest_centre_lines = get_nearest_lines_to_a_point(point = entity_location, lines = centre_lines)
    
    # 4. For the first two nearest lines, extend the wall:
    extended_lines = get_extended_wall_lines_with_nearest_lines(graph, nearest_line1, nearest_line2)