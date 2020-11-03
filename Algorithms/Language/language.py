import ezdxf
import pillarplus.language_helper as pc
import logging
import csv
import os

this_dir = os.path.dirname(__file__)

# : Read parameters.csv (Generally common for most projects)
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
    logging.error(f'Parameters file "parameters.csv" is missing')
    exit()

print(params_dict)

# Setup logging file
try:
    logging.basicConfig(filename=this_dir + params_dict['ProjectFolder'] +
                        'identification.log',
                        filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')
except FileNotFoundError:
    print("Incorrect folder location in parameters.csv file")
    exit()

# read a dxf file
dwg = ezdxf.readfile(this_dir + params_dict['ProjectFolder'] + "drainage output.dxf")

# dwg.layers, dwg.blocks
# use dwg.layers to get layers
# use dwg.blocks to get properties of the block
# blocks has dxftype()=='INSERT'

# modelspace contains all entities
msp = dwg.modelspace()

#conversion_dict = pc.dict_reader('spanish','Translator.xlsx')
conversion_static_dict = pc.manual_hindi_dict
conversion_dynamic_dict = pc.manual_dynammic_hindi_dict 


text_entities = []
for entity in msp:
	# if entity.dxftype()=='TEXT':
	# 	text_to_convert = e.dxf.text
	# 	text_location = e.dxf.insert
	# 	text_height = e.dxf.height
	# 	rotation = e.dxf.rotation
	# 	width = e.dxf.width
	# 	text_entities.append(entity)

	if entity.dxftype()=='MTEXT':
		text_entities.append(entity)


for entity in text_entities:
	if entity.dxftype()=='MTEXT':
		text_to_convert = entity.plain_text();
		text_location = entity.dxf.insert
		text_height = entity.dxf.char_height
		rotation = entity.dxf.rotation
		width = entity.dxf.width
		text_to_convert = text_to_convert.replace('\n','')
		text_layer = entity.dxf.layer

		try:
			text_to_convert = text_to_convert.replace(' ','')
			converted_text =  pc.converted_result(text_to_convert,conversion_static_dict,conversion_dynamic_dict)
			print(converted_text,'-> Output')
		except Exception as e:
			print('Error: ' ,e)
			continue;
		new_entity = msp.add_mtext(converted_text,dxfattribs={'char_height': text_height, 'layer': text_layer,'rotation':rotation,'width':width})
		new_entity.set_location(text_location)

for entity in text_entities:
	msp.delete_entity(entity);

dwg.saveas(this_dir + params_dict['ProjectFolder'] + 'hindi.dxf')