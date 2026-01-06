<template>
  <div class="glass-overlay sub-modal-overlay" @click.self="$emit('update:modelValue', false)">
    <div class="glass-modal animate__animated animate__zoomIn">
      <div class="modal-header-custom">
        <h5 class="fw-bold mb-0">待办设置</h5>
        <button class="close-pill" @click="$emit('update:modelValue', false)">关闭</button>
      </div>
      <div class="modal-body-custom">
        <div class="settings-form">
          <div class="form-group">
            <label class="form-label">待办提醒时间（分钟）</label>
            <input
                type="number"
                v-model.number="localSettings.reminderTime"
                class="form-input"
                placeholder="请输入提醒时间"
                min="1"
            />
            <small class="form-hint">系统将在待办截止前指定分钟数发送提醒</small>
          </div>

          <div class="form-group">
            <label class="form-label">紧急待办时间范围（分钟）</label>
            <input
                type="number"
                v-model.number="localSettings.urgentTimeRange"
                class="form-input"
                placeholder="请输入紧急时间范围"
                min="1"
            />
            <small class="form-hint">在此时间范围内的待办将被标记为紧急</small>
          </div>

          <div class="form-group">
            <label class="form-label">待办刷新间隔（秒）</label>
            <input
                type="number"
                v-model.number="localSettings.refreshInterval"
                class="form-input"
                placeholder="请输入刷新间隔"
                min="10"
            />
            <small class="form-hint">系统自动刷新待办列表的时间间隔</small>
          </div>

          <div class="form-group">
            <label class="form-label">显示设置</label>
            <div class="toggle-group">
              <label class="toggle-label">
                <input type="checkbox" v-model="localSettings.showCompleted"/>
                <span>显示已完成的待办</span>
              </label>
              <label class="toggle-label">
                <input type="checkbox" v-model="localSettings.showUrgentOnly"/>
                <span>仅显示紧急待办</span>
              </label>
              <label class="toggle-label">
                <input type="checkbox" v-model="localSettings.enableSound"/>
                <span>启用提醒声音</span>
              </label>
              <label class="toggle-label">
                <input type="checkbox" v-model="localSettings.autoOpenReminder"/>
                <span>自动打开提醒弹窗</span>
              </label>
            </div>
          </div>

          <div class="text-center mt-4">
            <button class="btn btn-primary rounded-pill px-5" @click="handleSave">
              <i class="bi bi-check-lg me-1"></i> 保存设置
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, watch} from 'vue';
import {useMessageStore} from "@/store/error.js";

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  settings: {
    type: Object,
    default: () => ({
      reminderTime: 30,
      urgentTimeRange: 60,
      refreshInterval: 60,
      showCompleted: false,
      showUrgentOnly: false,
      enableSound: false,
      autoOpenReminder: true
    })
  }
});

const emit = defineEmits(['update:modelValue', 'save']);

const messageStore = useMessageStore();
const localSettings = ref({...props.settings});

watch(() => props.settings, (newSettings) => {
  localSettings.value = {...newSettings};
}, {deep: true});

const handleSave = () => {
  try {
    localStorage.setItem('todoSettings', JSON.stringify(localSettings.value));
    emit('save', localSettings.value);
    emit('update:modelValue', false);
    messageStore.setSuccess('设置已保存');
  } catch (error) {
    messageStore.setClientError('badRequest');
    console.error('保存设置失败:', error);
  }
};
</script>

<style scoped>
/* 毛玻璃背景遮罩 */
.glass-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  z-index: 2100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sub-modal-overlay {
  z-index: 2100;
  background: rgba(0, 0, 0, 0.2);
}

/* 悬浮窗主体 */
.glass-modal {
  background: white;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* 头部样式 */
.modal-header-custom {
  padding: 24px 30px;
  border-bottom: 1px solid #f1f1f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 内容区域 */
.modal-body-custom {
  padding: 20px 30px;
  overflow-y: auto;
  background: #fafafa;
}

/* 按钮与标签 */
.close-pill {
  border: none;
  background: #f5f5f5;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.close-pill:hover {
  background: #eeeeee;
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

.toggle-label span {
  line-height: 1.5;
}

/* Vue 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 进场动画：使用缩放效果区分 */
.animate__zoomIn {
  animation-duration: 0.3s;
}

@keyframes zoomIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
