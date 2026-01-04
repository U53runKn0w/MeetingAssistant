<template>
  <div class="container mt-5 mb-5 pb-5">
    <header class="text-center mb-5">
      <h1 class="display-5 fw-bold text-primary">分析结果详情</h1>
      <p class="lead text-muted">基于 AI 智能提取的会议核心要素</p>
    </header>

    <div class="row row-cols-1 row-cols-md-2 g-4 mb-5">
      <div v-for="(data, key) in results" :key="key" class="col">
        <div class="card result-card h-100 shadow-sm border-0">
          <div :class="['card-header py-3', toolConfigs[key]?.class]">
            <h5 class="card-title mb-0 text-white">
              <i :class="['bi me-2', toolConfigs[key]?.icon]"></i>
              {{ toolConfigs[key]?.name }}
            </h5>
          </div>
          <div class="card-body bg-white">
            <div v-if="!data" class="text-muted text-center py-4">暂无分析数据</div>

            <div v-else-if="key === 'extract_meeting_basic_info'" class="info-list">
              <div class="mb-2"><strong>主题：</strong> <span class=" bg-light text-dark">{{ data.subject }}</span>
              </div>
              <div class="mb-2"><strong>时间：</strong> {{ formatDateTime(data.time) }} ({{ data.duration }})</div>
              <div>
                <strong>参会人员：</strong>
                <div class="mt-2">
                  <span v-for="person in data.attendees" :key="person"
                        class="badge rounded-pill bg-outline-primary me-2 mb-2">
                    {{ person }}
                  </span>
                </div>
              </div>
            </div>

            <div v-else-if="key === 'parse_meeting_agenda_conclusion'" class="agenda-list">
              <div v-for="(item, index) in data" :key="index" class="agenda-item border-bottom pb-2 mb-2">
                <div class="fw-bold text-primary mb-1 small"><i class="bi bi-dot"></i> {{ item.agenda }}</div>
                <div class="ps-3 text-secondary small">{{ item.conclusion }}</div>
              </div>
            </div>

            <div v-else-if="key === 'generate_meeting_todo'" class="todo-list">
              <div v-for="(todo, index) in data" :key="index" class="d-flex align-items-start mb-3 todo-item">
                <div class="todo-check me-2 mt-1"><i class="bi bi-check2-square text-warning"></i></div>
                <div>
                  <div class="fw-bold small">{{ todo.task }}</div>
                  <div class="text-muted extra-small">
                    责任人：<span class="text-dark">{{ todo.owner }}</span> | 截止：{{ todo.deadline }}
                  </div>
                </div>
              </div>
            </div>

            <div v-else-if="key === 'mark_meeting_follow_up'" class="follow-up-list">
              <div v-for="(follow, index) in data" :key="index" class="mb-3">
                <div class="fw-bold small text-info"><i class="bi bi-question-circle me-1"></i> {{ follow.topic }}</div>
                <div class="ps-3 border-start ms-1 text-muted small mt-1">{{ follow.reason }}</div>
              </div>
            </div>

            <div v-else class="result-content text-secondary">
              {{ data }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="text-center mt-4">
      <button @click="goBack" class="btn btn-outline-primary px-5 py-2 rounded-pill">
        <i class="bi bi-arrow-left me-2"></i>
        返回输入页面
      </button>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue';
import {useRouter} from 'vue-router';
import {useChat} from "@/store/chat.js";

const router = useRouter();
const isLoading = ref(true);

const results = ref({
  extract_meeting_basic_info: null,
  parse_meeting_agenda_conclusion: null,
  generate_meeting_todo: null,
  mark_meeting_follow_up: null
});

const toolConfigs = {
  extract_meeting_basic_info: {name: "会议基本信息", icon: "bi-info-circle-fill", class: "bg-primary"},
  parse_meeting_agenda_conclusion: {name: "议程与结论", icon: "bi-journal-check", class: "bg-success"},
  generate_meeting_todo: {name: "待办事项 (To-do)", icon: "bi-clipboard-data-fill", class: "bg-warning text-dark"},
  mark_meeting_follow_up: {name: "跟进事项", icon: "bi-exclamation-diamond-fill", class: "bg-info text-white"}
};

// 工具函数：格式化时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

onMounted(() => {
  fetchMeetingDetails();
});

const fetchMeetingDetails = async () => {
  isLoading.value = true;
  const conversation = useChat();
  const rawData = conversation.extractObservation();

  const parsedResults = {};
  for (const key in rawData) {
    if (key !== "get_user_info") {
      try {
        let strData = rawData[key];
        // 关键修正：如果内容是单引号的字符串，JSON.parse 会失败，需要转换
        if (typeof strData === 'string') {
          const validJsonStr = strData.replace(/'/g, '"');
          parsedResults[key] = JSON.parse(validJsonStr);
        } else {
          parsedResults[key] = strData;
        }
      } catch (e) {
        console.warn(`解析 ${key} 失败`, e);
        parsedResults[key] = null;
      }
    }
  }

  results.value = parsedResults;
  isLoading.value = false;
};

const goBack = () => router.push('/');
</script>

<style scoped>
/* 容器边距优化 */
.container {
  max-width: 1200px;
}

/* 卡片进入动画 */
.result-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
  border-radius: 12px;
}

.result-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

/* 标题样式 */
.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* 内容区域 */
.result-content {
  line-height: 1.8;
  font-size: 0.95rem;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .display-6 {
    font-size: 1.5rem;
  }
}

/* 继承你原有的样式并增加以下部分 */
.bg-outline-primary {
  border: 1px solid #0d6efd;
  color: #0d6efd;
  background: transparent;
}

.agenda-item:last-child {
  border-bottom: none !important;
}

.extra-small {
  font-size: 0.75rem;
}

.todo-item {
  transition: all 0.2s;
}

.todo-item:hover {
  background: #fff9e6;
  border-radius: 4px;
}

.border-start {
  border-left: 3px solid #0dcaf0 !important;
}

/* 针对不同工具的渐变增强 */
.bg-primary {
  background: linear-gradient(45deg, #4e73df, #224abe) !important;
}

.bg-success {
  background: linear-gradient(45deg, #1cc88a, #13855c) !important;
}

.bg-warning {
  background: linear-gradient(45deg, #f6c23e, #dda20a) !important;
}

.bg-info {
  background: linear-gradient(45deg, #36b9cc, #258391) !important;
}
</style>