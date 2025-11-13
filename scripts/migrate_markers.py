import json


data = json.load(open('../data/markers-1.02.json','r'))

f = open('markers-1.02.json','w')

cells = {}

for entry in data['features']:
    prop = entry['properties']
    if prop['form_id']=='00000010':
        prop['type'] = prop['description']
        prop['signature'] = 'STAT'
    else:
        prop['signature'] = prop['description']

    del prop['description']

    if 'cell' in prop and 'cell_name' in prop:
        if prop['cell_name']:
            cells[prop['cell']] = prop['cell_name']
        del prop['cell_name']

data['cells'] = cells

json.dump(data, f, indent=2, sort_keys=False)

