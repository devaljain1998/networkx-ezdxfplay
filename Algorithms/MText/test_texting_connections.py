import json
import sys
import ezdxf
from pillarplus.texting import add_text_to_connection

# Read JSON File
json_file_paths = {
    'dra': 'Algorithms/MText/input/dra.json',
    'ws': 'Algorithms/MText/input/ws.json',
    'updated': 'Algorithms/MText/input/updated_identification.json',
}
json_file_path = json_file_paths['ws']

try:
    with open(json_file_path) as json_file:
        identification_json = json.load(json_file)
        print('Json Read file success.')
except Exception as e:
    print(f'Failed to load identification due to: {e}.')
    sys.exit(1)

# Declaring MSP and DWG
dwg = ezdxf.new('R2010')
msp = dwg.modelspace()

entities = {entity['number']: entity for entity in identification_json['entities']}
joints = {joint['number']: joint for joint in identification_json['joints']}
params = identification_json["params"]

stl = []
# Get connections and draw connections:
def get_and_draw_connections():
    connections = identification_json['connections']
    for connection in connections:
        source = entities.get(connection.get('source_number')) if connection['source_type'] == 'Entity' else joints.get(connection.get('source_number'))
        end = entities.get(connection.get('target_number')) if connection['target_type'] == 'Entity' else joints.get(connection.get('target_number'))
        
        stl.append({'source': source['location'], 'target': end['location']})
        if not (source['location'] is None or end['location'] is None):
            msp.add_line(source['location'], end['location'], dxfattribs = {'layer': 'ConnectionLayer'})
            connection['source_location'] = source['location']
            connection['target_location'] = end['location']
        
    return connections

# Add texting to the connections
connections = get_and_draw_connections()
for connection in connections:
    if connection.get('source_location') is not None and connection.get('target_location') is not None:
        print(f'Now writing text for connection: {connection}')
        print(f'Source Loc: {connection["source_location"]}, Target Loc: {connection["target_location"]}')
        add_text_to_connection(connection, connection['source_location'], connection['target_location'], params, msp, 'ConnectionTextingLayer')
        print('Success in addition of text!\n')
        
print('stl', stl)
output_file = 'dra_texting.dxf'
output_file_path = 'Algorithms/MText/output/'
dwg.saveas(output_file_path + output_file)