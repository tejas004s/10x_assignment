from fastapi import FastAPI, HTTPException
from app.planner import generate_trajectory, WallConfig, Waypoint
from app.database import save_trajectory, init_db
from app.logger import logger, log_timing
from typing import List
import time
import hashlib
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

init_db()

@app.post("/api/trajectories", response_model=List[Waypoint])
@log_timing("create_trajectory")
async def create_trajectory(config: WallConfig):
    start = time.time()

    # Hash input for caching or ID generation
    config_str = f"{config.width}-{config.height}-{[(o.x, o.y, o.width, o.height) for o in config.obstacles]}"
    config_hash = hashlib.md5(config_str.encode()).hexdigest()

    # Generate path
    try:
        trajectory = generate_trajectory(config)
    except Exception as e:
        logger.error(f"Trajectory generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error")

    duration = round(time.time() - start, 3)
    logger.info(f"Trajectory {config_hash} generated with {len(config.obstacles)} obstacles in {duration}s")

    save_trajectory(
        trajectory_id=config_hash,
        width=config.width,
        height=config.height,
        coverage_width=config.coverage_width,
        obstacles=len(config.obstacles),
        waypoints=trajectory,
        duration=duration
    )

    return trajectory

@app.get("/api/metrics")
def get_metrics():
    return {"status": "metrics endpoint ready"}