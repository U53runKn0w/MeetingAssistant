<template>
  <aside class="sidebar-wrapper" :class="{ 'is-collapsed': isCollapsed }">
    <div class="sidebar-header">
      <div class="brand-area" v-show="!isCollapsed">
        <div class="brand-icon">
          <i class="bi bi-robot"></i>
        </div>
        <span class="brand-title">历史记录</span>
      </div>

      <button
        class="toggle-btn"
        @click="isCollapsed = !isCollapsed"
        :title="isCollapsed ? '展开侧边栏' : '收起侧边栏'"
      >
        <i class="bi" :class="isCollapsed ? 'bi-layout-sidebar-inset' : 'bi-layout-sidebar'"></i>
      </button>
    </div>

    <div class="sidebar-content custom-scrollbar">
      <div v-if="loading" class="text-center py-4" v-show="!isCollapsed">
        <div class="spinner-border spinner-border-sm text-secondary" role="status"></div>
      </div>

      <div v-else-if="history.length === 0" class="empty-state" v-show="!isCollapsed">
        <i class="bi bi-inbox text-muted"></i>
        <span class="small text-muted mt-2">暂无会议记录</span>
      </div>

      <div v-else class="nav-list">
        <div
            v-for="item in history"
            :key="item.id"
            class="nav-item"
            :class="{ 'active': activeId === item.id }"
            @click="handleSelectMeeting(item.id)"
        >
          <div class="nav-icon" :title="isCollapsed ? item.title : ''">
            <i class="bi bi-chat-left-text"></i>
          </div>

          <div class="nav-text" v-show="!isCollapsed">
            <div class="item-title" :title="item.title">{{ item.title }}</div>
            <div class="item-meta">
              <span class="date">{{ item.date }}</span>
              <i class="bi bi-chevron-right arrow"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="sidebar-footer">
      <div class="nav-item" :class="{ 'justify-content-center': isCollapsed }">
        <div class="nav-icon">
          <i class="bi bi-gear"></i>
        </div>
        <div class="nav-text" v-show="!isCollapsed">
          <span class="item-title">设置</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import service from "@/js/request.js";
import { useMeeting } from "@/store/meeting.js";


const meetingStore = useMeeting();
const isCollapsed = ref(false);
const activeId = ref(null);
const history = ref([]);
const loading = ref(false);

const handleSelectMeeting = async (id) => {
    activeId.value = id; // 更新选中状态高亮
    await meetingStore.loadMeeting(id); // 调用 store 发送请求
};

const fetchHistory = async () => {
  loading.value = true;
  try {
    // 调用后端接口
    const res = await service.get('/history');

    // 数据映射与格式化
    history.value = res.map(m => {
      const dateObj = new Date(m.start_time);
      // 格式化日期为 "MM-DD HH:mm" 的简洁格式
      const formattedDate = `${dateObj.getMonth() + 1}-${dateObj.getDate()} ${dateObj.getHours().toString().padStart(2, '0')}:${dateObj.getMinutes().toString().padStart(2, '0')}`;

      return {
        id: m.meeting_id,
        title: m.subject || '无主题会议',
        date: formattedDate
      };
    });
  } catch (e) {
    console.error("加载历史记录失败:", e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchHistory();
});
</script>

<style scoped>
/* 容器基础样式 */
.sidebar-wrapper {
  width: 280px;
  height: 100vh;
  background: rgba(255, 255, 255, 0.85); /* 略微增加不透明度以适应内容 */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  z-index: 100;
  position: relative;
  box-shadow: 1px 0 10px rgba(0, 0, 0, 0.02);
}

.sidebar-wrapper.is-collapsed {
  width: 80px;
}

/* Header */
.sidebar-header {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  margin-bottom: 10px;
}

.brand-area {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
  white-space: nowrap;
}

.brand-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
}

.brand-title {
  font-weight: 700;
  font-size: 1rem;
  color: var(--text-main);
  letter-spacing: -0.5px;
}

/* 切换按钮 */
.toggle-btn {
  border: none;
  background: transparent;
  color: var(--text-muted);
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.toggle-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--text-main);
}

.sidebar-wrapper.is-collapsed .toggle-btn {
  margin: 0 auto;
}

/* 内容列表区 */
.sidebar-content {
  flex: 1;
  padding: 0 12px;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 单个列表项 */
.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  padding: 12px 14px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-main);
  border: 1px solid transparent;
}

.nav-item:hover {
  background-color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
  transform: translateY(-1px);
}

.nav-item.active {
  background-color: rgba(37, 99, 235, 0.08);
  color: var(--primary);
  border-color: rgba(37, 99, 235, 0.1);
}

.nav-item.active .nav-icon {
  color: var(--primary);
}

.nav-icon {
  font-size: 1.1rem;
  min-width: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--text-muted);
  transition: color 0.2s;
}

.sidebar-wrapper.is-collapsed .nav-item {
  justify-content: center;
  padding: 12px 0;
}

/* 文本区域 */
.nav-text {
  margin-left: 12px;
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 0.9rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: var(--text-light);
}

.arrow {
  opacity: 0;
  transform: translateX(-5px);
  transition: all 0.2s;
}

.nav-item:hover .arrow {
  opacity: 1;
  transform: translateX(0);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
  opacity: 0.6;
}

/* 底部 */
.sidebar-footer {
  padding: 16px 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.03);
}

/* 滚动条美化 */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
}
</style>