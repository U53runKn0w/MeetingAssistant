# 会议智能助手系统技术文档

## 项目简介

会议智能助手系统是一个基于 LangChain 和 DeepSeek AI 的智能会议管理平台。系统通过 AI 自动分析会议内容，提取关键信息，生成会议纪要、待办事项和思维导图，帮助用户高效管理会议。

## 目录结构

```
Digital/
├── api/                  # API 接口层
│   ├── __init__.py      # Flask 应用初始化
│   ├── auth.py          # 用户认证
│   ├── chat.py          # 聊天交互
│   ├── history.py       # 聊天历史
│   ├── meetings.py      # 会议管理
│   ├── preferences.py   # 用户偏好
│   ├── results.py       # 结果展示
│   ├── todos.py         # 待办事项
│   └── transcript.py    # 会议转录
├── action/              # AI 工具和动作
│   ├── tools.py         # LangChain 工具集
│   └── models.py        # 数据模型定义
├── db/                  # 数据库层
│   ├── manager.py       # 数据库管理器
│   ├── models.py        # 数据库模型
│   ├── init.sql         # 数据库初始化脚本
│   ├── insert.sql       # 测试数据插入脚本
│   ├── migrate.sql      # 数据库迁移脚本
│   └── delete.sql       # 数据清理脚本
├── config/              # 配置文件
│   ├── .env             # 环境变量
│   ├── template.txt     # 通用 Agent 模板
│   ├── meeting.txt      # 会议上下文模板
│   ├── template_preference.txt  # 偏好分析模板
│   └── template_mindmap.txt      # 思维导图模板
├── front/               # 前端应用 (Vue 3)
│   ├── src/
│   │   ├── components/  # Vue 组件
│   │   ├── views/       # 页面视图
│   │   ├── router/      # 路由配置
│   │   ├── store/       # Pinia 状态管理
│   │   └── js/          # 工具函数
│   └── package.json
├── app.py               # 应用入口
├── agent.py             # Agent 创建和执行
├── config.py            # 配置加载
└── requirements.txt     # Python 依赖

```

## 技术栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | ^3.8 | 主要开发语言 |
| Flask | ~3.1.2 | Web 框架 |
| Flask-CORS | ~6.0.2 | 跨域支持 |
| Flask-JWT-Extended | ~4.7.1 | JWT 认证 |
| SQLAlchemy | ~2.0.45 | ORM 框架 |
| LangChain | ^1.1.0 | AI 应用框架 |
| LangChain-Classic | ^1.0.0 | LangChain 经典版 |
| LangChain-DeepSeek | latest | DeepSeek 模型集成 |
| LangChain-Community | ^0.4.0 | 社区扩展 |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | ^3.5.26 | 前端框架 |
| Vue Router | ^4.6.4 | 路由管理 |
| Pinia | ^3.0.4 | 状态管理 |
| Axios | ^1.13.2 | HTTP 客户端 |
| Bootstrap | ^5.3.8 | UI 框架 |
| Bootstrap Icons | ^1.13.1 | 图标库 |
| Mermaid | ^11.12.2 | 思维导图渲染 |
| Vite | ^7.3.0 | 构建工具 |

## 核心功能模块

### 1. 用户认证模块 (`api/auth.py`)

提供用户登录、注册和 JWT 令牌管理功能。

