conversion_factor = {
    'mm': 1.0,
    'inch': 0.0393701
}
centre_lines = get_centre_lines(
    msp, dwg, "", conversion_factor=conversion_factor['inch'],
    lines = cleaned_wall_lines)
pprint([centre_line.__dict__ for centre_line in centre_lines])
