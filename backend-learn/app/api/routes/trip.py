from fastapi import APIRouter, HTTPException

from app.agents.trip_planner_agent import get_planner_agent
from app.agents.trip_planner_graph import run_trip_graph
from app.models.schemas import TripRequest, TripPlanResponse

router = APIRouter(prefix="/trip", tags=["旅行规划"])


@router.post("/plan", response_model=TripPlanResponse)
def get_plan_trip(request: TripRequest):
    try:
        trip_plan = run_trip_graph(request)

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"旅行计划生成失败: {error}",
        ) from error