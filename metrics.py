from shapely.geometry import Polygon
from shapely import union_all, intersection_all
from itertools import combinations

def coverage_area(floor_plan: Polygon, visi_polygons: list[Polygon]) -> float | str:
    """Returns the proportion of the art gallery that is observed by at least one guard."""
    union_visi_polygons = union_all(visi_polygons)
    if floor_plan.area > 0:
        return union_visi_polygons.area / floor_plan.area
    else:
        return "-"

def overlap_area(floor_plan: Polygon, visi_polygons: list[Polygon]) -> float | str:
    """Returns the proportion of the art gallery that is observed by at least two guards."""

    # Generate all unique pairs of polygons
    all_intersections = []
    for poly_a, poly_b in combinations(visi_polygons, 2):
        # Calculate the intersection of each pair
        overlap = poly_a.intersection(poly_b)
        # Only keep non-empty intersections
        if not overlap.is_empty:
            all_intersections.append(overlap)
    # Combine all the resulting intersection geometries
    multi_overlap_area = union_all(all_intersections)
    if floor_plan.area > 0:
        return multi_overlap_area.area / floor_plan.area
    else:
        return "-"

def best_guard(floor_plan: Polygon, visi_polygons: list[Polygon]) -> float | str:
    """Returns the proportion of the art gallery that is observed by the guard with the largest visibility polygon."""
    if floor_plan.area > 0:
        return max([poly.area for poly in visi_polygons]) / floor_plan.area
    else:
        return "-"

def worst_guard(floor_plan: Polygon, visi_polygons: list[Polygon]) -> float | str:
    """Returns the proportion of the art gallery that is observed by the guard with the smallest visibility polygon."""
    if floor_plan.area > 0:
        return min([poly.area for poly in visi_polygons]) / floor_plan.area
    else:
        return "-"