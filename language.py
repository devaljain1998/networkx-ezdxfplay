import ezdxf
import pillarplus.language_helper as pc
import logging
import csv
import os
import math

this_dir = os.path.dirname(__file__)
print(this_dir)
# : Read parameters.csv (Generally common for most projects)
try:
    params_dict = {}
    with open(this_dir + '/parameters.csv') as csv_file:
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
    
MTEXT_ATTACHMENT_POINTS = {
    "MTEXT_TOP_LEFT":	1,
    "MTEXT_TOP_CENTER":	2,
    "MTEXT_TOP_RIGHT":	3,
    "MTEXT_MIDDLE_LEFT":	4,
    "MTEXT_MIDDLE_CENTER":	5,
    "MTEXT_MIDDLE_RIGHT":	6,
    "MTEXT_BOTTOM_LEFT":	7,
    "MTEXT_BOTTOM_CENTER":	8,
    "MTEXT_BOTTOM_RIGHT":	9,
}

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
    if entity.dxftype()=='TEXT':
    	# text_to_convert = e.dxf.text
    	# text_location = e.dxf.insert
    	# text_height = e.dxf.height
    	# rotation = e.dxf.rotation
    	# width = e.dxf.width
        text_entities.append(entity)

    if entity.dxftype()=='MTEXT':
        text_entities.append(entity)


for entity in text_entities:
    if entity.dxftype()=='MTEXT':
        text_to_convert = entity.plain_text();
        print(text_to_convert, 'INPUT->')
        text_location = entity.dxf.insert
        text_to_convert = text_to_convert.replace('\n','')

        try:
            text_to_convert = text_to_convert.replace(' ','')
            converted_text =  pc.converted_result(text_to_convert,conversion_static_dict,conversion_dynamic_dict)
            entity.text = converted_text
            print(converted_text,'-> Output')
        except Exception as e:
            print('Error: ' ,e)
            continue;
        
    elif entity.dxftype() == 'TEXT':
        print('TEXT')
        text_to_convert = entity.dxf.text
        print(text_to_convert, 'INPUT->')
        text_location = entity.dxf.insert
        text_to_convert = text_to_convert.replace('\n','')

        try:
            text_to_convert = text_to_convert.replace(' ','')
            print('entity_text: ', entity.dxf.text)
            converted_text =  pc.converted_result(text_to_convert,conversion_static_dict,conversion_dynamic_dict)
            entity.dxf.text = converted_text
            print('entity_text: ', entity.text)
            print(converted_text,'-> Output')
        except Exception as e:
            print('Error: ' ,e)
            continue;
        

dwg.saveas(this_dir + params_dict['ProjectFolder'] + 'hindi.dxf')