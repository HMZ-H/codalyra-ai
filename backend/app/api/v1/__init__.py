from fastapi import APIRouter

from app.api.v1 import auth, evaluations, github, health, projects, repositories, reviews, runs, tasks, trajectories, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(projects.router)
api_router.include_router(repositories.router)
api_router.include_router(tasks.router)
api_router.include_router(runs.router)
api_router.include_router(evaluations.router)
api_router.include_router(trajectories.router)
api_router.include_router(reviews.router)
api_router.include_router(github.router)
