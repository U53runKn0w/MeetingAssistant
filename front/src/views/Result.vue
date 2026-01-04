<template>
  <div class="container mt-5 mb-5 pb-5">
    <header class="text-center mb-5">
      <h1 class="display-6 fw-bold text-dark">分析结果详情</h1>
      <p class="text-muted">基于 AI 智能提取的会议核心要素</p>
    </header>

    <div class="row row-cols-1 row-cols-md-2 g-4 mb-5">
      <div v-for="(result, key) in results" :key="key" class="col">
        <div class="card result-card h-100 shadow-sm border-0">
          <div :class="['card-header py-3', toolConfigs[key]?.class]">
            <h5 class="card-title mb-0 text-white">
              <i :class="['bi me-2', toolConfigs[key]?.icon]"></i>
              {{ toolConfigs[key]?.name }}
            </h5>
          </div>
          <div class="card-body bg-white">
            <div class="result-content text-secondary" style="white-space: pre-line;">
              {{ result || '暂无分析数据' }}
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
import {useConversation} from "@/js/store.js";

const router = useRouter();

const isLoading = ref(true);


const results = ref({
  extract_meeting_basic_info: "",
  parse_meeting_agenda_conclusion: "",
  generate_meeting_todo: "",
  mark_meeting_follow_up: ""
});

const toolConfigs = {
  extract_meeting_basic_info: {
    name: "会议基本信息",
    icon: "bi-info-circle-fill",
    class: "bg-primary" // 使用 Bootstrap 内置类或自定义 CSS
  },
  parse_meeting_agenda_conclusion: {
    name: "议程与结论",
    icon: "bi-journal-check",
    class: "bg-success"
  },
  generate_meeting_todo: {
    name: "待办事项 (To-do)",
    icon: "bi-clipboard-data-fill",
    class: "bg-warning text-dark"
  },
  mark_meeting_follow_up: {
    name: "跟进事项",
    icon: "bi-exclamation-diamond-fill",
    class: "bg-info text-white"
  }
};

onMounted(() => {
  fetchMeetingDetails();
});

const fetchMeetingDetails = async () => {
  isLoading.value = true;
  const conversation = useConversation();
  const rawData = conversation.extractObservation();

  // 移除不需要展示的项
  delete rawData["get_user_info"];

  // 对每一项进行解析
  const parsedResults = {};
  for (const key in rawData) {
    try {
      let strData = rawData[key];
      // 清洗数据：1. 处理 Python datetime 对象； 2. 将单引号替换为双引号
      const sanitized = strData
          .replace(/datetime\.datetime\((.*?)\)/g, '"$1"')
          .replace(/'/g, '"');

      parsedResults[key] = JSON.parse(sanitized);
    } catch (e) {
      console.warn(`解析 ${key} 失败，将使用原始字符串`, e);
      parsedResults[key] = rawData[key];
    }
  }

  results.value = parsedResults;
  isLoading.value = false;
};

const goBack = () => router.push('/');
</script>


<style scoped src="@/assets/results.css"></style>
<style scoped>
/* 容器边距优化 */
.container {
  max-width: 1000px;
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

/* 针对不同工具的微调 */
.bg-primary {
  background: linear-gradient(45deg, #0d6efd, #0a58ca) !important;
}

.bg-success {
  background: linear-gradient(45deg, #198754, #146c43) !important;
}

.bg-warning {
  background: linear-gradient(45deg, #ffc107, #ffca2c) !important;
}

.bg-info {
  background: linear-gradient(45deg, #0dcaf0, #0bacbe) !important;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .display-6 {
    font-size: 1.5rem;
  }
}
</style>