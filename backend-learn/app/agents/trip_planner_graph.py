from functools import lru_cache
from time import perf_counter
from typing import TypedDict, Literal, Any

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from app.agents.trip_planner_agent import get_planner_agent
from app.models.schemas import TripRequest, TripPlan


class TripGraphState(TypedDict):
    # FastAPI传入的请求参数
    request: TripRequest

    # 三个agent的返回结果
    attraction_response: str
    weather_response: str
    hotel_response: str

    # 规划 Agent 返回的原始文本
    planner_response: str

    # 解析后的最终结果
    trip_plan: TripPlan | None

    # 各阶段的错误信息
    attraction_error: str
    weather_error: str
    hotel_error: str
    planner_error: str

    # 输入校验结果
    input_ok: bool
    input_error: str


def create_initial_state(request: TripRequest) -> TripGraphState:
    return {
        "request": request,
        "attraction_response": "",
        "weather_response": "",
        "hotel_response": "",
        "planner_response": "",
        "trip_plan": None,
        "attraction_error": "",
        "weather_error": "",
        "hotel_error": "",
        "planner_error": "",
        "input_ok": False,
        "input_error": "",
    }


def validate_input(state: TripGraphState) -> dict:
    request = state["request"]
    if not request.city.strip():
        return {
            "input_ok": False,
            "input_error": "缺少目的地城市",
        }

    if request.start_date > request.end_date:
        return {
            "input_ok": False,
            "input_error": "开始日期不能晚于结束日期",
        }

    return {
        "input_ok": True,
        "input_error": "",
    }


def route_after_validation(state: TripGraphState) -> Literal["dispatch_queries", "invalid_input_fallback"]:
    if state["input_ok"]:
        return "dispatch_queries"
    return "invalid_input_fallback"


def invalid_input_fallback(state: TripGraphState) -> dict:
    return {
        "trip_plan": None,
        "planner_error": state["input_error"],
    }


def dispatch_queries(state: TripGraphState) -> dict:
    return {}


def create_collect_attractions_node(planner: Any):
    def collect_attractions(state: TripGraphState) -> dict[str, Any]:
        request = state["request"]
        try:
            query = planner.build_attraction_query(request)

            start_time = perf_counter()

            response = planner.attraction_agent.run(query)
            print("正在执行景点搜索agent...")

            finish_time = perf_counter() - start_time
            print("景点搜索耗时:",finish_time)
            return {
                "attraction_response": response,
                "attraction_error": "",
            }
        except Exception as e:
            return {
                "attraction_response": "",
                "attraction_error": str(e),
            }

    return collect_attractions


def create_collect_weather_node(planner: Any):
    def collect_weather(state: TripGraphState, ) -> dict[str, Any]:
        request = state["request"]

        try:
            print("[天气 MCP 节点] 开始")
            start_time = perf_counter()

            response = planner.amap_tool.run({
                "action": "call_tool",
                "tool_name": "maps_weather",
                "arguments": {
                    "city": request.city,
                },
            })

            elapsed = perf_counter() - start_time
            print(f"[天气 MCP 节点] 完成，耗时：{elapsed:.2f} 秒")
            return {
                "weather_response": response,
                "weather_error": "",
            }
        except Exception as error:
            return {
                "weather_response": (
                    "实时天气暂不可用，"
                    "请提醒用户出行前再次确认天气。"
                ),
                "weather_error": str(error),
            }

    return collect_weather


def create_collect_hotel_node(planner: Any):
    def collect_hotel(
            state: TripGraphState,
    ) -> dict[str, Any]:
        request = state["request"]

        try:
            print("[酒店 MCP 节点] 开始")

            keywords = request.accommodation.strip()

            if "酒店" not in keywords:
                keywords += " 酒店"

            start_time = perf_counter()
            response = planner.amap_tool.run({
                "action": "call_tool",
                "tool_name": "maps_text_search",
                "arguments": {
                    "keywords": keywords,
                    "city": request.city,
                    "citylimit": "true",
                },
            })

            elapsed = perf_counter() - start_time
            print(
                f"[酒店 MCP 节点] 完成，耗时：{elapsed:.2f} 秒"
            )
            return {
                "hotel_response": response,
                "hotel_error": "",
            }
        except Exception as error:
            return {
                "hotel_response": (
                    "酒店实时推荐暂不可用，"
                    "请根据行程区域自行选择住宿。"
                ),
                "hotel_error": str(error),
            }

    return collect_hotel


def create_build_plan_node(planner: Any):
    def build_plan(
            state: TripGraphState,
    ) -> dict[str, Any]:
        request = state["request"]
        response = ""
        try:
            query = planner.build_planner_query(
                request,
                state["attraction_response"],
                state["weather_response"],
                state["hotel_response"],
            )

            start_time = perf_counter()

            response = planner.planner_agent.run(query)
            trip_plan = planner.parse_response(response, request)
            print("正在执行规划搜索agent...")

            finish_time = perf_counter() - start_time
            print("行程规划耗时:", finish_time)
            return {
                "planner_response": response,
                "trip_plan": trip_plan,
                "planner_error": "",
            }
        except Exception as error:
            fallback_plan = planner.create_fallback_plan(request)

            return {
                "planner_response": response,
                "trip_plan": fallback_plan,
                "planner_error": str(error),
            }

    return build_plan


def build_trip_graph(planner: Any):
    builder = StateGraph(TripGraphState)

    collect_attractions = create_collect_attractions_node(planner)
    collect_weather = create_collect_weather_node(planner)
    collect_hotel = create_collect_hotel_node(planner)
    build_plan = create_build_plan_node(planner)

    builder.add_node("validate_input", validate_input)
    builder.add_node("dispatch_queries", dispatch_queries)
    builder.add_node("collect_attractions", collect_attractions)
    builder.add_node("collect_weather", collect_weather)
    builder.add_node("collect_hotel", collect_hotel)
    builder.add_node("build_plan", build_plan)
    builder.add_node("invalid_input_fallback", invalid_input_fallback)

    builder.add_edge(START, "validate_input")
    builder.add_conditional_edges(
        "validate_input",
        route_after_validation,
        {
            "dispatch_queries": "dispatch_queries",
            "invalid_input_fallback": "invalid_input_fallback",
        }
    )
    builder.add_edge("dispatch_queries", "collect_attractions")
    builder.add_edge("dispatch_queries", "collect_weather")
    builder.add_edge("dispatch_queries", "collect_hotel")
    builder.add_edge("collect_attractions", "build_plan")
    builder.add_edge("collect_weather", "build_plan")
    builder.add_edge("collect_hotel", "build_plan")
    builder.add_edge("build_plan", END)
    builder.add_edge("invalid_input_fallback", END)

    return builder.compile()


def run_trip_graph(request: TripRequest) -> TripPlan:
    graph = get_trip_graph()
    initial_state = create_initial_state(request)
    final_state = graph.invoke(initial_state)
    trip_plan = final_state["trip_plan"]

    if trip_plan is None:
        error_message = (
                final_state["planner_error"]
                or "旅行计划生成失败"
        )
        raise ValueError(error_message)

    return trip_plan

@lru_cache(maxsize=1)
def get_trip_graph():
    planner = get_planner_agent()
    return build_trip_graph(planner)
