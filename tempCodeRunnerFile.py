dwg.layers.new('IP-LAYER')
for polyline in polylines:
    # print('polyline: ', polyline)
    msp.add_lwpolyline(polyline, dxfattribs = {'layer': 'IP-LAYER',}) # 'color': random.randint(1, 7)
