<template>
  <div class="sidebar-wrapper" :class="{ 'is-collapsed': isCollapsed }">
    <div class="sidebar-header">
      <div class="brand-area" v-show="!isCollapsed">
        <div class="logo-dot"></div>
        <span class="brand-title">历史记录</span>
      </div>

      <button class="menu-toggle" @click="isCollapsed = !isCollapsed" :title="isCollapsed ? '展开' : '收起'">
        <svg v-if="isCollapsed" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor"
             stroke-width="2.5">
          <path d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
    </div>

    <div class="sidebar-content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <span>加载中...</span>
      </div>

      <div class="list-group" v-else>
        <div
            v-for="item in history"
            :key="item.session_id"
            class="nav-item"
            :class="{
              'is-active': sessionId === item.session_id,
              'collapsed-item': isCollapsed
            }"
            @click="selectSession(item)"
        >
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 8v4l3 3m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/>
            </svg>
          </div>

          <div class="nav-text" v-show="!isCollapsed">
            <div class="title">{{ item.title || '新对话' }}</div>
            <div class="date">{{ formatDate(item.created_at) }}</div>
          </div>

          <button class="delete-btn" @click.stop="openDeleteModal(item)">...</button>

          <ConfirmModal
              v-model="isModalVisible"
              title="确认删除"
              :loading="isDeleting"
              confirm-text="确认删除"
              @confirm="handleDelete"
          >
            确定要删除对话 <strong>“{{ itemToDelete?.title }}”</strong> 吗？
          </ConfirmModal>

          <button
              v-if="!isCollapsed"
              class="delete-btn"
              @click.stop="openDeleteModal(item)"
              title="删除记录"
          >
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <path
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>

          <div class="tooltip" v-if="isCollapsed">{{ item.title || '新对话' }}</div>
        </div>
      </div>
    </div>

    <div class="sidebar-footer" v-show="!isCollapsed">
      <div class="stats">
        <span class="dot"></span>
        共 {{ history.length }} 条记录
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, ref} from 'vue';
import service from "@/js/request.js";
import {useChatStore} from "@/store/chat.js";
import {storeToRefs} from "pinia";
import ConfirmModal from "@/components/ConfirmModal.vue";
import {useMessageStore} from "@/store/error.js";

const isCollapsed = ref(false);
const chat = useChatStore()
const history = ref([])
const {sessionId} = storeToRefs(chat);
const loading = ref(false);
const messageStore = useMessageStore();

const fetchHistory = async () => {
  loading.value = true;
  service.get('/history').then((data) => {
    history.value = data;
  }).catch((error) => {
    messageStore.setError("获取历史记录失败")
    console.error("获取历史记录失败：", error.response?.data || error.message);
  }).finally(() => {
    loading.value = false;
  });
};

const selectSession = async (item) => {
  sessionId.value = item.session_id;

  service.get(`/history/${item.session_id}`).then((data) => {
    chat.messages = []
    data.forEach((item) => {
      chat.messages.push({
        "type": item.type,
        "text": item.text,
      });
    })

    chat.question = item.title;
    chat.text = item.meeting;

    if (chat.messages.length > 0 && chat.question.length > 0) {
      chat.buttonsShow = true;
    }

  }).catch((error) => {
    console.error('加载会话详情失败:', error);
  });
};


onMounted(() => {
  fetchHistory();
});

function formatDate(dateString) {
  const date = new Date(dateString);

  if (isNaN(date.getTime())) return "Invalid Date";

  const pad = (num) => String(num).padStart(2, '0');

  const YYYY = date.getFullYear();
  const MM = pad(date.getMonth() + 1);
  const DD = pad(date.getDate());
  const HH = pad(date.getHours());
  const mm = pad(date.getMinutes());
  const ss = pad(date.getSeconds());

  return `${YYYY}-${MM}-${DD} ${HH}:${mm}:${ss}`;
}

const isModalVisible = ref(false);
const itemToDelete = ref(null);
const isDeleting = ref(false);

const openDeleteModal = (item) => {
  itemToDelete.value = item;
  isModalVisible.value = true;
};

const handleDelete = async () => {
  isDeleting.value = true;
  try {
    service.delete(`/history/${itemToDelete.value.session_id}`).then((data) => {
      history.value = history.value.filter(h => h.session_id !== itemToDelete.value.session_id);
      isModalVisible.value = false;
    });
  } finally {
    isDeleting.value = false;
  }
};

