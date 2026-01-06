<template>
  <div v-if="visible" class="modal-backdrop fade show"></div>
  <div class="modal fade show" v-if="visible" style="display: block;" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content shadow-lg">
        <div class="modal-header">
          <h5 class="modal-title"><i class="bi bi-gear me-2"></i>思维导图设置</h5>
          <button type="button" class="btn-close" @click="handleCancel"></button>
        </div>
        <div class="modal-body">
          <div class="settings-form">
            <div class="form-group">
              <label class="form-label">主题样式</label>
              <select v-model="localSettings.theme" class="form-input">
                <option value="default">默认</option>
                <option value="forest">森林</option>
                <option value="dark">暗色</option>
                <option value="neutral">中性</option>
              </select>
              <small class="form-hint">选择思维导图的配色主题</small>
            </div>

            <div class="form-group">
              <label class="form-label">渲染间隔（毫秒）</label>
              <input
                  type="number"
                  v-model.number="localSettings.renderInterval"
                  class="form-input"
                  placeholder="请输入渲染间隔"
                  min="100"
                  step="100"
              />
              <small class="form-hint">思维导图刷新渲染的时间间隔</small>
            </div>

            <div class="form-group">
              <label class="form-label">显示设置</label>
              <div class="toggle-group">
                <label class="toggle-label">
                  <input type="checkbox" v-model="localSettings.autoRender"/>
                  <span>自动渲染导图</span>
                </label>
                <label class="toggle-label">
                  <input type="checkbox" v-model="localSettings.showSourceCode"/>
                  <span>显示源代码</span>
                </label>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="handleCancel">取消</button>
          <button class="btn btn-primary" @click="handleSave" :disabled="isSaving">
            <span v-if="isSaving" class="spinner-border spinner-border-sm me-1"></span>
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, watch} from "vue";
import {useMessageStore} from "@/store/error.js";

const props = defineProps({
  visible: Boolean,
  settings: Object
});

const emit = defineEmits(['update:visible', 'save']);

const localSettings = ref({...props.settings});
const isSaving = ref(false);
const messageStore = useMessageStore();

watch(() => props.settings, (newSettings) => {
  localSettings.value = {...newSettings};
}, {deep: true});

watch(() => props.visible, (newVal) => {
  if (newVal) {
    localSettings.value = {...props.settings};
  }
});

const handleCancel = () => {
  localSettings.value = {...props.settings};
  emit('update:visible', false);
};

const handleSave = async () => {
  isSaving.value = true;
  try {
    localStorage.setItem('mindmapSettings', JSON.stringify(localSettings.value));
    messageStore.setSuccess('思维导图设置已保存');
    emit('save', {...localSettings.value});
    // 触发 storage 事件，让其他组件感知到设置变化
    window.dispatchEvent(new StorageEvent('storage', {
      key: 'mindmapSettings',
      newValue: JSON.stringify(localSettings.value)
    }));
  } catch (error) {
    messageStore.setClientError('badRequest');
    console.error('保存设置失败:', error);
  } finally {
    isSaving.value = false;
  }
};
</script>

<style scoped>
.modal-backdrop {
  z-index: 1060;
}

.modal {
  z-index: 1065;
}

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
  color: #1f2937;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.2s;
  outline: none;
}

.form-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-hint {
  display: block;
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 6px;
}

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
  color: #1f2937;
  cursor: pointer;
  user-select: none;
  padding: 6px 0;
}

.toggle-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #3b82f6;
}

.toggle-label span {
  line-height: 1.5;
}
</style>
