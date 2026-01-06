-- 开启外键约束 (SQLite 默认可能不开启)
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------
-- 1. 用户表
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS users
(
    user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT    UNIQUE NOT NULL,
    password   TEXT    NOT NULL,
    nickname   TEXT,     -- 用户昵称
    role       TEXT,     -- 职位 (如：经理、工程师、设计师等)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------
-- 2. 会议表
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS meetings
(
    meeting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER   NOT NULL,
    subject    TEXT      NOT NULL,
    start_time TIMESTAMP NOT NULL,
    duration   INTEGER CHECK(duration >= 0), -- 分钟数，非负数
    summary    TEXT,                         -- 会议纪要文本
    status     TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'completed')), -- 会议状态：scheduled-已计划, completed-已完成
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- 3. 参会人表
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS attendees
(
    attendee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    meeting_id  INTEGER NOT NULL,
    FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id) ON DELETE CASCADE,
    UNIQUE (meeting_id, name) -- 同一会议中不能有重复参会人
);

-- ---------------------------------------------------------
-- 4. 议题结论表
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS agenda_conclusions
(
    agenda_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL,
    agenda     TEXT    NOT NULL,
    conclusion TEXT,
    FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- 5. 待办事项表
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS todos
(
    todo_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    meeting_id INTEGER NOT NULL,
    owner      TEXT    NOT NULL,
    task       TEXT    NOT NULL,
    deadline   TIMESTAMP,
    status     TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- 6. 待跟进事项表
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS follow_ups
(
    follow_up_id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id   INTEGER NOT NULL,
    topic        TEXT    NOT NULL,
    reason       TEXT,
    is_resolved  BOOLEAN DEFAULT 0 CHECK(is_resolved IN (0, 1)),
    FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- 7. 对话记录表
-- ---------------------------------------------------------
-- 1. 对话会话表：存储一次完整对话的背景信息
CREATE TABLE IF NOT EXISTS chat_sessions
(
    session_id TEXT PRIMARY KEY, -- 唯一会话ID (建议使用 UUID 或 时间戳)
    user_id    INTEGER NOT NULL,
    query      TEXT,             -- 对话标题，可由模型自动生成或记录第一句话
    meeting    TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 对话步骤明细表：存储 ReAct 的每一个环节
CREATE TABLE IF NOT EXISTS dialog_steps
(
    step_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id     TEXT    NOT NULL, -- 关联 sessions 表
    sequence_order INTEGER NOT NULL, -- 步骤顺序 (0, 1, 2...)
    type           TEXT    NOT NULL, -- 类型：Thought, Action, Action Input, Observation, Final Answer
    content        TEXT,             -- 具体文本内容
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
);

-- ---------------------------------------------------------
-- 8. 偏好设置表
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS preferences
(
    preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    category      TEXT    NOT NULL,
    value         TEXT    NOT NULL, -- 偏好值
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    UNIQUE (user_id, category)
);

-- ---------------------------------------------------------
-- 索引优化：为常用查询字段创建索引，提升检索速度
-- ---------------------------------------------------------

-- 对话相关索引
CREATE INDEX IF NOT EXISTS idx_session_order ON dialog_steps (session_id, sequence_order);
CREATE INDEX IF NOT EXISTS idx_chat_session_user ON chat_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_chat_session_created ON chat_sessions (created_at DESC);

-- 用户会议查询索引
CREATE INDEX IF NOT EXISTS idx_meeting_user ON meetings (user_id);
CREATE INDEX IF NOT EXISTS idx_meeting_time ON meetings (start_time DESC);

-- 待办事项查询索引
CREATE INDEX IF NOT EXISTS idx_todo_user ON todos (user_id, status);
CREATE INDEX IF NOT EXISTS idx_todo_deadline ON todos (deadline DESC);

-- 会议关联数据索引
CREATE INDEX IF NOT EXISTS idx_attendee_meeting ON attendees (meeting_id);
CREATE INDEX IF NOT EXISTS idx_agenda_meeting ON agenda_conclusions (meeting_id);
CREATE INDEX IF NOT EXISTS idx_followup_meeting ON follow_ups (meeting_id);