**主要接口:**
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/refresh` - 刷新令牌

### 2. 智能对话模块 (`api/chat.py`)

基于 LangChain Agent 的智能对话系统，支持会议分析、思维导图生成和个性化偏好分析。

**主要接口:**
- `POST /api/chat` - 智能对话 (SSE 流式响应)
- `POST /api/chat/test` - 测试接口
- `POST /api/mindmap` - 生成思维导图
- `POST /api/preference` - 分析用户偏好

**核心 Agent 类型:**

| Agent 类型 | 用途 | 工具集 |
|------------|------|--------|
| `create_agent` | 通用会议分析 | 会议基础信息提取、议程分析、待办生成、跟进标记、用户信息、联网搜索 |
| `create_pref_agent` | 偏好分析 | 用户信息获取、偏好生成 |
| `create_mindmap_chain` | 思维导图生成 | 直接链式调用 (无工具) |

### 3. 会议管理模块 (`api/meetings.py`)

管理用户会议的创建、查询和更新。

**主要接口:**
- `GET /api/meetings` - 获取用户所有会议
- `GET /api/meetings/<id>` - 获取会议详情
- `PUT /api/meetings/<id>/summary` - 更新会议纪要

### 4. 待办事项模块 (`api/todos.py`)

管理会议相关的待办任务。

**主要接口:**
- `GET /api/todos` - 获取待办列表
- `POST /api/todos` - 添加待办事项
- `PUT /api/todos/<id>` - 更新单个待办
- `PUT /api/todos/update` - 批量更新待办

### 5. 用户偏好模块 (`api/preferences.py`)

存储和管理用户的个性化偏好设置。

**主要接口:**
- `GET /api/preferences` - 获取用户偏好
- `POST /api/preferences` - 添加用户偏好
- `DELETE /api/preferences/<id>` - 删除用户偏好

### 6. 聊天历史模块 (`api/history.py`)

管理用户的聊天会话记录。

**主要接口:**
- `GET /api/history` - 获取聊天历史
- `DELETE /api/history/<id>` - 删除聊天会话

### 7. 会议转录模块 (`api/transcript.py`)

处理会议音频转录功能。

**主要接口:**
- `POST /api/transcript` - 上传并转录会议音频

## AI 工具集详解 (`action/tools.py`)

### 1. extract_meeting_basic_info

**功能:** 从会议文本中提取基础元数据

**参数:**
- `text` (str): 会议文本片段

**返回值:**
```python
{
    "attendees": ["张三", "李四"],      # 参会人员列表
    "time": "2026-01-05 10:00",       # 会议时间 (ISO 格式)
    "subject": "产品评审会",          # 会议主题 (15 字以内)
    "duration": "1小时"               # 会议时长
}
```

### 2. parse_meeting_agenda_conclusion

**功能:** 提取会议的议程和结论

**参数:**
- `text` (str): 包含讨论内容的文本段落

**返回值:**
```python
[
    {
        "agenda": "移动端改版时间表",
        "conclusion": "确定于2月中旬开启 Beta 测试"
    },
    {
        "agenda": "预算申请",
        "conclusion": "通过初步审核，需提交详细费用清单"
    }
]
```

### 3. generate_meeting_todo

**功能:** 识别并生成会议待办事项

**参数:**
- `text` (str): 包含任务分配指令的文本

**返回值:**
```python
[
    {
        "owner": "李四",
        "task": "提交移动端 UI 设计初稿",
        "deadline": "2026-01-12 18:00"
    }
]
```

**特性:**
- 自动将"明天"、"下周"等相对时间转换为具体日期
- 默认截止时间为 18:00
- 未提及时间时标记为"待确认"

### 4. mark_meeting_follow_up

**功能:** 识别需要会后跟进的未决事项

**参数:**
- `text` (str): 反映意见分歧或不确定性的上下文

**返回值:**
```python
[
    {
        "topic": "第三方接口限流问题",
        "reason": "当前供应商未给出明确并发限制回复"
    }
]
```

### 5. generate_user_preferences

**功能:** 将用户的非结构化要求转化为标准偏好并持久化

**参数:**
- `param` (str): JSON 字符串，包含 `text` 和 `username`

**返回值:**
```python
[
    {
        "category": "个人身份",
        "preference": "专业商务"
    }
]
```

**支持的类别:**
- `个人身份`: 称呼方式、语气偏好
- `输出格式`: 表格、HTML、排版要求
- `内容权重`: 关注重点、筛选偏好

### 6. get_user_info

**功能:** 加载用户的完整画像信息

**参数:**
- `username` (str): 用户名

**返回值:**
```python
{
    "preferences": {
        "output_language": "zh-CN",
        "analysis_style": "concise"
    },
    "meetings": [
        {
            "meeting_id": 1,
            "subject": "Q1 产品规划周会",
            "start_time": "2026-01-05 10:00:00",
            "status": "completed"
        }
    ],
    "todos": [
        {
            "todo_id": 1,
            "task": "提交移动端 UI 设计初稿",
            "status": "pending"
        }
    ]
}
```

### 7. search_term_explanation

**功能:** 通过 DuckDuckGo 搜索引擎查询专有名词或问题的解释

**参数:**
- `question` (str): 搜索查询内容

**返回值:**
```python
"关于「RAG」的搜索结果：检索增强生成是一种人工智能技术..."
```

**特性:**
- 自动重试机制 (最多 3 次)
- 整合多个搜索结果
- 适用于技术术语、行业专有名词

## 数据库设计

### 核心表结构

#### users (用户表)
```sql
user_id (主键) | username | password | nickname | role
```

#### meetings (会议表)
```sql
meeting_id (主键) | user_id (外键) | subject | start_time | duration | summary | status
```

#### attendees (参会人表)
```sql
id (主键) | meeting_id (外键) | name
```

#### agenda_conclusions (议程结论表)
```sql
id (主键) | meeting_id (外键) | agenda | conclusion
```

#### todos (待办事项表)
```sql
todo_id (主键) | user_id (外键) | meeting_id (外键) | owner | task | deadline | status
```

#### follow_ups (跟进事项表)
```sql
id (主键) | meeting_id (外键) | topic | reason
```

#### chat_sessions (聊天会话表)
```sql
session_id (主键) | user_id (外键) | query | meeting_content | created_at
```

#### dialog_steps (对话步骤表)
```sql
id (主键) | session_id (外键) | step_order | step_type | step_content | created_at
```

#### preferences (用户偏好表)
```sql
id (主键) | user_id (外键) | category | value
```

## 前端核心组件

### 页面视图 (`views/`)

| 组件 | 功能 |
|------|------|
| `HomeView.vue` | 主页，展示聊天界面 |
| `LoginView.vue` | 用户登录/注册页 |
| `ResultView.vue` | 结果展示页 |

### 功能组件 (`components/`)

| 组件 | 功能 |
|------|------|
| `ChatBox.vue` | 聊天对话框主组件 |
| `ChatMessage.vue` | 单条聊天消息渲染 |
| `ChatInput.vue` | 聊天输入框 |
| `ChatTools.vue` | 聊天工具栏 |
| `History.vue` | 聊天历史记录 |
| `MeetingInput.vue` | 会议内容输入 |
| `MindMapModal.vue` | 思维导图弹窗 |
| `TodoSettings.vue` | 待办事项设置 |
| `MyInfo.vue` | 用户信息管理 |
| `PreferenceGenerator.vue` | 偏好生成器 |
| `UrgentTodoReminder.vue` | 紧急待办提醒 |
| `ResultModal.vue` | 结果展示弹窗 |

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 20.19.0+ 或 22.12.0+

### 后端启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
# 编辑 config/.env 文件，设置 DEEPSEEK_API_KEY 等参数

# 3. 初始化数据库
python -c "from db.manager import db; db.init_db()"

# 4. (可选) 插入测试数据
python db/insert.sql

# 5. 启动后端服务
python app.py
```

