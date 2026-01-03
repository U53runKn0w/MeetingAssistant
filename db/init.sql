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
CREATE TABLE IF NOT EXISTS conversations
(
    conv_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    role       TEXT NOT NULL,
    content    TEXT NOT NULL,
    meeting_id INTEGER,
    tool_used  TEXT,
    timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id) ON DELETE CASCADE
);

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

-- =========================================================
-- 测试数据插入 (Mock Data)
-- =========================================================

-- 插入测试用户 (密码均为模拟哈希值)
INSERT INTO users (username, password)
VALUES ('zhangsan', '123456'),
       ('lisi', '123456');

-- 插入用户偏好
INSERT INTO preference (user_id, category, preference)
VALUES (1, 'output_language', 'zh-CN'),
       (1, 'analysis_style', 'concise'),
       (2, 'output_language', 'en-US');

-- 插入会议 (假设 2026年1月1日)
INSERT INTO meetings (user_id, subject, start_time, duration)
VALUES (1, 'Q1 产品规划周会', '2026-01-05 10:00:00', 60),
       (1, 'AI 助手架构评审', '2026-01-06 14:30:00', 90);

-- 插入参会人
INSERT INTO attendees (name, meeting_id)
VALUES ('张三', 1),
       ('李四', 1),
       ('王五', 1),
       ('张三', 2),
       ('技术专家A', 2);

-- 插入议题结论
INSERT INTO agenda_conclusions (meeting_id, agenda, conclusion)
VALUES (1, '移动端改版时间表', '确定于2月中旬开启 Beta 测试'),
       (1, '预算申请', '通过初步审核，需提交详细费用清单');

-- 插入待办事项
INSERT INTO todos (user_id, meeting_id, owner, task, deadline, status)
VALUES (1, 1, '李四', '提交移动端 UI 设计初稿', '2026-01-12 18:00:00', 'pending'),
       (1, 1, '王五', '整理 Q1 预算明细表', '2026-01-08 12:00:00', 'in_progress');

-- 插入待跟进事项
INSERT INTO follow_ups (meeting_id, topic, reason)
VALUES (2, '第三方接口限流问题', '当前供应商未给出明确并发限制回复');

-- 插入对话记录
INSERT INTO conversations (role, content, meeting_id, tool_used)
VALUES ('user', '帮我总结一下今天的会议结论', 1, NULL),
       ('assistant', '今天的会议主要达成了两项共识：1.移动端2月Beta测试；2.预算初审通过。', 1, 'summarizer_tool');