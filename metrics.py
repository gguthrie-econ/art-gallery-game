from itertools import combinations
from shapely import union_all

from state import GameState

def coverage_area(state: GameState) -> float | str:
    """Returns the proportion of the art gallery that is observed by at least one guard."""
    union_visi_polygons = union_all([g["visibility"] for g in state.guards])
    if state.floor_plan.area > 0:
        return union_visi_polygons.area / state.floor_plan.area
    else:
        return "-"

def overlap_area(state: GameState) -> float | str:
    """Returns the proportion of the art gallery that is observed by at least two guards."""

    # Generate all unique pairs of polygons
    all_intersections = []
    for poly_a, poly_b in combinations([g["visibility"] for g in state.guards], 2):
        # Calculate the intersection of each pair
        overlap = poly_a.intersection(poly_b)
        # Only keep non-empty intersections
        if not overlap.is_empty:
            all_intersections.append(overlap)
    # Combine all the resulting intersection geometries
    multi_overlap_area = union_all(all_intersections)
    if state.floor_plan.area > 0:
        return multi_overlap_area.area / state.floor_plan.area
    else:
        return "-"

def best_guard(state: GameState) -> float | str:
    """Returns the proportion of the art gallery that is observed by the guard with the largest visibility polygon."""
    if state.floor_plan.area > 0:
        vis_polygons = [g["visibility"] for g in state.guards]
        return max([poly.area for poly in vis_polygons]) / state.floor_plan.area
    else:
        return "-"

def worst_guard(state: GameState) -> float | str:
    """Returns the proportion of the art gallery that is observed by the guard with the smallest visibility polygon."""
    if state.floor_plan.area > 0:
        vis_polygons = [g["visibility"] for g in state.guards]
        return min([poly.area for poly in vis_polygons]) / state.floor_plan.area
    else:
        return "-"