### 前端启动

```bash
# 1. 进入前端目录
cd front

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

## 配置说明

### 环境变量 (config/.env)

```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=your_api_key_here

# Agent 配置
TEMPERATURE=0.7
MAX_ITERATIONS=10
VERBOSE=false

# 数据库配置
DATABASE_URL=sqlite:///db/db.sqlite

# JWT 密钥
JWT_SECRET_KEY=meeting_assistant
```

### Prompt 模板

系统使用多个 Prompt 模板来引导 AI 行为：

- `template.txt`: 通用会议分析 Agent 模板
- `template_preference.txt`: 用户偏好分析模板
- `template_mindmap.txt`: 思维导图生成模板
- `meeting.txt`: 会议上下文示例

## API 接口文档

### 认证接口

#### 登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "zhangsan",
  "password": "123456"
}

Response:
{
  "code": 200,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": 1,
    "username": "zhangsan",
    "nickname": "张三"
  }
}
```

### 聊天接口

#### 智能对话 (SSE 流式)
```http
POST /api/chat
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "query": "请总结一下今天的会议",
  "meeting": "会议内容文本...",
  "session_id": null,  // 可选，续传时提供
  "step_offset": 0     // 可选，续传偏移量
}

Response (Server-Sent Events):
data: {"type": "meta", "content": "session_123"}

data: {"type": "stream", "content": "根据会议内容"}

data: {"type": "status", "content": "正在调用工具: extract_meeting_basic_info..."}

data: {"type": "observation", "content": "Observation: {...}"}

data: {"type": "done", "content": ""}
```

#### 生成思维导图
```http
POST /api/mindmap
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "conclusion": "会议结论文本..."
}
```

### 会议接口

