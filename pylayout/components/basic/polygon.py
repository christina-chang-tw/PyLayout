import numpy as np

def regular_polygon(x: float, y: float, radius: float, angle: float, angle_resolution: float=2.5, start_angle: float=0) -> np.ndarray:
    """
    Returns the points of a regular polygon.

    Args:
        x [float]: x coordinate of the center.
        y [float]: y coordinate of the center.
        radius [float]: radius of the polygon.
        angle [float]: angle of the polygon.
        angle_resolution [float]: angle resolution.
        start_angle [float]: starting angle.

    Returns:
        np.ndarray: points of the regular polygon.
    """
    num_points = int(360 / angle_resolution) + 1
    angles = np.linspace(start_angle, start_angle + angle, num_points)
    points = np.column_stack((x + radius * np.cos(angles), y + radius * np.sin(angles)))
    return points