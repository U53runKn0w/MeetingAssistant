-- =========================================================
-- 测试数据插入 (Mock Data)
-- =========================================================
DELETE FROM users;
DELETE  FROM meetings;
DELETE  FROM attendees;
DELETE  FROM agenda_conclusions;
DELETE  FROM todos;
DELETE  FROM follow_ups;
DELETE  FROM dialog_steps;
DELETE  FROM chat_sessions;
DELETE  FROM preferences;

-- 插入测试用户 (密码均为模拟哈希值)
INSERT INTO users (username, password, nickname, role)
VALUES ('zhangsan', '123456', '张三', '产品经理'),
       ('lisi', '123456', '李四', '开发工程师');

-- 插入用户偏好
INSERT INTO preferences (user_id, category, value)
VALUES (1, 'output_language', 'zh-CN'),
       (1, 'analysis_style', 'concise'),
       (2, 'output_language', 'en-US'),
       (2, 'analysis_style', 'verbose');


-- 插入会议 (假设 2026年1月1日)
-- 会议1: 已完成的会议,包含纪要
INSERT INTO meetings (user_id, subject, start_time, duration, summary, status)
VALUES (1, 'Q1 产品规划周会', '2026-01-05 10:00:00', 60,
        '会议主题：Q1 产品规划周会
        会议时间：2026年1月5日 10:00-11:00
        会议地点：线上会议

        参会人员：张三（产品经理）、李四（开发工程师）、王五（UI设计师）

        会议内容记录：
        张三："今天主要是同步一下Q1的产品规划，确保各部门对目标和里程碑有统一认识。先从技术团队开始，李工有什么需要协调的吗？"

        李四："好的，张三。我们这边主要负责移动端改版和用户权限系统两个模块。移动端改版的基础框架已经搭建完成，预计1月中旬可以进入联调阶段。不过权限系统部分，因为涉及到多个子系统的权限整合，可能需要提前和各产品线确认权限粒度。"

        王五："UI这边已经完成了移动端的视觉稿设计，包括首页改版、个人中心升级等核心页面。接下来会配合开发团队进行UI切图和交互细节调整。关于配色方案，建议统一使用品牌新的蓝色系，保持视觉一致性。"

        张三："很好，各部门的进展都很顺利。那我们定一下时间节点：1月15日移动端开始联调，1月20日完成权限系统整合。大家还有其他问题吗？"

        李四："我这边还有一个点，关于权限系统的测试，建议提前安排测试人员进行冒烟测试，确保基础功能没问题后再联调。"

        张三："同意，这个很重要。那今天的会议就到这里，大家按照既定计划推进，有问题及时在群里沟通。"

        会议结论：
        1. 确认Q1核心目标：移动端改版和用户权限系统优化
        2. 关键时间节点：1月15日移动端联调，1月20日权限系统整合完成
        3. 优先进行权限系统的冒烟测试', 'completed');

-- 会议2: 未开始的会议,无纪要
INSERT INTO meetings (user_id, subject, start_time, duration, status)
VALUES (1, 'AI 助手架构评审', '2026-01-06 14:30:00', 90, 'scheduled');

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