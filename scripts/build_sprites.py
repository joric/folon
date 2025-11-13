import csv,json,re,os,base64

def jsondump(obj, f, ensure_ascii=False, indent=2, sort_keys=True, maxlen=120):
    def fmt(o, level=0):
        s = json.dumps(o, ensure_ascii=False, sort_keys=sort_keys, separators=(',', ': '))  # Use the parameter
        if len(s) <= maxlen:
            return s
        pad = ' ' * (indent * level)
        pad_in = ' ' * (indent * (level + 1))
        if isinstance(o, dict):
            # Sort the items if sort_keys is True
            items = o.items()
            if sort_keys:
                items = sorted(items, key=lambda x: str(x[0]))
            items = [f'{json.dumps(k, ensure_ascii=False)}: {fmt(v, level + 1)}' for k, v in items]
            return '{\n' + ',\n'.join(pad_in + i for i in items) + '\n' + pad + '}'
        if isinstance(o, list):
            items = [fmt(x, level + 1) for x in o]
            return '[\n' + ',\n'.join(pad_in + i for i in items) + '\n' + pad + ']'
        return s
    f.write(fmt(obj) + '\n')

def map_symbols():
    symbols = csv.reader(open('swf_export/csv/symbols.csv'), delimiter=';')

    shapes = {}
    lookup = {}

    for p in symbols:
        i, name = p
        i = int(i)
        shapes[name] = i

    # load markers

    data = json.load(open('../data/markers.json'))
    markers = set()

    for o in data['features']:
        p = o.get('properties',{})
        if p.get('signature')=='STAT':
            t = p.get('type')
            if t:
                markers.add(t)

    # most markers can be mapped by TNAM but not these
    custom_mapping = {
        "Brotherhood of Steel": "BoSMarker",
        "Metro Station": "MetroMarker",
        "Factory / Industrial Site": "FactoryMarker",
        "Low-Rise Building": "LowRiseMarker",
        "Office / Civic Building": "OfficeMarker",
        "Mechanist LairRaider settlementVassal settlementPotential Vassal settlement": "MechanistMarker",
        "Brownstone Townhouse": "BrownstoneMarker",
        "Sewer / Utility Tunnels": "SewerMarker",
        "Ruins - Urban": "UrbanRuinsMarker",
        "Ruins - Town": "TownRuinsMarker",
        "Natural Landmark": "LandmarkMarker",
        "Gov't Building / Monument": "MonumentMarker",
        "Custom 66": "RaiderSettlementMarker",
        "Custom 67": "VassalSettlementMarker",
        "Custom 69": "BottlingPlantMarker",
        "Custom 70": "GalacticMarker",
        "Custom 71": "HubMarker",
        "Custom 73": "MonorailMarker",
        "Custom 74": "RidesMarker",
        "Custom 75": "SafariMarker",
        "Custom 77": "POIMarker",
        "Custom 79": "OperatorsMarker",
        "Custom 80": "PackMarker",
    }

    mapping = {}

    for m in markers:
        tag = re.sub(r'[^A-Za-z0-9]', '', m) + 'Marker'

        keys = list(shapes.keys())

        mapping[m] = {}

        if m in custom_mapping:
            k = custom_mapping[m]

            mapping[m] = {"class": k, "index": shapes[k] }

            del shapes[ k ]

        for k in keys:
            if k==tag:
                mapping[m] = {"class": tag, "index": shapes[k] }
                del shapes[k]

    jsondump(mapping, open('swf_mapping.json','w'), ensure_ascii=False, indent=2, sort_keys=True)

    #print('-- unmapped shapes:')
    #for k in shapes: print(k)
    #print('-- unmapped TNAM:')

    for k in mapping:
        if len(mapping[k])==0:
            print(k)

def convert_svg():
    pass
    '''
    import cairosvg # pip install cairosvg
    from PIL import Image
    from io import BytesIO

    fname = 'swf_export/shapes/126.svg'

    #png_bytes = cairosvg.svg2png(url=fname, output_width=256, output_height=256)
    #svg_data = open(fname, 'rb').read()
    #png_data = cairosvg.svg2png(bytestring=svg_data)
    #img = Image.open(BytesIO(png_data))

    png_bytes = cairosvg.svg2png(url=fname, output_width=256, output_height=256)
    img = Image.open(BytesIO(png_bytes)).convert('RGBA')
    img.save('output.png')

    # from svglib.svglib import svg2rlg
    # from reportlab.graphics import renderPM
    #drawing = svg2rlg(fname)
    #renderPM.drawToFile(drawing, "output.png", fmt="PNG", dpi=512)
    '''

    #for k,v in mapping.items(): print(k, v['index'])

