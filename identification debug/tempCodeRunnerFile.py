all_blocks = []
for e in msp.query('INSERT'):
    block_name = e.dxf.name
    all_blocks.append(block_name)
print(set(all_blocks))    
