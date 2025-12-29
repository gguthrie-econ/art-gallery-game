import numpy as np 
from shapely.geometry import Point, MultiPoint, LineString, Polygon, box, GeometryCollection


rng = np.random.default_rng()

def generate_floor_plan(num_rooms: int, min_overlap: float, dx: float, dy: float) -> Polygon:
    """
    Generates a polygon representing the floor plan of the art gallery.
    """

    # Build first room
    x, y = 0, 0
    rooms = box(x-dx, y-dy, x+dx, y+dy)

    # Add extra rooms
    for n in range(num_rooms-1):
        direction = rng.choice(['x_direction', 'y_direction'])

        if direction == 'x_direction':
            x += rng.choice([-(2-min_overlap)*dx, (2-min_overlap)*dx])
            y += rng.uniform( -(2-min_overlap)*dy, (2-min_overlap)*dy)
        else:
            x += rng.uniform( -(2-min_overlap)*dx, (2-min_overlap)*dx)
            y += rng.choice([-(2-min_overlap)*dy, (2-min_overlap)*dy])

        room = box(x-dx, y-dy, x+dx, y+dy)
        rooms = rooms.union(room)

    return Polygon(rooms.exterior)

def boundary_points(floor_plan: Polygon, padding: float, n_points: int) -> list[Point]:
    """
    Generates a list of points on the boundary of a rectangle surrounding the floor plan.
    This list is used when we calculate visibility polygons.
    """
    # Get the bounding box coordinates
    x_min, y_min, x_max, y_max = floor_plan.bounds
    # Calculate buffers
    dx, dy = padding * (x_max - x_min), padding * (y_max - y_min)
    # Create a rectangle from the augmented bounds
    bounding_box = box(x_min-dx, y_min-dy, x_max+dx, y_max+dy)

    # Calculate the total length of the boundary
    boundary_line = bounding_box.exterior # The boundary is a LinearRing
    total_length = boundary_line.length

    # Calculate the interval distance between points
    interval = total_length / n_points 

    # Create a list of distances along the line where points should be placed
    distances = [i * interval for i in range(int(total_length / interval))]

    # Use the interpolate method to find the point at each calculated distance
    return [boundary_line.interpolate(d) for d in distances]

def closest_point(guard: Point, floor_plan: Polygon, ref_point: Point) -> Point:
    """
    Finds the closest point to the guard that is on the floor_plan's boundary and on the line between the 
    guard and ref_point. This point is used when we generate visibility polygons.
    """
    line_temp = LineString([guard, ref_point])
    intersection_temp = floor_plan.boundary.intersection(line_temp)
    # Normalize the intersection result into a list of points
    if isinstance(intersection_temp, Point):
        # If it's a single Point, put it in a list
        geometries = [intersection_temp]
    elif isinstance(intersection_temp, (MultiPoint, GeometryCollection)):
        # If it's a MultiPoint or a collection, use .geoms to get the list
        geometries = list(intersection_temp.geoms)
    else:
        # Handle other cases (e.g., LineString or empty GeometryCollection)
        # If it's empty, geometries will be an empty list, which is fine for min()
        geometries = []

    # Find the closest point
    if geometries:
        closest_point = min(geometries, key=lambda p: guard.distance(p))
    else:
        # Handle the case where there was no intersection
        pass
    
    return closest_point

def visibility_polygon(guard: Point, floor_plan: Polygon, boundary_points: list[Point]) -> Polygon:
    """
    Generate the guard's visibility polygon, given the location of the guard, the floor plan, and a set of boundary points
    outside the floor_plan's boundary.
    """
    # Initialize list of vertices  
    vis_points=[]

    for ref_point in boundary_points:
        line_temp = LineString([guard, ref_point])
        intersection_temp = floor_plan.boundary.intersection(line_temp)

        # Normalize the intersection result into a list of points
        if isinstance(intersection_temp, Point):
            # If it's a single Point, put it in a list
            geometries = [intersection_temp]
        elif isinstance(intersection_temp, (MultiPoint, GeometryCollection)):
            # If it's a MultiPoint or a collection, use .geoms to get the list
            geometries = list(intersection_temp.geoms)
        else:
            # Handle other cases (e.g., LineString or empty GeometryCollection)
            # If it's empty, geometries will be an empty list, which is fine for min()
            geometries = []
            
        # Find the closest point
        if geometries:
            closest_point = min(geometries, key=lambda p: guard.distance(p))
            vis_points.append(closest_point)
            # ... continue with your logic
        else:
            # Handle the case where there was no intersection
            pass

    coords = [[p.x, p.y] for p in vis_points]

    # Create the Polygon
    return Polygon(coords)