// 暴露 fetchHistory 方法供父组件调用
defineExpose({
  fetchHistory
});
</script>

<style scoped>
/* 变量定义 */
.sidebar-wrapper {
  --sb-bg: #ffffff;
  --sb-hover: #f3f4f6;
  --sb-active: #eff6ff;
  --primary: #2563eb;
  --text-main: #1f2937;
  --text-dim: #9ca3af;
  --border-color: #f3f4f6;

  width: 260px;
  height: 100vh;
  background-color: var(--sb-bg);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  box-shadow: 4px 0 12px rgba(0, 0, 0, 0.02);
}

.sidebar-wrapper.is-collapsed {
  width: 72px;
}

/* Header */
.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 18px;
  flex-shrink: 0;
}

.brand-area {
  display: flex;
  align-items: center;
  gap: 10px;
  animation: fadeIn 0.3s;
}

.logo-dot {
  width: 12px;
  height: 12px;
  background: var(--primary);
  border-radius: 4px;
  box-shadow: 0 0 10px rgba(37, 99, 235, 0.3);
}

.brand-title {
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--text-main);
  letter-spacing: 0.5px;
}

.menu-toggle {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 8px;
  color: var(--text-dim);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.menu-toggle:hover {
  background: var(--sb-hover);
  color: var(--primary);
}

/* Content & List */
.sidebar-content {
  flex: 1;
  /*overflow-y: overlay; !* 现代浏览器平滑滚动 *!*/
  padding: 8px 12px;
}

/* 隐藏滚动条但保留功能 */
.sidebar-content::-webkit-scrollbar {
  width: 4px;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: transparent;
  border-radius: 4px;
}

.sidebar-content:hover::-webkit-scrollbar-thumb {
  background: #e5e7eb;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 6px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--text-main);
  border: 1px solid transparent;
}

.nav-item:hover {
  background: var(--sb-hover);
  transform: translateX(2px);
}

.nav-item.is-active {
  background: var(--sb-active);
  color: var(--primary);
  border: 1px solid rgba(37, 99, 235, 0.1);
}

.nav-item.is-active .nav-icon {
  color: var(--primary);
}

.collapsed-item {
  justify-content: center;
  padding: 12px 0;
}

.nav-icon {
  min-width: 24px;
  display: flex;
  justify-content: center;
  color: var(--text-dim);
  transition: color 0.2s;
}

.nav-text {
  margin-left: 12px;
  overflow: hidden;
  flex: 1;
}

.title {
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.date {
  font-size: 0.7rem;
  color: var(--text-dim);
  margin-top: 2px;
}

/* Footer */
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  background: linear-gradient(to top, var(--sb-bg), transparent);
}

.stats {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  color: var(--text-dim);
}

.stats .dot {
  width: 6px;
  height: 6px;
  background: #10b981;
  border-radius: 50%;
}

/* Tooltip */
.nav-item .tooltip {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  left: 80%;
  background: #1f2937;
  color: white;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 100;
  transition: all 0.2s;
  pointer-events: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.nav-item:hover .tooltip {
  visibility: visible;
  opacity: 1;
  left: calc(100% + 12px);
}

/* Loading Animation */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding-top: 40px;
  color: var(--text-dim);
  font-size: 0.8rem;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--sb-hover);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 删除按钮基础样式 */
.delete-btn {
  position: absolute;
  right: 8px;
  opacity: 0; /* 平时隐藏 */
  padding: 6px;
  border: none;
  background: transparent;
  color: var(--text-dim);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Hover item 时显示按钮 */
.nav-item:hover .delete-btn {
  opacity: 1;
}

/* 按钮自身的 Hover 效果 */
.delete-btn:hover {
  background-color: #fee2e2; /* 浅红色背景 */
  color: #ef4444; /* 红色图标 */
}

/* 如果是 Active 状态，调整按钮颜色以适配蓝色背景 */
.nav-item.is-active .delete-btn {
  color: #60a5fa;
}

.nav-item.is-active .delete-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* 确保文字不会被按钮挡住 */
.nav-item:hover .nav-text {
  padding-right: 24px;
}


</style>