#### 获取会议列表
```http
GET /api/meetings
Authorization: Bearer {access_token}

Response:
{
  "code": 200,
  "data": [
    {
      "meeting_id": 1,
      "subject": "Q1 产品规划周会",
      "start_time": "2026-01-05 10:00:00",
      "duration": 60,
      "status": "completed"
    }
  ]
}
```

### 待办事项接口

#### 获取待办列表
```http
GET /api/todos
Authorization: Bearer {access_token}

Response:
{
  "code": 200,
  "data": [
    {
      "todo_id": 1,
      "owner": "李四",
      "task": "提交移动端 UI 设计初稿",
      "deadline": "2026-01-12 18:00:00",
      "status": "pending"
    }
  ]
}
```

## 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         前端层 (Vue 3)                        │
├─────────────────────────────────────────────────────────────┤
│  聊天界面  │  会议管理  │  待办列表  │  思维导图  │  用户设置  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS + SSE
┌──────────────────────────▼──────────────────────────────────┐
│                         API 层 (Flask)                        │
├─────────────────────────────────────────────────────────────┤
│  auth  │  chat  │  meetings  │  todos  │  preferences  │  history  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                         业务逻辑层                            │
├─────────────────────────────────────────────────────────────┤
│              LangChain Agent (ReAct 模式)                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  extract_meeting_basic_info  │  search_term          │    │
│  │  parse_meeting_agenda        │  generate_todo        │    │
│  │  mark_meeting_follow_up      │  generate_preference   │    │
│  │  get_user_info               │                       │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                        数据层                                 │
├─────────────────────────────────────────────────────────────┤
│              SQLAlchemy ORM + SQLite                         │
└─────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    外部服务                                   │
├─────────────────────────────────────────────────────────────┤
│              DeepSeek API  │  DuckDuckGo Search               │
└─────────────────────────────────────────────────────────────┘
```

## 数据流图

### 会议分析流程

```
用户输入会议文本
    ↓
create_agent() 创建 Agent 执行器
    ↓
Agent 使用 ReAct 模式思考:
    Thought: 需要提取会议基本信息
    ↓
Action: extract_meeting_basic_info
    ↓
Observation: 返回参会人、时间、主题等
    ↓
Thought: 需要分析议程和结论
    ↓
Action: parse_meeting_agenda_conclusion
    ↓
Observation: 返回议程-结论对
    ↓
Thought: 需要提取待办事项
    ↓
Action: generate_meeting_todo
    ↓
Observation: 返回待办列表
    ↓
Final Answer: 生成完整的会议纪要 (HTML 格式)
```

### 聊天对话流程

```
用户发送问题
    ↓
检查是否有 session_id
    ├─ 无 → 创建新会话，返回 session_id
    └─ 有 → 恢复会话上下文
    ↓
Agent 流式生成响应 (SSE)
    ├─ stream: 文本片段
    ├─ status: 工具调用状态
    ├─ observation: 工具执行结果
    └─ done: 完成信号
    ↓
前端实时解析并渲染
    ↓
每步实时保存到 dialog_steps 表
```

## 关键技术实现

### 1. ReAct Agent 模式

系统使用 LangChain 的 ReAct (Reasoning + Acting) 模式，让 AI 具备推理和行动能力：

```python
# agent.py
react_agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

agent_executor = AgentExecutor(
    agent=react_agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
)
```

### 2. SSE 流式响应

使用 Server-Sent Events 实现实时流式输出：

```python
async def run_agent_async_generator(executor, data, session_id, step_offset):
    async for event in executor.astream_events(data, version="v2"):
        if kind == "on_chat_model_stream":
            yield f"data: {json.dumps({'type': 'stream', 'content': content})}\n\n"
        elif kind == "on_tool_start":
            yield f"data: {json.dumps({'type': 'status', 'content': f'正在调用工具: {tool_name}'})}\n\n"
```

### 3. 结构化输出

使用 Pydantic 模型确保 AI 输出的格式一致性：

```python
class BasicInfo(BaseModel):
    attendees: List[str]
    time: str
    subject: str
    duration: str

structured_llm = llm.with_structured_output(BasicInfo)
```

### 4. 断点续传

通过 `session_id` 和 `step_offset` 实现对话断点续传：

```python
# 恢复已保存的步骤
existing_steps = db.get_chat_detail(session_id)
step_counter = len(existing_steps)
yield f"data: {json.dumps({'type': 'resumed', 'content': step_counter})}\n\n"
```