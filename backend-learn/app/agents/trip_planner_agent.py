from datetime import datetime, timedelta
import json

from hello_agents import SimpleAgent
from hello_agents.tools import MCPTool

from app.config import get_settings
from app.models.schemas import TripRequest, TripPlanResponse, DayPlan, Attraction, TripPlan, Budget, Meal, Hotel, \
    Location, WeatherInfo
from app.services.llm_service import get_llm

PLANNER_AGENT_PROMPT = """
你是行程规划专家。你的任务是根据用户输入和已有信息，生成符合 TripPlan 结构的 JSON。

重要格式要求：
1. 只返回 JSON，不要返回解释文字
2. hotel 必须是对象，不能是字符串
3. weather_info 必须是数组，不能是字符串
4. budget 必须是对象，不能是字符串
5. visit_duration 必须是分钟整数，例如 180，不能写 "3小时"
6. ticket_price 必须是整数，例如 60，不能写 "60元"
7. meals 每一项必须包含 type、name、description、estimated_cost
8. meals 里不要使用 recommendation 字段
9. type 使用 breakfast、lunch、dinner，不要使用 早餐、午餐、晚餐
10. day_index 从 0 开始

请严格返回如下结构：
{
  "city": "北京",
  "start_date": "2026-06-10",
  "end_date": "2026-06-10",
  "days": [
    {
      "date": "2026-06-10",
      "day_index": 0,
      "description": "当天行程概述",
      "transportation": "公共交通",
      "accommodation": "经济型酒店",
      "hotel": {
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {"longitude": 116.397, "latitude": 39.899},
        "price_range": "300-500元",
        "rating": "4.5",
        "distance": "距离主要景点约3公里",
        "type": "经济型酒店",
        "estimated_cost": 400
      },
      "attractions": [
        {
          "name": "景点名称",
          "address": "景点地址",
          "location": {"longitude": 116.4074, "latitude": 39.9163},
          "visit_duration": 180,
          "description": "景点描述",
          "category": "历史文化",
          "ticket_price": 60
        }
      ],
      "meals": [
        {
          "type": "breakfast",
          "name": "早餐推荐",
          "description": "早餐描述",
          "estimated_cost": 30
        }
      ]
    }
  ],
  "weather_info": [
    {
      "date": "2026-06-10",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 31,
      "night_temp": 22,
      "wind_direction": "南风",
      "wind_power": "1-3级"
    }
  ],
  "overall_suggestions": "总体建议",
  "budget": {
    "total_attractions": 60,
    "total_hotels": 400,
    "total_meals": 220,
    "total_transportation": 70,
    "total": 750
  }
}
"""

ATTRACTION_AGENT_PROMPT = """
你是景点搜索专家。你的任务是根据城市和用户偏好，整理适合旅行计划使用的景点候选信息。

要求：
1. 根据用户城市和偏好，给出 4-8 个候选景点
2. 每个景点包含名称、地址、经纬度、类别、建议游览时间、门票价格、简短描述
3. 结果用简洁文本或 JSON 都可以
4. 不要生成完整行程，只负责提供景点候选信息

重点事项：
你必须使用 amap_maps_text_search 工具搜索景点。
工具调用格式：
[TOOL_CALL:amap_maps_text_search:keywords=景点关键词,city=城市名]
"""

WEATHER_AGENT_PROMPT = """
你是天气查询专家。你的任务是根据城市和旅行日期，整理旅行计划需要的天气信息。

要求：
1. 根据用户提供的城市、开始日期、结束日期，给出每天的天气参考
2. 每天天气包含日期、白天天气、夜间天气、白天温度、夜间温度、风向、风力
3. 温度必须使用纯数字，不要带 °C、℃、度 等单位
4. 不要生成完整行程，只负责提供天气信息
5. 输出尽量简洁，方便行程规划 Agent 使用

重点事项：
你必须使用 amap_maps_weather 工具查询天气。
工具调用格式：
[TOOL_CALL:amap_maps_weather:city=城市名]

"""

