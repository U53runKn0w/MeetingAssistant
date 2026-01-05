<template>
  <div class="row g-4 mb-4">
    <div class="col-md-4" @click="showDetail('meeting')">
      <div class="card shadow-sm border-0 border-start border-4 border-info h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="card-subtitle text-muted fw-bold">我的会议</h6>
            <i class="bi bi-calendar-event text-info"></i>
          </div>
          <div class="meeting-list small" v-if="myData.nextMeeting">
            <p class="mb-1 fw-bold text-primary">{{ formatTime(myData.nextMeeting.start_time) }}</p>
            <p class="mb-0 text-secondary">{{ myData.nextMeeting.subject }}</p>
          </div>
          <div v-else class="text-muted small">暂无会议安排</div>
        </div>
      </div>
    </div>

    <div class="col-md-4" @click="showDetail('todo')">
      <div class="card shadow-sm border-0 border-start border-4 border-primary h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="card-subtitle text-muted fw-bold">我的待办</h6>
            <span class="badge bg-primary rounded-pill">{{ myData.todos.length }}</span>
          </div>
          <div class="todo-list small">
            <div v-for="todo in myData.todos" :key="todo.todo_id" class="text-truncate border-bottom py-1">
              <i class="bi bi-check2-circle me-1"
                 :class="todo.status === 'completed' ? 'text-success' : 'text-warning'"></i>
              {{ todo.task }}
            </div>
            <div v-if="myData.todos.length === 0" class="text-muted py-2">暂无待办事项</div>
          </div>
        </div>
      </div>
    </div>

    <div class="col-md-4" @click="showDetail('preference')">
      <div class="card shadow-sm border-0 border-start border-4 border-success h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="card-subtitle text-muted fw-bold">我的偏好</h6>
            <i class="bi bi-person-gear text-success"></i>
          </div>
          <div class="preference-list small">
            <div v-for="pref in myData.preferences" :key="pref.category"
                 class="d-flex justify-content-between border-bottom py-1">
              <span class="text-secondary">{{ pref.category }}:</span>
              <span class="fw-bold text-dark">{{ pref.value }}</span>
            </div>
            <div v-if="myData.preferences.length === 0" class="text-muted py-2">尚未设置偏好</div>
          </div>
        </div>
      </div>
    </div>

    <Transition name="fade">
      <div v-if="isModalOpen" class="glass-overlay" @click.self="isModalOpen = false">
        <div class="glass-modal animate__animated animate__fadeInUp">

          <div class="modal-header-custom">
            <div class="d-flex align-items-center">
              <div :class="['icon-box', activeType]">
                <i :class="getIcon(activeType)"></i>
              </div>
              <div>
                <h3 class="fw-bold mb-0 text-dark">{{ modalTitle }}</h3>
                <p class="text-muted mb-0 small">{{ modalSubtitle }}</p>
              </div>
            </div>
            <button class="close-pill" @click="isModalOpen = false">
              <i class="bi bi-x"></i> 关闭
            </button>
          </div>

          <div class="modal-body-custom">
            <div v-if="modalDataList.length === 0" class="empty-state">
              <i class="bi bi-inbox"></i>
              <p>暂无相关详细信息</p>
            </div>

            <div v-for="(item, index) in modalDataList" :key="index" class="detail-item-card">
              <template v-if="activeType === 'todo'">
                <div class="status-indicator" :class="item.status"></div>
                <div class="flex-grow-1">
                  <div class="fw-bold text-dark">{{ item.task }}</div>
                  <div class="small text-muted">
                    <i class="bi bi-clock me-1"></i> 截止于: {{ formatTime(item.deadline) }}
                  </div>
                </div>
                <span :class="['badge-pill', item.status]">{{ item.status }}</span>
              </template>

              <template v-if="activeType === 'meeting'">
                <div class="status-indicator meeting"></div>
                <div class="flex-grow-1">
                  <div class="fw-bold text-dark">{{ item.subject }}</div>
                  <div class="small text-muted">
                    <i class="bi bi-calendar3 me-1"></i> {{ formatTime(item.start_time) }}
                  </div>
                </div>
                <i class="bi bi-chevron-right text-muted"></i>
              </template>

              <template v-if="activeType === 'preference'">
                <div class="pref-label">{{ item.category }}</div>
                <div class="pref-value">{{ item.value }}</div>
              </template>
            </div>
            <div v-if="activeType === 'preference'" class="text-center mt-4">
              <button class="btn btn-outline-success rounded-pill px-4" @click="openSubModal">
                <i class="bi bi-gear-fill me-1"></i> 生成偏好
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="isSubModalOpen" class="glass-overlay sub-modal-overlay" @click.self="isSubModalOpen = false">
        <div class="glass-modal animate__animated animate__zoomIn">
          <div class="modal-header-custom">
            <h5 class="fw-bold mb-0">生成偏好</h5>
            <button class="close-pill" @click="isSubModalOpen = false">返回</button>
          </div>
          <div class="modal-body-custom">
            <PreferenceGenerator></PreferenceGenerator>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import {ref, onMounted, computed} from "vue";
import service from "@/js/request.js";
import PreferenceGenerator from "@/components/PreferenceGenerator.vue";
import {useMessageStore} from "@/store/error.js";

