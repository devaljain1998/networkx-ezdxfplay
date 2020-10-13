        boundry_points = [(point[0], point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_lower_height), (point[0] + x_extra_distance, point[1] + y_extra_height), (point[0], point[1] + y_extra_height), (point[0], point[1] + y_lower_height)]
        boundryline = msp.add_lwpolyline(boundry_points, dxfattribs={'layer': 'TextLayerBoundry'})
                
        # proper positioning
        # Positioning x coordinate:
        point[0] += (0 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (-110 * conversion_factor)
        # Increasing the Y coordinate:
        point[1] += (70 * conversion_factor) if 0 <= abs(
            degrees(slant_line_angle)) <= 90 else (70 * conversion_factor)
