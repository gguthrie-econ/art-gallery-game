from state import GameState
from geometry import boundary_points, generate_floor_plan, visibility_polygon
from shapely.geometry import Point

from config import FLOOR_PLAN_BUFFER, NUM_BDRY_PTS, DX, DY

def new_game(settings):
    floor_plan = generate_floor_plan(
            num_rooms = settings["num_rooms"],
            min_overlap = settings["min_overlap"],
            dx=DX,
            dy=DY
        )
    bdry_pts = boundary_points(floor_plan, FLOOR_PLAN_BUFFER, NUM_BDRY_PTS)  
    return GameState(floor_plan, bdry_pts, settings)

def add_guard(state, x, y):
    if not state.floor_plan.contains(Point(x, y)):
        raise ValueError("The guard must be inside the art gallery. Try again with new coordinates.")

    if len(state.guards) >= state.settings["max_guards"]:
        raise ValueError("Maximum number of guards reached")

    vis_poly = visibility_polygon(
        Point(x, y),
        state.floor_plan,
        state.boundary_points,
    )

    guard = {
        "id": state.next_guard_id,
        "x": x,
        "y": y,
        "visibility": vis_poly,
    }

    state.guards.append(guard)
    state.next_guard_id += 1
    return state

def remove_last_guard(state):
    if state.guards:
        state.guards.pop()
        state.next_guard_id -= 1
    return state

def remove_all_guards(state):
    state.guards = []
    state.next_guard_id = 1
    return state