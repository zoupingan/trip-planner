from fastapi import APIRouter, HTTPException

from app.services.amap_service import get_amap_service
from app.services.unsplash_service import get_unsplash

router = APIRouter(prefix="/poi", tags=["POI"])

@router.get("/photo")
async def get_attraction_photo(name: str):
    try:
        unsplash_service = get_unsplash()
        photo_url = unsplash_service.get_photo_url(f"{name} China landmark")
        if not photo_url:
            photo_url = unsplash_service.get_photo_url(name)

        return {
            "success": True,
            "message": "获取图片成功",
            "data": {
                "name": name,
                "photo_url": photo_url,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取景点图片失败: {str(e)}",
        )

@router.get("/search")
async def search_poi(keywords: str, city: str = "北京"):
    try:
        amap_service = get_amap_service()
        result = amap_service.search_poi(keywords, city)

        return {
            "success": True,
            "message": "搜索成功",
            "data": result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"搜索 POI 失败: {str(e)}",
        )

@router.get("/detail/{poi_id}")
async def get_poi_detail(poi_id: str):
    try:
        amap_service = get_amap_service()
        result = amap_service.get_poi_detail(poi_id)

        return {
            "success": True,
            "message": "获取 POI 详情成功",
            "data": result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取 POI 详情失败: {str(e)}",
        )