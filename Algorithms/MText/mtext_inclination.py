import ezdxf

def add_mtext(string: str, point, distance: float, rotation, msp):
    # Replace all the '/' with '/n'
    mtext_string = string.replace('/', '/n')
    # Replace all the '$' with '/n'
    mtext_string = string.replace('$', '/n')
    
    mtext = msp.add_mtext(mtext_string, dxfattribs={'style': 'OpenSans'})
    
    mt