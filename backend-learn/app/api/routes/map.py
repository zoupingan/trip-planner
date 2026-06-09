from fastapi import APIRouter, HTTPException
from fastapi.params import Query

from app.models.schemas import RouteRequest
from app.services.amap_service import get_amap_service

router = APIRouter(prefix="/map", tags=["地图服务"])


@router.get("/poi")
async def search_poi(keywords: str = Query(..., description="搜索关键字"),
                     city: str = Query(..., description="搜索城市"),
                     citylimit: bool = Query(True, description="是否只搜这个城市，默认 True")):
    try:
        amap_service = get_amap_service()
        result = amap_service.search_poi(keywords, city, citylimit)
        return {"success": True, "data": result}
    except Exception as e:
        print(f"POI 搜索失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"天气查询失败: {str(e)}",
        )

@router.get("/weather")
async def get_weather(
    city: str = Query(..., description="城市名称"),
):
    try:
        service = get_amap_service()
        result = service.get_weather(city)

        return {
            "success": True,
            "message": "天气查询成功",
            "data": result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"天气查询失败: {str(e)}",
        )

@router.post("/route")
async def plan_route(request: RouteRequest):
    try:
        service = get_amap_service()

        result = service.plan_route(
            origin_address=request.origin_address,
            destination_address=request.destination_address,
            origin_city=request.origin_city,
            destination_city=request.destination_city,
            route_type=request.route_type,
        )

        return {
            "success": True,
            "message": "路线规划成功",
            "data": result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"路线规划失败: {str(e)}",
        )
