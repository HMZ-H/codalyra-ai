import asyncio
import json
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.database.models.review import Review
from app.database.models.run import Run
from app.database.models.trajectory import Trajectory

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


class ReviewConnectionManager:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = {}

    async def connect(self, review_id: str, ws: WebSocket):
        await ws.accept()
        if review_id not in self.connections:
            self.connections[review_id] = []
        self.connections[review_id].append(ws)

    def disconnect(self, review_id: str, ws: WebSocket):
        if review_id in self.connections:
            self.connections[review_id] = [c for c in self.connections[review_id] if c != ws]
            if not self.connections[review_id]:
                del self.connections[review_id]

    async def broadcast(self, review_id: str, data: dict):
        if review_id not in self.connections:
            return
        message = json.dumps(data)
        dead = []
        for ws in self.connections[review_id]:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(review_id, ws)


manager = ReviewConnectionManager()


def _get_review_state(review_id: str) -> dict | None:
    db = SessionLocal()
    try:
        review = db.get(Review, uuid.UUID(review_id))
        if not review:
            return None

        runs = db.query(Run).filter(Run.review_id == review.id).all()
        agent_runs = {}
        for run in runs:
            agent_type = run.agent_name.replace("-agent", "")
            run_data = {
                "status": run.status,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                "duration_seconds": run.duration_seconds,
                "error_message": run.error_message,
            }
            if run.evaluation:
                feedback = {}
                if run.evaluation.feedback:
                    try:
                        feedback = json.loads(run.evaluation.feedback) if isinstance(run.evaluation.feedback, str) else run.evaluation.feedback
                    except (json.JSONDecodeError, TypeError):
                        pass
                run_data["findings_count"] = len(feedback.get("findings", []))
                run_data["score"] = run.evaluation.score
            agent_runs[agent_type] = run_data

        trajectories = db.query(Trajectory).join(Run).filter(
            Run.review_id == review.id,
        ).order_by(Trajectory.timestamp.desc()).limit(10).all()

        recent_logs = [
            {
                "agent": t.run.agent_name.replace("-agent", "") if t.run else "unknown",
                "action": t.action_type,
                "output": t.action_output[:200] if t.action_output else "",
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "duration_ms": t.duration_ms,
            }
            for t in trajectories
        ]

        return {
            "type": "review_update",
            "review_id": review_id,
            "status": review.status,
            "overall_score": review.overall_score,
            "summary": review.summary,
            "findings_count": review.findings_count,
            "agent_runs": agent_runs,
            "recent_logs": recent_logs,
        }
    finally:
        db.close()


@router.websocket("/ws/reviews/{review_id}")
async def review_websocket(websocket: WebSocket, review_id: str):
    await manager.connect(review_id, websocket)
    try:
        state = _get_review_state(review_id)
        if state:
            await websocket.send_text(json.dumps(state))

        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=3.0)
            except asyncio.TimeoutError:
                pass

            state = _get_review_state(review_id)
            if state:
                await websocket.send_text(json.dumps(state))

            if state and state["status"] in ("completed", "failed"):
                await asyncio.sleep(1)
                await websocket.send_text(json.dumps(state))
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.warning(f"WebSocket error for review {review_id}: {e}")
    finally:
        manager.disconnect(review_id, websocket)
