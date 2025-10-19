import json
import xml.etree.ElementTree as ET

with open('data.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

with open('data.xml', 'r', encoding='utf-8') as f:
    xml_data = ET.parse(f)

print('JSON:')
for record in json_data:
    for key, value in record.items():
        print(f'{key}: {value}')
    print()

print('\nXML:')
root = xml_data.getroot()
for item in root.findall('item'):
    for child in item:
        print(f'{child.tag.replace("_", " ")}: {child.text}')
    print()
