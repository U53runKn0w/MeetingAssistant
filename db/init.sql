-- 开启外键约束 (SQLite 默认可能不开启)
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------
-- 1. 用户表
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS users
(
    user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT UNIQUE NOT NULL,
    password   TEXT        NOT NULL,
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
    duration   INTEGER, -- 分钟数
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
    FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id) ON DELETE CASCADE
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
    user_id    INTEGER NOT NULL,
    todo_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL,
    owner      TEXT    NOT NULL,
    task       TEXT    NOT NULL,
    deadline   TIMESTAMP,
    status     TEXT DEFAULT 'pending', -- pending/in_progress/completed
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
    is_resolved  BOOLEAN DEFAULT 0,
    FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- 7. 对话记录表
-- ---------------------------------------------------------
-- 1. 对话会话表：存储一次完整对话的背景信息
CREATE TABLE IF NOT EXISTS chat_sessions
(
    session_id TEXT PRIMARY KEY, -- 唯一会话ID (建议使用 UUID 或 时间戳)
    user_id    TEXT NOT NULL,    -- 用户标识，如 "zhangsan"
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

-- 为常用查询字段创建索引，提升检索速度
CREATE INDEX IF NOT EXISTS idx_session_order ON dialog_steps (session_id, sequence_order);

-- ---------------------------------------------------------
-- 8. 偏好设置表
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS preference
(
    preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    category      TEXT    NOT NULL,
    preference    TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    UNIQUE (user_id, category)
);

-- DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS meetings;
-- DROP TABLE IF EXISTS attendees;
-- DROP TABLE IF EXISTS agenda_conclusions;
-- DROP TABLE IF EXISTS todos;
-- DROP TABLE IF EXISTS follow_ups;
-- DROP TABLE IF EXISTS chat_sessions;
-- DROP TABLE IF EXISTS dialog_steps;
-- DROP TABLE IF EXISTS preference;