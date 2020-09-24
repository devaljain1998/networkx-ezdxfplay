import ezdxf

dwg = ezdxf.new('R2010')
msp = dwg.modelspace()

filePath = 'dxfFilesOut/'

#msp.add_line((10, 10), (20, 10), dxfattribs={'layer': 'MyLines'})
#msp.add_line((10, 10), (10, 20), dxfattribs={'layer': 'MyLines'})


# msp.add_circle(center=(10, 10),
#                radius=2,
#                dxfattribs={'layer': 'MyLines'}
#                )

# msp.add_circle(center=(10, 10),
#                radius=2,
#                dxfattribs={'layer': 'MyLines'}
#                )


'''
msp.add_arc(center=(10, 10),
radius=10,
start_angle=180, # shortcut
end_angle=135, # shortcut
dxfattribs={'layer': 'MyLines'}
)

msp.add_ellipse(
center=(10, 10),
major_axis=(5,0),
ratio=.5,
dxfattribs={'layer': 'MyLines'}
)
'''

# msp.add_arc(center=(10, 10),
# radius=10,
# start_angle=180, # shortcut
# end_angle=235, # shortcut
# dxfattribs={'layer': 'MyLines'}
# )

#Adding a MTEXT entity:
def test_adding_multiline_text():
    multiline_txt = """
        This is a sample multiline.
        The multiline text has a type of 
        'MTEXT' in the software.
        Let's try it out.
    """
    mtext = msp.add_mtext(multiline_txt, dxfattribs={'style': 'OpenSans'})
    #Setting the position:
    mtext.set_location((50, 10))
    
    print('Success in adding multiline text')
    
# test_adding_multiline_text()

def test_creation_of_dimensions():
    print('Testing the dimensioning')
    
    # Add a LINE entity, not required
    msp.add_line((0, 0), (3, 0))
    # Add a horizontal dimension, default dimension style is 'EZDXF'
    dim = msp.add_linear_dim(base=(3, 2), p1=(0, 0), p2=(3, 0))
    # Necessary second step, to create the BLOCK entity with the dimension geometry.
    # Additional processing of the dimension line could happen between adding and
    # rendering call.
    dim.render()
    
    
    #testing with another dimension:
    msp.add_line((15, 15), (75, 15))
    dim2 = msp.add_linear_dim(
        base = (3, 2), 
        p1 = (15, 15), p2 = (75, 15), 
        override = {'dimtad' : 1}
        )
    dim2.render()
    
    print('Dimension is printed')
    
# test_creation_of_dimensions()


def test_creation_of_hatch():
    print('Testing Hatch')
    hatch = msp.add_hatch(color=3)  # by default a solid fill hatch with fill color=7 (white/black)

    # every boundary path is always a 2D element
    # vertex format for the polyline path is: (x, y[, bulge])
    # there are no bulge values in this example
    hatch.paths.add_polyline_path([(0, 0, 1), (10, 0), (10, 10, -0.5), (0, 10)], is_closed=1)    
    print('Hatch Test Success')

test_creation_of_hatch()

# save dwg files as a dxf file
dwg.saveas(filePath + 'created_arc.dxf')
