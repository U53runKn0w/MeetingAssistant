<template>
  <div class="sidebar-wrapper" :class="{ 'is-collapsed': isCollapsed }">
    <div class="sidebar-header">
      <div class="brand-area" v-show="!isCollapsed">
        <div class="logo-dot"></div>
        <span class="brand-title">历史记录</span>
      </div>

      <button class="menu-toggle" @click="isCollapsed = !isCollapsed" :title="isCollapsed ? '展开' : '收起'">
        <svg v-if="isCollapsed" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor"
             stroke-width="2">
          <path d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 17l-5-5m0 0l5-5m-5 5h12"/>
        </svg>
      </button>
    </div>

    <div class="sidebar-content">
      <div class="list-group">
        <div
            v-for="item in history"
            :key="item.id"
            class="nav-item"
            :class="{ 'centered': isCollapsed }"
        >
          <div class="nav-icon" v-show="!isCollapsed">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 8v4l3 3m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/>
            </svg>
          </div>
          <div class="nav-text" v-show="!isCollapsed">
            <div class="title">{{ item.title }}</div>
            <div class="date">{{ item.date }}</div>
          </div>
          <div class="tooltip" v-if="isCollapsed">{{ item.title }}</div>
        </div>
      </div>
    </div>

    <div class="sidebar-footer" v-show="!isCollapsed">
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue';

const isCollapsed = ref(false);

// 模拟数据
const history = ref([
  {id: 1, title: '关于项目进度的讨论', date: '2024-03-20'},
  {id: 2, title: '季度预算规划会议', date: '2024-03-19'},
  {id: 3, title: '技术架构选型评审', date: '2024-03-18'},
]);
</script>

<style scoped>
.sidebar-wrapper {
  --sb-bg: #f9fafb;
  --sb-hover: #eceef2;
  --sb-active: #e2e4e9;
  --primary: #2563eb;
  --text-main: #374151;
  --text-dim: #6b7280;

  width: 260px;
  height: 100vh;
  background-color: var(--sb-bg);
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.sidebar-wrapper.is-collapsed {
  width: 64px;
}

/* Header 融合设计 */
.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.brand-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-dot {
  width: 10px;
  height: 10px;
  background: var(--primary);
  border-radius: 2px;
}

.brand-title {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-main);
}

/* 按钮一体化 */
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
  transition: background 0.2s;
}

.sidebar-wrapper.is-collapsed .menu-toggle {
  margin: 0 auto;
}

.menu-toggle:hover {
  background: var(--sb-hover);
  color: var(--text-main);
}

/* 列表项优化 */
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  padding: 10px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-main);
}

.nav-item:hover {
  background: var(--sb-hover);
}

.nav-item.centered {
  justify-content: center;
  padding: 10px 0;
}

.nav-icon {
  min-width: 24px;
  display: flex;
  justify-content: center;
  color: var(--text-dim);
}

.nav-text {
  margin-left: 12px;
  overflow: hidden;
}

.title {
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.date {
  font-size: 0.75rem;
  color: var(--text-dim);
}

/* 底部设计 */
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
  font-size: 0.7rem;
  color: var(--text-dim);
}

/* 简单的 Tooltip 效果 */
.nav-item:hover .tooltip {
  display: block;
}

.tooltip {
  display: none;
  position: absolute;
  left: 100%;
  margin-left: 10px;
  background: #333;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 100;
}
</style>

