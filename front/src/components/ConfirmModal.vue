<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="modal-overlay" @click="$emit('update:modelValue', false)">
        <div class="modal-content" @click.stop>
          <div class="modal-icon" :class="type">
            <slot name="icon">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
                <path
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
            </slot>
          </div>

          <h3 v-if="title">{{ title }}</h3>

          <div class="modal-body">
            <slot>{{ message }}</slot>
          </div>

          <div class="modal-actions">
            <button class="btn-cancel" @click="$emit('update:modelValue', false)">
              {{ cancelText }}
            </button>
            <button
                :class="['btn-confirm', type]"
                :disabled="loading"
                @click="$emit('confirm')"
            >
              <span v-if="loading" class="btn-spinner"></span>
              {{ loading ? loadingText : confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue: Boolean,      // 控制显示隐藏 (v-model)
  title: String,            // 标题
  message: String,          // 内容
  type: {                   // 类型：danger (红), primary (蓝)
    type: String,
    default: 'danger'
  },
  confirmText: {type: String, default: '确认'},
  cancelText: {type: String, default: '取消'},
  loadingText: {type: String, default: '处理中...'},
  loading: Boolean          // 按钮加载状态
});

defineEmits(['update:modelValue', 'confirm']);
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-content {
  background: white;
  width: 90%;
  max-width: 360px;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

/* 危险类型样式 */
.modal-icon.danger {
  background: #fee2e2;
  color: #ef4444;
}

.btn-confirm.danger {
  background: #ef4444;
  color: white;
}

.btn-confirm.danger:hover {
  background: #dc2626;
}

/* 主要类型样式 */
.modal-icon.primary {
  background: #eff6ff;
  color: #2563eb;
}

.btn-confirm.primary {
  background: #2563eb;
  color: white;
}

.btn-confirm.primary:hover {
  background: #1d4ed8;
}

.modal-content h3 {
  margin: 0 0 8px;
  color: #1f2937;
  font-size: 1.1rem;
}

.modal-body {
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 24px;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.modal-actions button {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-cancel {
  background: #f3f4f6;
  color: #4b5563;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 动画部分保持不变 */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content {
  animation: modal-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modal-in {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>