HOTEL_AGENT_PROMPT = """
你是酒店推荐专家。你的任务是根据城市、住宿偏好和行程安排，整理适合旅行计划使用的酒店候选信息。

要求：
1. 根据用户城市和住宿偏好，推荐 3-5 个酒店候选
2. 每个酒店包含名称、地址、经纬度、价格范围、评分、距离主要景点的距离、酒店类型、预估费用
3. 酒店类型要尽量匹配用户 accommodation
4. 不要生成完整行程，只负责提供酒店候选信息
5. 输出尽量简洁，方便行程规划 Agent 使用

重点事项：
你必须使用 amap_maps_text_search 工具搜索酒店。
工具调用格式：
[TOOL_CALL:amap_maps_text_search:keywords=酒店,city=城市名]

"""

# 示例数据
preference_attractions = {
    "历史文化": [
        ("历史博物馆", "了解城市历史文化的好地方"),
        ("古城街区", "适合散步和感受当地历史氛围"),
    ],
    "美食": [
        ("本地小吃街", "可以品尝当地特色小吃"),
        ("传统餐馆", "适合体验城市代表性美食"),
    ],
    "自然风光": [
        ("城市公园", "适合放松和散步"),
        ("湖边景区", "适合欣赏自然风光"),
    ],
    "购物": [
        ("商业步行街", "适合购物和逛街"),
        ("特色市场", "可以购买当地特色商品"),
    ],
}