def update_types():
    data = json.load(open('../data/types.json'))

    def process(data):
        if type(data) is not dict: return
        for k, obj in data.items():
            if k in mapping:
                #obj['marker'] = mapping[k]['class']
                #obj['index'] = mapping[k]['index']
                del obj['marker']
            process(obj)

    process(data)

    json.dump(data, open('types.json','w'), ensure_ascii=False, indent=2, sort_keys=True)

def update_icons():
    mapping = json.load(open('swf_mapping.json'))
    types = json.load(open('../data/types.json'))
    icons = json.load(open('../data/icons.json'))

    def process(data):
        if type(data) is not dict: return

        for k, obj in data.items():
            if k in mapping:
                image = mapping[k]['class']
                index = mapping[k]['index']

                icon = obj['icon']

                obj['icon'] = image

                #icons[icon]['image'] = image

                content = icons[icon]

                del icons[icon]

                icons[image] = content

                icons[image]['image'] = f'{index}.svg'

            process(obj)

    process(types)

    jsondump(icons, open('icons.json','w'), ensure_ascii=False, indent=2, sort_keys=True)

    jsondump(types, open('types.json','w'), ensure_ascii=False, indent=2, sort_keys=True)


def build_js():
    path = 'swf_export/shapes/'
    with open('icons.js', 'w', encoding='utf-8') as out:
        out.write('export const icons = {\n')

        with os.scandir(path) as entries:
            for entry in sorted(entries, key=lambda e: natural_key(e.name)):
                name = entry.name
                if name.endswith('.svg'):
                    data = open(entry.path, 'r').read()
                    data = clean_data(data)
                    encoded = base64.b64encode(data.encode('utf-8')).decode()
                    out.write(f"  '{name[:-4]}': 'data:image/svg+xml;base64,{encoded}',\n")
            out.write('};\n')


import xml.etree.ElementTree as ET

def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def strip_ns_and_whitespace(elem):
    # Remove namespace prefix from tag
    if '}' in elem.tag:
        elem.tag = elem.tag.split('}', 1)[1]
    # Remove unwanted attributes
    for attr in list(elem.attrib):
        if '}' in attr or attr in ['height', 'width', 'ffdec:objectType']:
            del elem.attrib[attr]
    # Strip text and tail whitespace
    if elem.text:
        elem.text = elem.text.strip()
    if elem.tail:
        elem.tail = elem.tail.strip()
    # Recurse into children
    for child in elem:
        strip_ns_and_whitespace(child)

def clean_data(xml_string: str) -> str:
    root = ET.fromstring(xml_string)
    strip_ns_and_whitespace(root)
    # Convert back to string
    data = ET.tostring(root, encoding='unicode', method='xml')
    # Convert quotes to single quotes
    data = data.replace('"', "'")
    # Remove any remaining line breaks or extra spaces
    data = re.sub(r">\s+<", "><", data)
    return data.strip()

def build_shapes(path='export/shapes'):
    shapes = {}
    with os.scandir(path) as entries:
        for entry in sorted(entries, key=lambda e: natural_key(e.name)):
            if entry.is_file() and entry.name.lower().endswith('.svg'):
                with open(entry.path, encoding='utf-8') as f:
                    data = f.read()
                    shapes[entry.name.replace('.svg','')] = clean_data(data)
    json.dump(shapes, open('shapes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2, sort_keys=False)

def clean_icons():
    icons = json.load(open('../data/icons.json'))
    for k in icons:
        if 'image' in icons[k]:
            del icons[k]['image']
    jsondump(icons, open('icons.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2, sort_keys=True)

def clean_svg(data):
    return data

def build_sprites(path='export/sprites'):
    sprites = {}

    def build_shapes(path):
        shapes = []
        for e in sorted(os.scandir(path), key=lambda e: natural_key(e.name)):
            s = open(e.path,'r').read()
            m = re.search(r'ffdec:characterId="(\d+)"', s)
            if m:
                shapes.append(int(m[1]))
        return shapes

    for e in sorted(os.scandir(path), key=lambda e: natural_key(e.name)):
        m = re.match(r'DefineSprite_(\d+)_(\w+Marker)', e.name)
        if m:
            i, name = int(m[1]), m[2]
            #print(i, name)
            shapes = build_shapes(e.path)
            if len(shapes)==2:
                sprites[name] = {"id": i, "shapes": shapes}

    jsondump(sprites, open('sprites.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2, sort_keys=True)


    icons = json.load(open('../data/icons.json'))

    for k in icons:
        if 'image' in icons[k]:
            del icons[k]['image']

        if k in sprites:
            #icons[k]['sprites'] = {"images": {"active": f'{sprites[k]['shapes'][0]}.png', "default": f'{sprites[k]['shapes'][1]}.png'}}
            icons[k]['sprites'] = sprites[k]['shapes']

    jsondump(icons, open('icons.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2, sort_keys=True)

if __name__ == '__main__':
    #clean_icons()
    #map_symbols()
    #update_icons()
    #build_svg()
    #build_js()

    build_sprites()
    #build_shapes()


