from pydantic import BaseModel
from typing import List

class Obstacle(BaseModel):
    x: float  # bottom-left corner
    y: float
    width: float
    height: float

class WallConfig(BaseModel):
    width: float
    height: float
    coverage_width: float = 0.15  # default robot sweep width
    obstacles: List[Obstacle]

class Waypoint(BaseModel):
    x: float
    y: float
    action: str  # "move" or "paint"
def generate_trajectory(config: WallConfig) -> List[Waypoint]:
    waypoints = []
    y = config.coverage_width / 2
    direction = 1  # 1 = left to right, -1 = right to left

    while y < config.height:
        x_start = 0 if direction == 1 else config.width
        x_end = config.width if direction == 1 else 0

        # Check if this stripe intersects any obstacle
        stripe_segments = get_stripe_segments(x_start, x_end, y, config)

        for seg_start, seg_end in stripe_segments:
            waypoints.append(Waypoint(x=seg_start, y=y, action="move"))
            waypoints.append(Waypoint(x=seg_end, y=y, action="paint"))

        y += config.coverage_width
        direction *= -1

    return waypoints

def get_stripe_segments(x_start, x_end, y, config: WallConfig):
    segments = [(min(x_start, x_end), max(x_start, x_end))]

    for obs in config.obstacles:
        if obs.y <= y <= obs.y + obs.height:
            new_segments = []
            for seg_start, seg_end in segments:
                # Left segment
                if obs.x > seg_start:
                    new_segments.append((seg_start, min(obs.x, seg_end)))
                # Right segment
                if obs.x + obs.width < seg_end:
                    new_segments.append((max(obs.x + obs.width, seg_start), seg_end))
            segments = new_segments

    return segments

# wall = WallConfig(
#     width=5.0,
#     height=5.0,
#     obstacles=[Obstacle(x=2.0, y=2.0, width=0.25, height=0.25)]
# )

# trajectory = generate_trajectory(wall)
# for wp in trajectory[:5]:
#     print(wp)