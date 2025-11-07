from app.database import save_trajectory, get_trajectory_by_id
from app.planner import Waypoint

def test_save_and_retrieve():
    trajectory_id = "test123"
    waypoints = [
        Waypoint(x=0.0, y=0.0, action="move"),
        Waypoint(x=1.0, y=0.0, action="paint")
    ]
    save_trajectory(
        trajectory_id=trajectory_id,
        width=5.0,
        height=3.0,
        coverage_width=0.15,
        obstacles=0,
        waypoints=waypoints,
        duration=0.5
    )
    retrieved = get_trajectory_by_id(trajectory_id)
    assert len(retrieved) == 2
    assert retrieved[0].action == "move"