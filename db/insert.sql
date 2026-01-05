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