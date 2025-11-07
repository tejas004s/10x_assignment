import sqlite3
from typing import List
from app.planner import Waypoint

DB_PATH = "data/robot_trajectories.db"
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trajectories (
        id TEXT PRIMARY KEY,
        width REAL,
        height REAL,
        obstacle_count INTEGER,
        coverage_width REAL,
        coverage_percent REAL,
        path_length REAL,
        duration REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS waypoints (
        trajectory_id TEXT,
        x REAL,
        y REAL,
        action TEXT,
        FOREIGN KEY (trajectory_id) REFERENCES trajectories(id)
    )
    """)

    conn.commit()
    conn.close()

def save_trajectory(
    trajectory_id: str,
    width: float,
    height: float,
    coverage_width: float,
    obstacles: int,
    waypoints: List[Waypoint],
    duration: float
):
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM trajectories WHERE id = ?", (trajectory_id,))
        if cursor.fetchone():
            return 
        path_length = sum(
            abs(waypoints[i].x - waypoints[i-1].x)
            for i in range(1, len(waypoints))
            if waypoints[i].y == waypoints[i-1].y
        )
        coverage_percent = round((path_length * coverage_width) / (width * height) * 100, 2)

        cursor.execute("""
        INSERT INTO trajectories (id, width, height, obstacle_count, coverage_width, coverage_percent, path_length, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (trajectory_id, width, height, obstacles, coverage_width, coverage_percent, path_length, duration))

        cursor.executemany("""
        INSERT INTO waypoints (trajectory_id, x, y, action)
        VALUES (?, ?, ?, ?)
        """, [(trajectory_id, wp.x, wp.y, wp.action) for wp in waypoints])


def get_trajectory_by_id(trajectory_id: str) -> List[Waypoint]:
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT x, y, action FROM waypoints
        WHERE trajectory_id = ?
        ORDER BY y, x
        """, (trajectory_id,))
        rows = cursor.fetchall()

    return [Waypoint(x=row[0], y=row[1], action=row[2]) for row in rows]
