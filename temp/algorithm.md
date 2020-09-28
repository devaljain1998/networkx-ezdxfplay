SLEEVE LINES:

1. Get all polylines from layer 'PP-BEAM'.
2. Create lines from all the polylines:<br>
```python    
def get_lines(polylines) -> list[tuple]:
    # 1. Break polylines into lines
    # 2. Check if the line is decreasing on X.
        # 2.1 If it is decreasing then reverse the line.
    # 3. Check in the end if the polyline is forming a closed figure:
        # 3.1 If yes then connect the first and last points too.
    return lines
```
3. Sort the lines: ```lines.sort()```
4. Find and form buckets of slopes from lines:<br>
```python
def get_slopes(lines) -> dict:
    
    return slopes
```