from typing import Any, Optional

from hello_agents.tools import MCPTool

from app.config import get_settings
from app.models.schemas import WeatherInfo

_amap_mcp_tool = None


def get_amap_mcp_tool() -> MCPTool:
    global _amap_mcp_tool
    settings = get_settings()
    if _amap_mcp_tool is None:
        if not settings.amap_api_key:
            raise ValueError("AMAP_API_KEY 未配置，请在 .env 文件中设置 AMAP_API_KEY")
        # 创建高德地图服务
        _amap_mcp_tool = MCPTool(
            name="amap",
            description="高德地图服务，支持 POI 搜索、天气查询、路线规划等能力",
            server_command=["uvx", "amap-mcp-server"],
            env={"AMAP_MAPS_API_KEY": settings.amap_api_key},
            auto_expand=True,
        )
        print("高德 MCP 工具初始化成功")
    return _amap_mcp_tool


class AmapService:
    def __init__(self):
        self.mcp_tool = get_amap_mcp_tool()

    # 搜索POI
    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> list[dict[str, Any]]:
        """
        :param keyword: 搜索的关键词
        :param city: 搜索的城市
        :param citylimit: 要不要只搜这个城市，默认 True
        :return:
        """
        try:
            result = self.mcp_tool.run({"action": "call_tool", "tool_name": "maps_text_search",
                                        "arguments": {"keywords": keywords, "city": city,
                                                      "citylimit": str(citylimit).lower()}})
            print(f"POI 搜索结果: {result[:300]}")
            return [
                {
                    "raw": result
                }
            ]
        except Exception as e:
            print(f"POI 搜索失败: {e}")
            return []

    # 获取天气
    def get_weather(self, city: str) -> list[WeatherInfo]:
        try:
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_weather",
                "arguments": {
                    "city": city
                }
            })
            return []
        except Exception as e:
            print(f"天气查询失败: {e}")
            return []

    # 获取POI详情
    def get_poi_detail(self, poi_id: str) -> dict[str, Any]:
        try:
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_search_detail",
                "arguments": {
                    "id": poi_id
                }
            })
            return {
                "raw": result
            }
        except Exception as e:
            print(f"POI 详情查询失败: {e}")
            return {}


    # 规划路线
    def plan_route(self,
                   origin_address: str,
                   destination_address: str,
                   origin_city: Optional[str] = None,
                   destination_city: Optional[str] = None,
                   route_type: str = "walking"
                   ) -> dict[str, Any]:

        try:
            tool_map = {
                "walking": "maps_direction_walking_by_address",
                "driving": "maps_direction_driving_by_address",
                "transit": "maps_direction_transit_integrated_by_address",
            }

            tool_name = tool_map.get(route_type, "maps_direction_walking_by_address")

            arguments = {
                "origin_address": origin_address,
                "destination_address": destination_address,
            }

            if origin_city:
                arguments["origin_city"] = origin_city
            if destination_city:
                arguments["destination_city"] = destination_city

            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": tool_name,
                "arguments": arguments
            })
            return {
                "raw": result
            }
        except Exception as e:
            print(f"路线规划失败: {e}")
            return {}


_amap_service = None


def get_amap_service() -> AmapService:
    global _amap_service

    if _amap_service is None:
        _amap_service = AmapService()

    return _amap_service
