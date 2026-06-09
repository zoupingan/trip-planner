# 智能旅行助手

基于 Vue 3、FastAPI、HelloAgents 和高德 MCP 实现的智能旅行规划项目。

用户填写目的地、出行日期、交通方式、住宿类型和旅行偏好后，后端通过多个 Agent 协作生成旅行计划，并向前端返回景点、酒店、天气、餐饮、预算和地图坐标等信息。

## 项目结构

```text
trip-planner/
├─ frontend/          Vue 3 前端
├─ backend-learn/     FastAPI 后端
└─ deploy/            Docker 部署配置和辅助脚本
```

## 主要技术

### 前端

- Vue 3
- TypeScript
- Vite
- Ant Design Vue
- Axios
- 高德地图 JavaScript API

### 后端

- Python 3.11
- FastAPI
- Pydantic
- HelloAgents
- 高德 MCP
- Unsplash API

## 必要环境变量

真实的 `.env` 文件包含密钥，不应提交到 GitHub。项目提供 `.env.example` 作为配置模板。

### 后端 `backend-learn/.env`

| 变量 | 是否必需 | 用途 |
| --- | --- | --- |
| `LLM_API_KEY` | 是 | 调用大语言模型 |
| `LLM_BASE_URL` | 是 | 大语言模型兼容接口地址 |
| `LLM_MODEL_ID` | 是 | 使用的模型名称 |
| `AMAP_API_KEY` | 是 | 后端通过高德 MCP 查询景点、天气和路线 |
| `UNSPLASH_ACCESS_KEY` | 是 | 查询景点图片 |
| `UNSPLASH_SECRET_KEY` | 否 | 当前代码未直接使用，保留给后续扩展 |
| `CORS_ORIGINS` | 是 | 允许访问后端的前端地址 |
| `HOST`、`PORT` | 是 | FastAPI 监听地址和端口 |

### 前端 `frontend/.env`

| 变量 | 是否必需 | 用途 |
| --- | --- | --- |
| `VITE_API_BASE_URL` | 是 | FastAPI 后端地址 |
| `VITE_AMAP_WEB_JS_KEY` | 是 | 前端加载高德地图 JavaScript API |
| `VITE_AMAP_WEB_KEY` | 否 | 当前前端代码没有使用 |

注意：所有以 `VITE_` 开头的变量都会被打包进前端代码，不能在其中存放服务端密钥。

## 本地启动

### 1. 启动后端

```powershell
cd backend-learn
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

填写 `backend-learn/.env` 中的密钥后运行：

```powershell
python run.py
```

默认地址：

```text
http://127.0.0.1:8001
```

健康检查：

```text
http://127.0.0.1:8001/health
```

### 2. 启动前端

打开另一个终端：

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

默认地址：

```text
http://localhost:5173
```

## 核心接口

```text
POST /api/trip/plan
GET  /api/poi/photo
GET  /api/poi/search
GET  /api/poi/detail/{poi_id}
GET  /health
```

## 安全说明

- 不要提交任何真实 `.env` 文件。
- 不要把 API Key、服务器密码或私钥写进代码。
- GitHub 仓库中只提交 `.env.example`。
- 如果密钥曾经被提交到 GitHub，仅删除文件并不安全，还应立即到对应平台重置密钥。
- 生产环境建议使用服务器环境变量或 Docker `env_file` 管理配置。

