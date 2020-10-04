import ezdxf


def draw_hatch_and_delete_bock(doc, data, path):
    """
    Function to call delete_block and make_hatch function
    Parameters:
        doc (dxf file): dxf file
        data (csv data): csv data of blocks to be deleted
        folder_name (string): folder in output is to be made
    Returns:
        None
    """
    blocks_name = []  # storing all the block names
    header = True  # boolean to ignore header

    for row in data:
        if header:
            header = False
        else:
            blocks_name.append(row[0])

    msp = doc.modelspace()
    # print("about to delete", blocks_name)
    log1 = delete_block(blocks_name, doc)
    # print("block deleted")
    log2 = make_layer(doc, msp)
    # print("saving in", path + '/hatch_output.dxf')

    doc.saveas(path + '/hatch_output.dxf')
    print("ADITYA")
    # # print("file saved")
    return log1, log2


def delete_block(blocks_name, doc):
    """
    Function to delete the block with the given name
    Takes a list of names of blocks and deletes them from the doc
    Parameter:
        blocks_name (list): list of blocks to be deleted
    Return:
        string: log info
    """
    msp = doc.modelspace()
    blocks_name.append('*U26')
    for block_ref in msp.query('INSERT'):
        # getting the block reference of all the blocks
        # # # print("block", block_ref.dxf.name, "in", block_ref.dxf.layer)
        if block_ref.dxf.name in blocks_name or block_ref.dxf.name == '*U26':
            # # # print("deleting", block_ref.dxf.name)
            try:
                # Try for the name of the block
                # If the block is already deleted, function doc.blocks.delete_block might raise error
                # print("about to delete", block_ref.dxf.name)
                doc.blocks.delete_block(name=block_ref.dxf.name, safe=False)
                # removing the name from the list
                # as it is no longer required
                # so that search can be faster
                blocks_name.remove(block_ref.dxf.name)
            except ezdxf.lldxf.const.DXFKeyError:
                # # # print("block", block_ref.dxf.name, "already deleted")
                continue
            except:
                print("could not delete", block_ref.dxf.name)

    return 'SUCCESS'  # A$C4CEA6FF1


def make_layer(doc, msp):
    """
    Makes hatch in the layers of name starting with 'PP-'
    Takes the ezdxf doc file as input
    Parameter:
        doc (dxf file): input file
    Returns:
        string: log info
    """

    success = 0
    # defining hatch
    hatch = msp.add_hatch(color=92, dxfattribs={'hatch_style': 0,'color':2})
    # setting the pattern
    hatch.set_pattern_fill('ANSI31', scale=20)

    for layer in doc.layers:
        # getting and iterating over all the layers
        if layer.dxf.name[0: 3] == 'PP-' and 'OUTER' not in layer.dxf.name:
            # hatching the layers with name beginning with 'PP-'
            # ignoring the outer boundary named 'PP-OUTER'
            # # print("hatching", layer.dxf.name)
            # if name starts with 'PP-'
            # neglecting the outer boundary block named 'PP-OUTER'

            # # # print("layer", layer.dxf.name)
            polylines = msp.query('LWPOLYLINE[layer=="%s"]' % layer.dxf.name)
            polyline_exists = False
            for polyline in polylines:
                # getting all the polylines
                polyline_exists = True
                # # # print("polyline found")
                # getting the points
                points = polyline.get_points()
                path = []
                for point in points:
                    path.append((point[0], point[1], point[2]))

                # # # print(points)
                hatch.paths.add_polyline_path(path, is_closed=1)
                success = success + 1
            if not polyline_exists:
                # # print("polyline does not exist in layer", layer.dxf.name)
                continue

    # # print("Total", success, "hatches were made")
    return 'SUCCESS,' + str(success) + ' Hatches are made'
