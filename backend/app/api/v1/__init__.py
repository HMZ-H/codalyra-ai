from fastapi import APIRouter

from app.api.v1 import agent_configs, analytics, auth, custom_rules, evaluations, exports, github, health, projects, repositories, reviews, runs, settings, tasks, teams, trajectories, users

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
api_router.include_router(settings.router)
api_router.include_router(analytics.router)
api_router.include_router(exports.router)
api_router.include_router(agent_configs.router)
api_router.include_router(teams.router)
api_router.include_router(custom_rules.router)
