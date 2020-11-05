"""
This module will contain functions for calculating the area and the volume of the walls.
That helps in the cost estimation of the project.

The main aim of this module is to automate the cost automation so that we can save tremendous time in between the projects.

Procedure of this module:
[Procedure]
"""

# Imports:


# Constants:


# Code:
def get_estimated_cost_data(*args, **kwargs):
    """This function gives the data to help in calculating the estimated cost.
    - Procedure of the function:
        [Procedure]
    [Args]
    [Returns]
    """
    # Set module up like constants and some parameters to be used throughout the module
    set_up_cost_estimation_module(*args, **kwargs)
    
    # Get wall groups, columns, door_details and window_details
    preprocessed_data = get_preprocessed_data(*args, **kwargs)
    
    # Get Wall groups:
    wall_groups = get_detected_wall_groups(preprocessed_data, *args, **kwargs)
    
    # Extend the wall groups:
    wall_groups = get_extended_wall_groups(wall_groups, *args, **kwargs)
    
    # Now estimate the costs:
    estimated_cost_data = get_estimated_costs(wall_groups, *args, **kwargs)
    
    # If required then process (or beautify) the estimated cost_data
    cleaned_estimated_cost_data = get_cleaned_estimated_cost_data(estimated_cost_data, *args, **kwargs)
    
    return cleaned_estimated_cost_data