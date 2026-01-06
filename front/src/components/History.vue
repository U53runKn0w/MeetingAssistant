<template>
  <div class="sidebar-wrapper" :class="{ 'is-collapsed': isCollapsed }">
    <div class="sidebar-header">
      <div class="brand-area" v-show="!isCollapsed">
        <div class="logo-dot"></div>
        <span class="brand-title">历史记录</span>
      </div>

      <div class="header-actions" v-show="!isCollapsed">
        <button
            class="btn-new-session"
            @click="newSession"
            title="新建会话"
        >
          <i class="bi bi-plus-lg"></i> 新会话
        </button>
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

      <button class="menu-toggle" v-show="isCollapsed" @click="isCollapsed = !isCollapsed"
              :title="isCollapsed ? '展开' : '收起'">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M4 6h16M4 12h16M4 18h16"/>
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
      <div class="user-info">
        <div class="user-avatar">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <div class="user-details">
          <div class="user-name">{{ userInfo.nickname || userInfo.username }}</div>
          <div class="user-role" v-if="userInfo.role">{{ userInfo.role }}</div>
        </div>
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

// 用户信息
const userInfo = ref({
  user_id: null,
  username: '',
  nickname: '',
  role: ''
});

const emit = defineEmits(['new-session', 'select-session']);
loading.value = true;
service.get('/history').then((data) => {
  history.value = data;
}).catch((error) => {
  messageStore.setNetworkError('failed');
  console.error("获取历史记录失败：", error.response?.data || error.message);
}).finally(() => {
  loading.value = false;
});

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const data = await service.get('/user/info');
    if (data) {
      userInfo.value = data;
    }
  } catch (error) {
    console.error("获取用户信息失败：", error.response?.data || error.message);
  }
};

onMounted(() => {
  fetchHistory();
  fetchUserInfo();
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
      messageStore.setSuccess('删除成功');
      isModalVisible.value = false;
    }).catch((error) => {
      messageStore.setClientError('badRequest');
      console.error('删除失败:', error);
    });
  } finally {
    isDeleting.value = false;
  }
};
const fetchHistory = async () => {
  loading.value = true;
  service.get('/history').then((data) => {
    history.value = data;
  }).catch((error) => {
    messageStore.setNetworkError('failed');
    console.error("获取历史记录失败：", error.response?.data || error.message);
  }).finally(() => {
    loading.value = false;
  });
};


const newSession = () => {
  // 通知父组件新建会话
  emit('new-session');
};

const selectSession = async (item) => {
  sessionId.value = item.session_id;

  // 通知父组件停止正在进行的生成
  emit('select-session');

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
    messageStore.setNetworkError('failed');
    console.error('加载会话详情失败:', error);
  });
};


onMounted(() => {
  fetchHistory();
});

// 暴露 fetchHistory 方法供父组件调用
defineExpose({
  fetchHistory
});
</script>

<style scoped>
/* 变量定义 */
.sidebar-wrapper {
  --sb-bg: #fafbfc;
  --sb-hover: #f3f4f6;
  --sb-active: #eff6ff;
  --primary: #3b82f6;
  --text-main: #1f2937;
  --text-dim: #9ca3af;
  --border-color: #e5e7eb;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 2px 4px -1px rgba(0, 0, 0, 0.1);

  width: 300px;
  height: 100vh;
  background: var(--sb-bg);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.sidebar-wrapper.is-collapsed {
  width: 70px;
}

/* Header */
.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex-shrink: 0;
  border-bottom: 1px solid var(--border-color);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 在折叠时强制隐藏 */
.sidebar-wrapper.is-collapsed .header-actions {
  display: none !important;
}

.btn-new-session {
  padding: 7px 14px;
  border: 1px solid var(--primary);
  background: transparent;
  color: var(--primary);
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.btn-new-session:hover {
  background: var(--primary);
  color: white;
}

.brand-area {
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}

/* 在折叠时强制隐藏 */
.sidebar-wrapper.is-collapsed .brand-area {
  display: none !important;
}

.logo-dot {
  width: 12px;
  height: 12px;
  background: var(--primary);
  border-radius: 4px;
}

.brand-title {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-main);
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.menu-toggle {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
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
  overflow-y: auto;
  padding: 12px 14px;
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
  background: #d1d5db;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  padding: 14px;
  margin-bottom: 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.15s;
  color: var(--text-main);
}

.nav-item:hover {
  background: var(--sb-hover);
}

.nav-item.is-active {
  background: var(--sb-active);
  color: var(--primary);
}

.nav-item.is-active .nav-icon {
  color: var(--primary);
}

.collapsed-item {
  justify-content: center;
  padding: 12px 0;
}

.nav-icon {
  min-width: 28px;
  display: flex;
  justify-content: center;
  color: var(--text-dim);
  transition: color 0.15s;
}

.nav-text {
  margin-left: 10px;
  overflow: hidden;
  flex: 1;
  white-space: nowrap;
  transition: opacity 0.2s;
}

/* 确保在折叠状态下文字完全隐藏 */
.sidebar-wrapper.is-collapsed .nav-text {
  display: none;
}

.title {
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-main);
}

.date {
  font-size: 0.7rem;
  color: var(--text-dim);
  margin-top: 2px;
}

/* Footer */
.sidebar-footer {
  padding: 14px 16px;
  border-top: 1px solid var(--border-color);
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
  transition: all 0.15s;
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
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
  opacity: 0;
  padding: 6px;
  border: none;
  background: transparent;
  color: var(--text-dim);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 确保在折叠状态下删除按钮完全隐藏 */
.sidebar-wrapper.is-collapsed .delete-btn {
  display: none;
}

/* Hover item 时显示按钮 */
.nav-item:hover .delete-btn {
  opacity: 1;
}

/* 按钮自身的 Hover 效果 */
.delete-btn:hover {
  background: #fee2e2;
  color: #ef4444;
}

/* 如果是 Active 状态，调整按钮颜色以适配蓝色背景 */
.nav-item.is-active .delete-btn {
  color: #60a5fa;
}

.nav-item.is-active .delete-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* 确保文字不会被按钮挡住 */
.nav-item:hover .nav-text {
  padding-right: 24px;
}

/* User Info Styles */
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  overflow: hidden;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.user-details {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-main);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role {
  font-size: 0.75rem;
  color: var(--text-dim);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.settings-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
  color: var(--text-dim);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.settings-btn:hover {
  background: var(--sb-hover);
  color: var(--primary);
}

/* Settings Form */
.settings-form {
  text-align: left;
  margin-top: 8px;
  max-height: 60vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-main);
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.2s;
  outline: none;
}

.form-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-hint {
  display: block;
  font-size: 0.75rem;
  color: var(--text-dim);
  margin-top: 6px;
}

/* Toggle Group */
.toggle-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--text-main);
  cursor: pointer;
  user-select: none;
  padding: 6px 0;
}

.toggle-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--primary);
}

</style>


