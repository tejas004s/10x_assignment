from app.planner import generate_trajectory, WallConfig, Obstacle

def test_simple_wall():
    config = WallConfig(width=5.0, height=3.0, obstacles=[])
    trajectory = generate_trajectory(config)
    assert len(trajectory) > 0
    assert all(wp.action in ["move", "paint"] for wp in trajectory)

def test_with_obstacle():
    config = WallConfig(
        width=5.0,
        height=3.0,
        obstacles=[Obstacle(x=2.0, y=1.0, width=1.0, height=1.0)]
    )
    trajectory = generate_trajectory(config)
    assert any(wp.x < 2.0 or wp.x > 3.0 for wp in trajectory)  # skips obstacle