const myData = ref({
  todos: [],
  meetings: [],
  nextMeeting: null,
  preferences: []
});

const messageStore = useMessageStore();
const isModalOpen = ref(false);
const activeType = ref(''); // 'todo', 'meeting', 'preference'

const getIcon = (type) => {
  const icons = {meeting: 'bi-calendar-event', todo: 'bi-check2-square', preference: 'bi-sliders'};
  return icons[type];
};

const modalSubtitle = computed(() => {
  if (activeType.value === 'todo') return `当前共有 ${modalDataList.value.length} 项任务`;
  if (activeType.value === 'meeting') return '接下来的日程安排';
  return '根据您的习惯个性化定制';
});

// 获取弹窗标题
const modalTitle = computed(() => {
  const titles = {todo: '所有待办事项', meeting: '会议日程列表', preference: '个人偏好设置'};
  return titles[activeType.value] || '详细信息';
});

// 获取当前要展示的详细数据
const modalDataList = computed(() => {
  if (activeType.value === 'todo') return myData.value.todos;
  if (activeType.value === 'meeting') return myData.value.meetings;
  if (activeType.value === 'preference') return myData.value.preferences;
  return [];
});

const showDetail = (type) => {
  activeType.value = type;
  isModalOpen.value = true;
};

const formatTime = (isoString) => {
  if (!isoString) return "";
  const date = new Date(isoString);
  return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
};

const fetchData = async () => {
  service.get(`/todos`).then(data => {
    if (data.code === 200) {
      myData.value.todos = data.data.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
    }
  }).catch(error => {
    messageStore.setNetworkError('failed');
    console.error("待办加载失败", error);
  });


  service.get(`/meetings`).then(data => {
    if (data.code === 200) {
      myData.value.meetings = data.data.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
      if (data.data.length > 0) myData.value.nextMeeting = myData.value.meetings[0];
    }
  }).catch(error => {
    messageStore.setNetworkError('failed');
    console.error("会议加载失败", error);
  });

  service.get(`/preferences`).then(data => {
    if (data.code === 200) {
      myData.value.preferences = data.data;
    }
  }).catch(err => {
    messageStore.setNetworkError('failed');
    console.error("偏好加载失败", err);
  });
};

onMounted(() => {
  fetchData();
});

const isSubModalOpen = ref(false); // 控制第二个模态框

// 打开第二个模态框的方法
const openSubModal = () => {
  isSubModalOpen.value = true;
};

// 如果你想在关闭主模态框时，同时关闭子模态框，可以修改之前的关闭逻辑
const closeMainModal = () => {
  isModalOpen.value = false;
  isSubModalOpen.value = false;
};
</script>

<style scoped>
.todo-list, .meeting-list, .preference-list {
  min-height: 60px;
}

.card-subtitle {
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

/* 鼠标悬停微动效果 */
.col-md-4 .card {
  transition: transform 0.2s;
  cursor: pointer;
}

.col-md-4 .card:hover {
  transform: translateY(-5px);
}

/* 全屏弹窗样式 */
.custom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-modal-content {
  background: white;
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  border-radius: 15px;
  padding: 30px;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.card {
  transition: transform 0.2s;
  cursor: pointer;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1) !important;
}

/* 1. 毛玻璃背景遮罩 */
.glass-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 2. 悬浮窗主体 */
.glass-modal {
  background: white;
  width: 90%;
  max-width: 650px;
  max-height: 80vh;
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

/* 3. 头部样式 */
.modal-header-custom {
  padding: 24px 30px;
  border-bottom: 1px solid #f1f1f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-right: 15px;
}

.icon-box.meeting {
  background: #e0f7fa;
  color: #00acc1;
}

.icon-box.todo {
  background: #e8eaf6;
  color: #3f51b5;
}

.icon-box.preference {
  background: #e8f5e9;
  color: #43a047;
}

/* 4. 内容列表卡片化 */
.modal-body-custom {
  padding: 20px 30px;
  overflow-y: auto;
  background: #fafafa;
}

.detail-item-card {
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.detail-item-card:hover {
  transform: scale(1.02);
  border-color: #eee;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 状态条装饰 */
.status-indicator {
  width: 4px;
  height: 30px;
  border-radius: 2px;
  margin-right: 15px;
}

.status-indicator.pending {
  background: #ffb300;
}

.status-indicator.completed {
  background: #4caf50;
}

.status-indicator.meeting {
  background: #00acc1;
}

/* 5. 按钮与标签 */
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

.badge-pill {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
}

.badge-pill.pending {
  background: #fff8e1;
  color: #ff8f00;
}

.badge-pill.completed {
  background: #e8f5e9;
  color: #2e7d32;
}

/* 偏好独有样式 */
.pref-label {
  font-weight: bold;
  color: #666;
  width: 40%;
}

.pref-value {
  color: #333;
  font-weight: 500;
}

/* Vue 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.sub-modal-overlay {
  z-index: 2100; /* 比第一个模态框的 2000 更高 */
  background: rgba(0, 0, 0, 0.2); /* 稍微深一点的遮罩感 */
}

/* 让第二个模态框小一点，体现层级感 */
.sub-modal-overlay .glass-modal {
  max-width: 450px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* 进场动画：使用缩放效果区分 */
.animate__zoomIn {
  animation-duration: 0.3s;
}
</style>