class SimpleTripPlanner:

    def __init__(self):
        # 创建 MCPTool 实例
        settings = get_settings()
        self.amap_tool = MCPTool(
            name = "amap",
            description="高德地图服务",
            server_command=["uvx", "amap-mcp-server"],
            env={"AMAP_MAPS_API_KEY": settings.amap_api_key},
            auto_expand=True
        )
        self.amap_tool.expandable = True

        # 创建 LLM 实例以及 Agent实例
        self.llm = get_llm()
        self.planner_agent = SimpleAgent(
            system_prompt=PLANNER_AGENT_PROMPT,
            name="Trip Planner",
            llm=self.llm
        )

        self.attraction_agent = SimpleAgent(
            system_prompt=ATTRACTION_AGENT_PROMPT,
            name="Attraction Searcher",
            llm=self.llm
        )
        self.attraction_agent.add_tool(self.amap_tool)

        self.weather_agent = SimpleAgent(
            system_prompt=WEATHER_AGENT_PROMPT,
            name="Weather Searcher",
            llm=self.llm
        )
        self.weather_agent.add_tool(self.amap_tool)

        self.hotel_agent = SimpleAgent(
            system_prompt=HOTEL_AGENT_PROMPT,
            name="Hotel Searcher",
            llm=self.llm
        )
        self.hotel_agent.add_tool(self.amap_tool)

    def plan_trip(self, request: TripRequest) -> TripPlan:
        try:

            attraction_query = self.build_attraction_query(request)
            attraction_response = self.attraction_agent.run(attraction_query)
            print("景点搜索结果:", attraction_response[:300])

            weather_query = self.build_weather_query(request)
            weather_response = self.weather_agent.run(weather_query)
            print("天气查询结果:", weather_response[:300])

            hotel_query = self.build_hotel_query(request)
            hotel_response = self.hotel_agent.run(hotel_query)
            print("酒店查询结果:", hotel_response[:300])

            planner_query = self.build_planner_query(request, attraction_response, weather_response, hotel_response)
            planner_response = self.planner_agent.run(planner_query)

            print("规划 Agent 返回:", planner_response[:300])

            return self.parse_response(planner_response, request)
        except Exception as e:
            print(f"生成旅行计划失败: {e}")
            return self._create_fallback_plan(request)

    # 构建景点查询query
    def build_attraction_query(self, request: TripRequest) -> str:
        if request.preferences:
            keywords = request.preferences[0]
        else:
            keywords = "景点"
        return  (f"请使用 amap_maps_text_search 工具搜索{request.city}的{keywords}相关景点。\n"
                 f"[TOOL_CALL:amap_maps_text_search:keywords={keywords},city={request.city}]"
        )

    # 构建计划查询query
    def build_planner_query(self, request: TripRequest, attractions: str, weather: str, hotels: str) -> str:
        query = f"""
        请根据以下信息生成{request.city}的{request.travel_days}天旅行计划。

        基本信息：
        - 城市：{request.city}
        - 日期：{request.start_date} 至 {request.end_date}
        - 天数：{request.travel_days}
        - 交通方式：{request.transportation}
        - 住宿偏好：{request.accommodation}
        - 旅行偏好：{", ".join(request.preferences) if request.preferences else "无"}

        景点信息：
        {attractions}

        天气信息：
        {weather}

        酒店信息：
        {hotels}

        请返回符合 TripPlan 结构的 JSON。
        """
        if request.free_text_input:
            query += f"\n{request.free_text_input}"

        return query

    def build_weather_query(self, request: TripRequest) -> str:
        return (
            f"请使用 amap_maps_weather 工具查询{request.city}的天气。\n"
            f"[TOOL_CALL:amap_maps_weather:city={request.city}]"
        )

    def build_hotel_query(self, request):
        return (
            f"请使用 amap_maps_text_search 工具搜索{request.city}的{request.accommodation}酒店。\n"
            f"[TOOL_CALL:amap_maps_text_search:keywords=酒店,city={request.city}]"
        )


    def parse_response(self, response: str, request: TripRequest):
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)  # 从json_start开始，找到下一个```的位置
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("未找到JSON格式的字符串")
            data = json.loads(json_str)
            return TripPlan(**data)
        except Exception as e:
            return self._create_fallback_plan(request)

    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:

        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        days = []

        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)

            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"第{i + 1}天基础行程",
                transportation=request.transportation,
                accommodation=request.accommodation,
                hotel=self.build_hotel(request),
                attractions=self.build_attractions(request),
                meals=self.build_meals(request),
            )

            days.append(day_plan)

        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=[],
            overall_suggestions="这是备用行程。当正常规划失败时，系统会返回这份基础计划。",
            budget=self.build_budget(request),
        )

    def build_attractions(self, request: TripRequest) -> list[Attraction]:

        selected = []
        for preference in request.preferences:
            if preference in preference_attractions:
                selected.extend(preference_attractions.get(preference, []))
        if not selected:
            selected = [
                ("热门景点", "这是城市里的热门游玩地点"),
                ("城市中心", "适合初次到访时了解城市风貌"),
            ]

        attractions = []
        for i, (name, description) in enumerate(selected[:2]):
            attractions.append(
                Attraction(
                    name=name,
                    description=description,
                    address=f"{request.city} {name}",
                    location=Location(longitude=0.0, latitude=0.0),
                    visit_duration=120
                )
            )
        return attractions

    def build_meals(self, request: TripRequest) -> list[Meal]:
        meals = []
        return meals

    def build_hotel(self, request: TripRequest) -> Hotel:
        hotel = Hotel(
            name="Sample Hotel",
            address="Sample Address",
            price_range="Mid-range",
            rating="4.5",
            distance="5 km from city center",
            type="Hotel",
            estimated_cost=500,
        )
        return hotel

    def build_weather_info(self, request) -> list[WeatherInfo]:
        pass

    def build_budget(self, request) -> Budget:
        budget = Budget(
            total_attractions=100,
            total_hotels=200,
            total_meals=300,
            total_transportation=400,
            total=1000
        )
        return budget




trip_planner = SimpleTripPlanner()


def get_planner_agent() -> SimpleTripPlanner:
    return trip_planner


if __name__ == "__main__":
    trip_planner = get_planner_agent()
    fake_response = '{"city": "北京", "days": [{}]}'

    result = trip_planner.plan_trip(
        TripRequest(city="北京", start_date="2023-08-01", end_date="2023-08-05",
                    travel_days=5,
                    transportation="公共交通", accommodation="酒店", ))
    print(result)
    print(type(result))
