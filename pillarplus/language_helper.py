import csv


def dict_reader(language, csv_name):  # Useless
    wb = xlrd.open_workbook(csv_name)
    sheet = wb.sheet_by_index(0)
    lines = []
    for i in range(sheet.nrows):
        line = []
        for j in range(sheet.ncols):
            line.append(sheet.cell_value(i, j))
        lines.append(line)

    line_count = 0
    lagnuage_to_column = {
        'hindi': 1,
        'spanish': 2,
    }
    column = lagnuage_to_column[language]
    conversion_dict = {}
    for line in lines:
        if line_count == 0:
            #line_count += 1
            pass
        else:
            conversion_dict[line[0]] = line[column]
        line_count += 1
    return conversion_dict
    # with open(csv_name) as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter=',')
    #     line_count = 0
    #     lagnuage_to_column = {
    #         'hindi': 1,
    #         'spanish': 2,
    #     }
    #     column = lagnuage_to_column[language]
    #     conversion_dict = {}
    #     for line in csv_reader:
    #         if line_count == 0:
    #             #line_count += 1
    #             pass
    #         else:
    #             conversion_dict[line[0]] = line[column]
    #         line_count += 1
    #     return conversion_dict

# static_text_to_convert ="welcome"
# # def Parameter(static_text_to_convert):
# if static_text_to_convert in hindi_dict:
#     converted_text = hindi_dict.get(static_text_to_convert)
#     print(converted_text)


def converted_result(text_to_be_converted, conversion_static_dict, conversion_dynamic_dict):
    converted_element_list = []
    new_list = []

    # DEBUGGING:
    if text_to_be_converted == 'COPF':
        debug_mode = True

    for key in conversion_static_dict.keys():
        english_word = key.replace(' ', '')
        if english_word.lower() in text_to_be_converted.lower():
            try:
                index = text_to_be_converted.index(english_word)
            except:
                try:
                    index = text_to_be_converted.index(english_word.lower())
                except:
                    index = text_to_be_converted.index(english_word.upper())
            new_word = conversion_static_dict[key]
            converted_element_list.append((new_word, index))

        text_to_be_converted = text_to_be_converted.replace(english_word, '{}')

    for key in conversion_dynamic_dict.keys():
        if text_to_be_converted.lower() == key.replace(' ', '').lower():
            converted_text = conversion_dynamic_dict[key]
        # Handling the case of Phi
        elif text_to_be_converted[1:].lower() == key.replace(' ', '')[1:].lower():
            converted_text = conversion_dynamic_dict[key]

    try:
        converted_text
    except NameError:
        print('\n\ndynamic not found for:', text_to_be_converted,
              '--------------------------------\n\n')
        converted_text = '{}'
    # converted_text = converted_element_list[len(converted_element_list) - 1]

    # sorted the list
    converted_element_list.sort(key=lambda x: x[1])
    # converted output
    conversion_flag = False
    for word in converted_element_list:
        for text in range(len(converted_text)):
            if converted_text[text] == '{' and converted_text[text + 1] == '}':
                conversion_flag = True
                converted_text = converted_text[: text] + \
                    word[0] + converted_text[text + 2:]
                break
            
    if not conversion_flag:
        return text_to_be_converted

    return(converted_text)


manual_hindi_dict_1 = {
    "Ø 25MM": "Ø 25 mi mi",
    "Ø 32MM": "Ø 32 mi mi",
    "Ø 20MM": "Ø 20 mi mi",
    "HWS PIPE": "garam pani ka pipe",
    "CWS PIPE": "thande pani ka pipe",
    "CISTERN": "cistern",
    "HEALTH FAUCET": "helth focit",
    "SHOWER": "shover",
    "BALL VALVE": "bal valve",
    "SINK": "cynk",
    "WASH BASIN": "wash becin",
    "CEILING": "chhat",
}

manual_dynammic_hindi_dict_1 = {
    "{}": "{}",
    "{} {} ": "{} {}",
    "{} {} THROUGH WALL CHASE TO {}": "{} aur {}  diwar me hote hue {} me",
    "{} {} THROUGH WALL CHASE FROM {}": "{} ke {}  diwar me hote hue {} me",
    "{} {} RUNNING  IN {}": "{} ke {} hote hue {} se",
}

'''
manual_hindi_dict = {
    "Ø 25MM": "Ø 25 mi mi",
    "Ø 32MM": "Ø 32 mi mi",
    "Ø 20MM": "Ø 20 mi mi",
    "HWS PIPE": "गरम पानी का पाईप",
    "CWS PIPE": "ठंडे पानी का पाईप",
    "CISTERN": "सिस्ट्रन",
    "HEALTH FAUCET": "हैल्थ फोसित",
    "SHOWER": "शावर",
    "BALL VALVE": "बॉल वॉल्व",
    "SINK": "सिन्क",
    "WASH BASIN": "वॉश बेसिन",
    "CEILING": "छत",
}
manual_dynammic_hindi_dict = {
    "{}": "{}",
    "{} {}": "{} {}",
    "{} {} THROUGH WALL CHASE TO {}": "{} और {}  दिवार में होते हुए {} में",
    "{} {} THROUGH WALL CHASE FROM {}": "{} के {}  दिवार में होते हुए {} से",
    "{} {} RUNNING  IN {}": "{} के {} होते हुए {} से",
}
'''

manual_hindi_dict = {
    "P.T.": "pee tee",
    "BT": "bee tee",
    "WWP": "doublu doublu pee",
    "50": "5",
    "110": "11",
    "bath": "Baaath",
    "UP": "uppppp",
    "SHOWER": "शावर",
    "BALL VALVE": "बॉल वॉल्व",
    "SINK": "सिन्क",
    "WASH BASIN": "वॉश बेसिन",
    "CEILING": "छत",
}
manual_dynammic_hindi_dict = {
    "{}": "{}",
    "∅{}MM{}": "∅{} emem {}",
    "{} {}": "{} {}",
    "{} {} THROUGH WALL CHASE TO {}": "{} और {}  दिवार में होते हुए {} में",
    "{} {} THROUGH WALL CHASE FROM {}": "{} के {}  दिवार में होते हुए {} से",
    "{} {} RUNNING  IN {}": "{} के {} होते हुए {} से",
}
