<template>
  <Transition name="fade">
    <div v-if="isVisible && urgentTodos.length > 0" class="modal-backdrop">
      <div class="modal-overlay" @click="dismiss"></div>
      <div class="modal-container">
        <div class="modal-header">
          <div class="d-flex align-items-center">
            <i class="bi bi-exclamation-triangle-fill text-warning me-2"></i>
            <span class="title-text">紧急待办提醒</span>
            <span class="badge">{{ urgentTodos.length }}</span>
          </div>
          <button class="close-btn" @click="dismiss">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="todo-list">
            <div v-for="todo in urgentTodos" :key="todo.todo_id" class="todo-item">
              <div class="todo-content">
                <div class="task-text">{{ todo.task }}</div>
                <div class="deadline-info" :class="getDeadlineClass(todo.deadline)">
                  <i class="bi bi-clock me-1"></i>
                  {{ getDeadlineText(todo.deadline) }}
                </div>
              </div>
              <button
                  class="complete-btn"
                  @click="markComplete(todo)"
                  :disabled="markingComplete === todo.todo_id"
                  title="标记完成"
              >
                <i v-if="markingComplete === todo.todo_id" class="bi bi-arrow-repeat spin"></i>
                <i v-else class="bi bi-check2-circle"></i>
              </button>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-dismiss" @click="dismiss">
            稍后提醒
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import {ref, computed, onMounted, onUnmounted} from 'vue';
import service from '@/js/request.js';
import {useMessageStore} from '@/store/error.js';

const messageStore = useMessageStore();
const todos = ref([]);
const markingComplete = ref(null);
const isVisible = ref(true);
let refreshInterval = null;

const urgentTodos = computed(() => {
  const now = new Date();
  const oneHourLater = new Date(now.getTime() + 1000 * 60 * 60 * 1000);

  return todos.value
      .filter(todo => {
        if (todo.status === 'completed') return false;
        if (!todo.deadline) return false;

        const deadline = new Date(todo.deadline);
        return deadline <= oneHourLater;
      })
      .sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
});

const fetchTodos = async () => {
  try {
    const response = await service.get('/todos');
    if (response.code === 200) {
      todos.value = response.data;
    }
  } catch (error) {
    console.error('获取待办失败:', error);
  }
};

const getDeadlineClass = (deadline) => {
  const now = new Date();
  const deadlineDate = new Date(deadline);

  if (deadlineDate < now) {
    return 'overdue';
  } else if (deadlineDate < new Date(now.getTime() + 30 * 60 * 1000)) {
    return 'urgent';
  } else {
    return 'warning';
  }
};

const getDeadlineText = (deadline) => {
  const now = new Date();
  const deadlineDate = new Date(deadline);
  const diffMs = deadlineDate - now;
  const diffMins = Math.floor(diffMs / (1000 * 60));

  if (diffMs < 0) {
    const days = Math.abs(Math.floor(diffMs / (1000 * 60 * 60 * 24)));
    const hours = Math.abs(Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)));
    const mins = Math.abs(Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60)));
    if (days > 0) {
      return `已逾期 ${days}d${hours}h${mins}m`;
    }
    if (hours > 0) {
      return `已逾期 ${hours}h${mins}m`;
    }
    return `已逾期 ${mins}m`;
  } else if (diffMins < 60) {
    return `${diffMins}m 后到期`;
  } else if (diffMins < 24 * 60) {
    const hours = Math.floor(diffMins / 60);
    const mins = diffMins % 60;
    return `${hours}h${mins}m 后到期`;
  } else {
    const days = Math.floor(diffMins / (24 * 60));
    const hours = Math.floor((diffMins % (24 * 60)) / 60);
    const mins = diffMins % 60;
    if (hours > 0 || mins > 0) {
      return `${days}d${hours}h${mins}m 后到期`;
    }
    return `${days}d 后到期`;
  }
};

const markComplete = async (todo) => {
  markingComplete.value = todo.todo_id;
  try {
    const response = await service.put(`/todos/${todo.todo_id}`, {
      status: 'completed'
    });
    if (response.code === 200) {
      messageStore.addMessage('待办已标记为完成', 'success');
      await fetchTodos();
    }
  } catch (error) {
    console.error('标记完成失败:', error);
    messageStore.addMessage('操作失败，请重试', 'danger');
  } finally {
    markingComplete.value = null;
  }
};

const dismiss = () => {
  isVisible.value = false;
};

const show = () => {
  isVisible.value = true;
};

onMounted(() => {
  fetchTodos();
  refreshInterval = setInterval(fetchTodos, 60000);
});

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});

defineExpose({
  show,
  dismiss
});
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.modal-container {
  position: relative;
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: modal-in 0.3s ease-out;
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #fff8e1 0%, #fff3cd 100%);
  border-radius: 16px 16px 0 0;
}

.title-text {
  font-size: 1.1rem;
  font-weight: 700;
  color: #e65100;
}

.badge {
  background: #ff5722;
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
  margin-left: 8px;
  min-width: 24px;
  text-align: center;
}

.close-btn {
  background: rgba(255, 87, 34, 0.1);
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ff5722;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1.1rem;
}

.close-btn:hover {
  background: rgba(255, 87, 34, 0.2);
  transform: rotate(90deg);
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.todo-item {
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  border-radius: 12px;
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border-left: 4px solid #ff5722;
  transition: all 0.2s ease;
}

.todo-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(255, 87, 34, 0.15);
}

.todo-content {
  flex: 1;
  min-width: 0;
  padding-right: 12px;
}

.task-text {
  font-size: 0.95rem;
  font-weight: 600;
  color: #212121;
  margin-bottom: 6px;
  line-height: 1.4;
  word-break: break-word;
}

.deadline-info {
  font-size: 0.8rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.8);
}

.deadline-info.overdue {
  color: #d32f2f;
  background: rgba(244, 67, 54, 0.1);
}

.deadline-info.urgent {
  color: #f57c00;
  background: rgba(255, 152, 0, 0.1);
}

.deadline-info.warning {
  color: #ff8f00;
  background: rgba(255, 193, 7, 0.1);
}

.complete-btn {
  background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 8px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.complete-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #43a047 0%, #388e3c 100%);
  transform: scale(1.08);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

.complete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
  border-radius: 0 0 16px 16px;
}

.btn-dismiss {
  background: white;
  border: 2px solid #e0e0e0;
  color: #757575;
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-dismiss:hover {
  background: #f5f5f5;
  border-color: #bdbdbd;
  color: #616161;
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 滚动条样式 */
.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: rgba(255, 152, 0, 0.4);
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 152, 0, 0.6);
}
</style>
