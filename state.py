from shapely.geometry import Point, Polygon

class GameState:
    def __init__(self, floor_plan: Polygon, boundary_points: list[Point], settings: dict):
        self.floor_plan = floor_plan
        self.boundary_points = boundary_points
        self.settings = settings
        self.guards = []
        self.next_guard_id = 1

    def is_finished(self):
        return len(self.guards) == self.settings["max_guards"]
    
    def show_results(self):
        return self.guards and (self.is_finished() or not self.settings["blind"])