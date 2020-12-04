import ezdxf

dwg = ezdxf.readfile('identification debug/in.dxf')
msp = dwg.modelspace()

all_blocks = []
for e in msp.query('INSERT'):
    block_name = e.dxf.name
    all_blocks.append(block_name)
print(set(all_blocks))    
    
# psp = dwg.layout('Layout2')
# for e in psp.query('INSERT'):
#     block_name = e.dxf.name
#     all_blocks.append(block_name)

# for block in dwg.blocks:
#     print(block.dxf.name)
#     print(block.__dict__)
#     print(block.entity_space, len(block.entity_space))
#     print(block.block_record)
    
#     if block.dxf.name == 'CCDD':
#         print('block_record_items: ', block.block_record.__dict__)
#         print('block.block_record.block_layou')
#         for item in block.entity_space:
#             print(item)

# print(set(all_blocks))    