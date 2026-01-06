<template>
  <div v-if="showModal" class="modal-backdrop fade show"></div>
  <div class="modal fade show" v-if="showModal" style="display: block;" tabindex="-1">
    <div class="modal-dialog modal-xl modal-dialog-centered">
      <div class="modal-content shadow-lg" style="max-height: 90vh;">
        <div class="modal-header bg-primary text-white">
          <h5 class="modal-title"><i class="bi bi-clipboard-data-fill me-2"></i>分析结果详情</h5>
          <button type="button" class="btn-close btn-close-white" @click="closeModal"></button>
        </div>
        <div class="modal-body overflow-auto p-4">
          <div class="container-fluid">
            <div class="row row-cols-1 row-cols-md-2 g-4">
              <div v-for="(data, key) in results" :key="key" class="col">
                <div class="card result-card h-100 shadow-sm border-0">
                  <div :class="['card-header py-3', toolConfigs[key]?.class]">
                    <h6 class="card-title mb-0 text-white">
                      <i :class="['bi me-2', toolConfigs[key]?.icon]"></i>
                      {{ toolConfigs[key]?.name }}
                    </h6>
                  </div>
                  <div class="card-body bg-white">
                    <div v-if="!data" class="text-muted text-center py-4">暂无分析数据</div>

                    <div v-else-if="key === 'extract_meeting_basic_info'" class="info-list">
                      <div class="mb-2"><strong>主题：</strong> <span class="bg-light text-dark">{{ data.subject }}</span></div>
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
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline-primary px-5 py-2 rounded-pill" @click="closeModal">
            <i class="bi bi-x-lg me-2"></i>关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, watch} from 'vue';
import {useChatStore} from "@/store/chat.js";

const showModal = ref(false);

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

// 打开模态框并加载数据
const openModal = () => {
  const conversation = useChatStore();
  const rawData = conversation.extractObservation();

  const parsedResults = {};
  for (const key in rawData) {
    if (key !== "get_user_info") {
      try {
        let strData = rawData[key];
        if (typeof strData === 'string') {
          const validJsonStr = strData
            .replace(/'([^']+)':/g, '"$1":')
            .replace(/:\s*'([^']*)'/g, ':"$1"')
            .replace(/\[\s*'([^']*)'/g, '["$1"')
            .replace(/'([^']*)'\s*\]/g, '$1"]')
            .replace(/,\s*'([^']*)'/g, ',"$1"')
            .replace(/\{\s*'([^']+)':/g, '{"$1":')
            .replace(/:\s*'([^']*)'\s*\}/g, ':"$1"}');

          parsedResults[key] = JSON.parse(validJsonStr);
        } else {
          parsedResults[key] = strData;
        }
      } catch (e) {
        console.warn(`解析 ${key} 失败`, e);
        try {
          let strData = rawData[key];
          if (typeof strData === 'string') {
            const escapedStr = strData.replace(/'([^']*?)'/g, (match, content) => {
              return '"' + content.replace(/'/g, "\\'") + '"';
            });
            parsedResults[key] = JSON.parse(escapedStr);
          }
        } catch (e2) {
          console.warn(`第二次解析 ${key} 也失败`, e2);
          parsedResults[key] = rawData[key];
        }
      }
    }
  }

  results.value = parsedResults;
  showModal.value = true;
};

// 关闭模态框
const closeModal = () => {
  showModal.value = false;
};

// 暴露方法供父组件调用
defineExpose({
  openModal,
  closeModal
});
</script>

<style scoped>
/* 卡片进入动画 */
.result-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
  border-radius: 12px;
  height: 320px;
}

.result-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
}

/* 标题样式 */
.card-title {
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* 卡片内容区域 */
.card-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 统一内容字体大小 */
.result-content,
.info-list,
.agenda-list,
.todo-list,
.follow-up-list {
  line-height: 1.8;
  font-size: 0.95rem;
  overflow-y: auto;
  max-height: 100%;
}

/* 统一标题字体 */
.card-body strong,
.card-body .fw-bold {
  font-size: 0.95rem;
}

/* 待办事项和跟进事项的标题 */
.todo-item .fw-bold,
.follow-up-list .fw-bold {
  font-size: 0.95rem;
}

/* 统一辅助文字大小 */
.text-muted {
  font-size: 0.875rem;
}

.small {
  font-size: 0.875rem;
}

.extra-small {
  font-size: 0.8rem;
}

/* 议程和结论样式 */
.agenda-item {
  padding-bottom: 0.75rem;
  margin-bottom: 0.75rem;
}

.agenda-item .fw-bold {
  font-size: 0.95rem;
}

.agenda-item .ps-3 {
  font-size: 0.9rem;
}

/* 待办事项样式 */
.todo-item {
  padding: 0.5rem;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.todo-item .fw-bold {
  font-size: 0.95rem;
}

.todo-check {
  font-size: 1.1rem;
}

/* 跟进事项样式 */
.follow-up-list .mb-3 {
  padding: 0.5rem;
  border-radius: 8px;
  background-color: #f0f8ff;
}

/* 徽章样式统一 */
.badge {
  font-size: 0.8rem;
  padding: 0.35rem 0.75rem;
}

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
