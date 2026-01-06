<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="modal-overlay" @click="$emit('update:modelValue', false)">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>编辑用户信息</h3>
            <button class="close-btn" @click="$emit('update:modelValue', false)">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <form @submit.prevent="handleSubmit">
              <div class="form-group">
                <label>用户名</label>
                <input
                    type="text"
                    v-model="formData.username"
                    disabled
                    class="input-disabled"
                />
              </div>

              <div class="form-group">
                <label>昵称</label>
                <input
                    type="text"
                    v-model="formData.nickname"
                    placeholder="请输入昵称"
                    maxlength="50"
                />
              </div>

              <div class="form-group">
                <label>角色</label>
                <input
                    type="text"
                    v-model="formData.role"
                    placeholder="请输入角色"
                    maxlength="50"
                />
              </div>

              <div class="modal-actions">
                <button type="button" class="btn-cancel" @click="$emit('update:modelValue', false)">
                  取消
                </button>
                <button
                    type="submit"
                    class="btn-save"
                    :disabled="loading"
                >
                  <span v-if="loading" class="btn-spinner"></span>
                  {{ loading ? '保存中...' : '保存' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import {ref, watch} from 'vue';
import service from "@/js/request.js";
import {useMessageStore} from "@/store/error.js";

const props = defineProps({
  modelValue: Boolean,
  userInfo: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['update:modelValue', 'saved']);
const messageStore = useMessageStore();

const formData = ref({
  user_id: null,
  username: '',
  nickname: '',
  role: ''
});

const loading = ref(false);

watch(() => props.userInfo, (newVal) => {
  if (newVal) {
    formData.value = {
      user_id: newVal.user_id,
      username: newVal.username,
      nickname: newVal.nickname || '',
      role: newVal.role || ''
    };
  }
}, {immediate: true, deep: true});

const handleSubmit = async () => {
  loading.value = true;
  try {
    await service.put('/user/info', {
      nickname: formData.value.nickname,
      role: formData.value.role
    });

    messageStore.setSuccess('保存成功');
    emit('saved', {
      ...formData.value
    });
    emit('update:modelValue', false);
  } catch (error) {
    messageStore.setClientError('badRequest');
    console.error('保存失败:', error);
  } finally {
    loading.value = false;
  }
};
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
  max-width: 420px;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.1rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group:last-of-type {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #374151;
  font-size: 0.9rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.2s;
  outline: none;
}

.form-group input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-group input:disabled,
.input-disabled {
  background: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.modal-actions button {
  flex: 1;
  padding: 10px 16px;
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

.btn-save {
  background: #2563eb;
  color: white;
}

.btn-save:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
