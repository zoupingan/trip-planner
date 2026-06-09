from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator


class TripRequest(BaseModel):
    city: str = Field(..., description="目的地城市")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    travel_days: int = Field(..., ge=1, le=30, description="旅行天数")
    transportation: str = Field(..., description="交通方式")
    accommodation: str = Field(..., description="住宿偏好")
    preferences: list[str] = Field(default_factory=list, description="旅行偏好")
    free_text_input: Optional[str] = Field(default="", description="额外要求")


class Location(BaseModel):
    """地理位置"""

    longitude: float = Field(..., description="经度")
    latitude: float = Field(..., description="纬度")


class Attraction(BaseModel):
    """景点信息"""

    name: str = Field(..., description="景点名称")
    address: str = Field(..., description="景点地址")
    location: Location = Field(..., description="经纬度坐标")
    visit_duration: int = Field(..., description="建议游览时间，单位分钟")
    description: str = Field(..., description="景点描述")
    category: str = Field(default="景点", description="景点类别")
    rating: Optional[float] = Field(default=None, description="评分")
    photos: list[str] = Field(default_factory=list, description="景点图片 URL 列表")
    poi_id: str = Field(default="", description="POI ID")
    image_url: Optional[str] = Field(default=None, description="图片 URL")
    ticket_price: int = Field(default=0, description="门票价格，单位元")  # 景点地址


class Meal(BaseModel):
    """餐饮信息"""

    type: str = Field(..., description="餐饮类型：breakfast/lunch/dinner/snack")
    name: str = Field(..., description="餐饮名称")
    address: Optional[str] = Field(default=None, description="餐饮地址")
    location: Optional[Location] = Field(default=None, description="餐饮位置")
    description: Optional[str] = Field(default=None, description="餐饮描述")
    estimated_cost: int = Field(default=0, description="预估费用，单位元")


class Hotel(BaseModel):
    """酒店信息"""

    name: str = Field(..., description="酒店名称")
    address: str = Field(default="", description="酒店地址")
    location: Optional[Location] = Field(default=None, description="酒店位置")
    price_range: str = Field(default="", description="价格范围")
    rating: str = Field(default="", description="评分")
    distance: str = Field(default="", description="距离说明")
    type: str = Field(default="", description="酒店类型")
    estimated_cost: int = Field(default=0, description="预估费用，单位元/晚")


class DayPlan(BaseModel):
    """单日行程"""

    date: str = Field(..., description="日期 YYYY-MM-DD")
    day_index: int = Field(..., description="第几天，从 0 开始")
    description: str = Field(..., description="当天行程概述")
    transportation: str = Field(..., description="交通方式")
    accommodation: str = Field(..., description="住宿偏好")
    hotel: Optional[Hotel] = Field(default=None, description="推荐酒店")
    attractions: list[Attraction] = Field(default_factory=list, description="景点列表")
    meals: list[Meal] = Field(default_factory=list, description="餐饮列表")


class WeatherInfo(BaseModel):
    """天气信息"""

    date: str = Field(..., description="日期 YYYY-MM-DD")
    day_weather: str = Field(default="", description="白天天气")
    night_weather: str = Field(default="", description="夜间天气")
    day_temp: Union[int, str] = Field(default=0, description="白天温度")
    night_temp: Union[int, str] = Field(default=0, description="夜间温度")
    wind_direction: str = Field(default="", description="风向")
    wind_power: str = Field(default="", description="风力")

    @field_validator("day_temp", "night_temp", mode="before")
    @classmethod
    def parse_temperature(cls, value):
        if isinstance(value, str):
            value = value.replace("°C", "").replace("℃", "").replace("°", "").strip()
            try:
                return int(value)
            except ValueError:
                return 0
        return value


class Budget(BaseModel):
    """预算信息"""

    total_attractions: int = Field(default=0, description="景点门票总费用")
    total_hotels: int = Field(default=0, description="酒店总费用")
    total_meals: int = Field(default=0, description="餐饮总费用")
    total_transportation: int = Field(default=0, description="交通总费用")
    total: int = Field(default=0, description="总费用")


class TripPlan(BaseModel):
    """完整旅行计划"""

    city: str = Field(..., description="目的地城市")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    days: list[DayPlan] = Field(..., description="每日行程")
    weather_info: list[WeatherInfo] = Field(default_factory=list, description="天气信息")
    overall_suggestions: str = Field(..., description="总体建议")
    budget: Optional[Budget] = Field(default=None, description="预算信息")


class TripPlanResponse(BaseModel):
    """旅行计划接口响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="响应消息")
    data: Optional[TripPlan] = Field(default=None, description="旅行计划数据")


class ErrorResponse(BaseModel):
    """错误响应"""

    success: bool = Field(default=False, description="是否成功")
    message: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(default=None, description="错误代码")


# 路线规划pydantic 模型
class RouteRequest(BaseModel):
    origin_address: str
    destination_address: str
    origin_city: Optional[str] = None
    destination_city: Optional[str] = None
    route_type: str = "walking"


class RouteInfo(BaseModel):
    distance: float
    duration: int
    route_type: str
    description: str


class RouteResponse(BaseModel):
    success: bool
    message: str = ""
    data: Optional[RouteInfo] = None
