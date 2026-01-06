<template>
  <div class="row g-4 mb-4">
    <div class="col-md-4" @click="showDetail('meeting')">
      <div class="card shadow-sm border-0 border-start border-4 border-info h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="card-subtitle text-muted fw-bold">我的会议</h6>
            <i class="bi bi-calendar-event text-info"></i>
          </div>
          <div class="meeting-list small" v-if="displayedMeetings.length > 0">
            <div v-for="meeting in displayedMeetings" :key="meeting.meeting_id || meeting.id" class="meeting-preview-item">
              <p class="mb-1 fw-bold text-primary">{{ formatTime(meeting.start_time) }}</p>
              <p class="mb-0 text-secondary">{{ meeting.subject }}</p>
            </div>
            <div v-if="myData.meetings.length > 3" class="more-meetings text-center mt-2 text-muted small">
              <i class="bi bi-chevron-down"></i> 还有 {{ myData.meetings.length - 3 }} 个会议
            </div>
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
            <span class="badge bg-primary rounded-pill">{{ displayedTodos.length }}</span>
          </div>
          <div class="todo-list small">
            <div v-for="todo in displayedTodos" :key="todo.todo_id" class="text-truncate border-bottom py-1">
              <i class="bi bi-check2-circle me-1"
                 :class="getStatusIconClass(todo.status)"></i>
              {{ todo.task }}
            </div>
            <div v-if="displayedTodos.length === 0" class="text-muted py-2">暂无待办事项</div>
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
            <div class="header-actions">
              <button v-if="activeType === 'todo'" class="settings-btn-custom" @click="openSettingsModal" title="设置">
                <i class="bi bi-gear-fill"></i>
              </button>
              <button class="close-pill" @click="isModalOpen = false">
                <i class="bi bi-x"></i> 关闭
              </button>
            </div>
          </div>

          <div class="modal-body-custom">
            <div v-if="modalDataList.length === 0" class="empty-state">
              <i class="bi bi-inbox"></i>
              <p>暂无相关详细信息</p>
            </div>

            <div v-for="(item, index) in modalDataList" :key="index" class="detail-item-card">
              <template v-if="activeType === 'todo'">
                <div v-if="editingIndex === index" class="edit-mode w-100">
                  <div class="d-flex flex-column gap-2 w-100">
                    <input v-model="editTask" class="form-control form-control-sm" placeholder="待办任务" />
                    <input v-model="editDeadline" type="datetime-local" class="form-control form-control-sm" />
                    <select v-model="editStatus" class="form-select form-select-sm">
                      <option value="pending">待确认</option>
                      <option value="in_progress">进行中</option>
                      <option value="completed">已完成</option>
                    </select>
                    <div class="d-flex gap-2">
                      <button class="btn btn-sm btn-success flex-grow-1" @click="saveTodoEdit(index)">
                        <i class="bi bi-check"></i> 保存
                      </button>
                      <button class="btn btn-sm btn-secondary flex-grow-1" @click="cancelEdit">
                        <i class="bi bi-x"></i> 取消
                      </button>
                    </div>
                  </div>
                </div>
                <template v-else>
                  <div class="status-indicator" :class="item.status"></div>
                  <div class="flex-grow-1">
                    <div class="fw-bold text-dark">{{ item.task }}</div>
                    <div class="small text-muted">
                      <i class="bi bi-clock me-1"></i> 截止于: {{ formatTime(item.deadline) }}
                    </div>
                  </div>
                  <div class="d-flex align-items-center gap-2">
                    <span :class="['badge-pill', item.status]">{{ getStatusText(item.status) }}</span>
                    <button class="btn btn-sm btn-outline-primary edit-todo-btn" @click="startTodoEdit(index, item)" title="编辑">
                      <i class="bi bi-pencil"></i>
                    </button>
                  </div>
                </template>
              </template>

              <template v-if="activeType === 'meeting'">
                <div
                    class="meeting-item-wrapper"
                    :class="{'clickable': item.status === 'completed' && item.summary}"
                    @click="item.status === 'completed' && item.summary ? openMeetingDetail(item) : null"
                >
                  <div class="status-indicator" :class="item.status === 'completed' ? 'meeting-completed' : 'meeting'"></div>
                  <div class="meeting-content">
                    <div class="meeting-header">
                      <div class="meeting-title">{{ item.subject }}</div>
                      <span :class="['meeting-badge', item.status === 'completed' ? 'completed' : 'pending']">
                        {{ item.status === 'completed' ? '已完成' : '待开始' }}
                      </span>
                    </div>
                    <div class="meeting-info">
                      <div class="meeting-time">
                        <i class="bi bi-calendar3"></i>
                        <span>{{ formatTime(item.start_time) }}</span>
                      </div>
                      <div v-if="item.duration" class="meeting-duration">
                        <i class="bi bi-clock-history"></i>
                        <span>{{ item.duration }}</span>
                      </div>
                    </div>
                    <div v-if="item.summary" class="meeting-summary">
                      <i class="bi bi-file-text"></i>
                      <span>{{ getSummaryPreview(item.summary) }}</span>
                    </div>
                  </div>
                  <div v-if="item.status === 'completed' && item.summary" class="view-detail-icon">
                    <i class="bi bi-arrow-right-circle-fill"></i>
                  </div>
                  <i v-else class="bi bi-chevron-right text-muted"></i>
                </div>
              </template>

              <template v-if="activeType === 'preference'">
                <div v-if="editingIndex === index" class="edit-mode w-100">
                  <div class="d-flex align-items-center gap-2 w-100">
                    <input v-model="editCategory" class="form-control form-control-sm" placeholder="分类" />
                    <input v-model="editValue" class="form-control form-control-sm" placeholder="值" />
                    <button class="btn btn-sm btn-success" @click="saveEdit(index)">
                      <i class="bi bi-check"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary" @click="cancelEdit">
                      <i class="bi bi-x"></i>
                    </button>
                  </div>
                </div>
                <template v-else class="w-100">
                  <div class="pref-content-wrapper w-100">
                    <div class="pref-label" @dblclick="startEdit(index, item)">{{ item.category }}</div>
                    <div class="pref-value" @dblclick="startEdit(index, item)">{{ item.value }}</div>
                    <button class="btn btn-sm btn-outline-danger delete-btn" @click="deletePreference(index)" title="删除">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </template>
              </template>
            </div>
            <div v-if="activeType === 'preference'" class="text-center mt-4">
              <button class="btn btn-outline-success rounded-pill px-4 me-2" @click="openSubModal">
                <i class="bi bi-gear-fill me-1"></i> 生成偏好
              </button>
              <button class="btn btn-outline-primary rounded-pill px-4" @click="openAddModal">
                <i class="bi bi-plus-circle me-1"></i> 手动添加
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 添加偏好模态框 -->
    <Transition name="fade">
      <div v-if="isAddModalOpen" class="glass-overlay sub-modal-overlay" @click.self="isAddModalOpen = false">
        <div class="glass-modal animate__animated animate__zoomIn">
          <div class="modal-header-custom">
            <h5 class="fw-bold mb-0">手动添加偏好</h5>
            <button class="close-pill" @click="isAddModalOpen = false">返回</button>
          </div>
          <div class="modal-body-custom">
            <div class="mb-3">
              <label class="form-label">偏好分类</label>
              <input v-model="newPreference.category" type="text" class="form-control" placeholder="例如: 主题、字体大小" />
            </div>
            <div class="mb-3">
              <label class="form-label">偏好值</label>
              <input v-model="newPreference.value" type="text" class="form-control" placeholder="例如: 暗黑模式、16px" />
            </div>
            <button class="btn btn-primary w-100" @click="addPreference" :disabled="!newPreference.category || !newPreference.value">
              添加
            </button>
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
            <PreferenceGenerator @preferenceGenerated="fetchData"></PreferenceGenerator>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="isSettingsVisible" class="glass-overlay sub-modal-overlay" @click.self="isSettingsVisible = false">
        <TodoSettings v-model="isSettingsVisible" :settings="settings" @save="handleSettingsSave"></TodoSettings>
      </div>
    </Transition>

    <!-- 会议详情模态框 -->
    <Transition name="fade">
      <div v-if="isMeetingDetailOpen" class="glass-overlay sub-modal-overlay" @click.self="closeMeetingDetail">
        <div class="glass-modal animate__animated animate__zoomIn meeting-detail-modal">
          <div class="modal-header-custom meeting-detail-header">
            <div class="d-flex align-items-center">
              <div class="icon-box meeting-detail-icon">
                <i class="bi bi-file-earmark-text-fill"></i>
              </div>
              <div>
                <h3 class="fw-bold mb-0 text-dark">会议详情</h3>
                <p class="text-muted mb-0 small">查看完整的会议纪要信息</p>
              </div>
            </div>
            <button class="close-pill" @click="closeMeetingDetail">
              <i class="bi bi-x"></i> 关闭
            </button>
          </div>

          <div class="modal-body-custom meeting-detail-body">
            <div v-if="selectedMeeting">
              <div class="meeting-detail-section">
                <h6 class="section-title">会议主题</h6>
                <div class="section-content">{{ selectedMeeting.subject }}</div>
              </div>

              <div class="meeting-detail-section">
                <h6 class="section-title">会议时间</h6>
                <div class="section-content">
                  <i class="bi bi-calendar3 me-2"></i>
                  {{ formatTime(selectedMeeting.start_time) }}
                  <span v-if="selectedMeeting.duration" class="ms-3">
                    <i class="bi bi-clock-history me-2"></i>
                    {{ selectedMeeting.duration }}
                  </span>
                </div>
              </div>

              <div class="meeting-detail-section">
                <h6 class="section-title">会议状态</h6>
                <div class="section-content">
                  <span :class="['status-badge', selectedMeeting.status]">
                    {{ selectedMeeting.status === 'completed' ? '已开展' : '待开始' }}
                  </span>
                </div>
              </div>

              <div v-if="selectedMeeting.summary" class="meeting-detail-section">
                <h6 class="section-title">会议纪要</h6>
                <div class="section-content meeting-summary-content">
                  {{ selectedMeeting.summary }}
                </div>
              </div>

              <div v-if="selectedMeeting.summary" class="meeting-detail-actions">
                <button class="btn btn-primary action-btn" @click="fillMeetingSummary">
                  <i class="bi bi-arrow-down-circle me-2"></i>
                  填入会议纪要
                </button>
                <button class="btn btn-outline-secondary action-btn" @click="closeMeetingDetail">
                  <i class="bi bi-x-circle me-2"></i>
                  取消
                </button>
              </div>
            </div>
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
import TodoSettings from "@/components/TodoSettings.vue";
import {useMessageStore} from "@/store/error.js";

const myData = ref({
  todos: [],
  meetings: [],
  nextMeeting: null,
  preferences: []
});

// 编辑相关
const editingIndex = ref(-1);
const editCategory = ref('');
const editValue = ref('');
const editItem = ref(null);

// 待办编辑相关
const editTask = ref('');
const editDeadline = ref('');
const editStatus = ref('pending');
const editTodoId = ref(null);

// 添加偏好相关
const isAddModalOpen = ref(false);
const newPreference = ref({
  category: '',
  value: ''
});

const messageStore = useMessageStore();
const isModalOpen = ref(false);
const activeType = ref(''); // 'todo', 'meeting', 'preference'

// 设置相关
const isSettingsVisible = ref(false);
const settings = ref({
  reminderTime: 30,
  urgentTimeRange: 60,
  refreshInterval: 60,
  showCompleted: false,
  showUrgentOnly: false,
  enableSound: false,
  autoOpenReminder: true
});

const openSettingsModal = () => {
  isSettingsVisible.value = true;
};

const handleSettingsSave = (newSettings) => {
  settings.value = {...settings.value, ...newSettings};
};

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
  if (activeType.value === 'todo') {
    // 根据设置过滤待办事项
    let filtered = myData.value.todos;
    if (!settings.value.showCompleted) {
      filtered = filtered.filter(todo => todo.status !== 'completed');
    }
    return filtered;
  }
  if (activeType.value === 'meeting') return myData.value.meetings;
  if (activeType.value === 'preference') return myData.value.preferences;
  return [];
});

// 首页显示的待办（根据设置过滤）
const displayedTodos = computed(() => {
  if (!settings.value.showCompleted) {
    return myData.value.todos.filter(todo => todo.status !== 'completed');
  }
  return myData.value.todos;
});

// 首页显示的会议（最多显示3个，未开始的会议优先）
const displayedMeetings = computed(() => {
  return myData.value.meetings.slice(0, 3);
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

// 获取会议纪要预览
const getSummaryPreview = (summary) => {
  if (!summary) return '';
  return summary.substring(0, 50) + (summary.length > 50 ? '...' : '');
};

const getStatusText = (status) => {
  const statusMap = {
    'pending': '待确认',
    'in_progress': '进行中',
    'completed': '已完成'
  };
  return statusMap[status] || status;
};

const getStatusIconClass = (status) => {
  const classMap = {
    'pending': 'text-warning',
    'in_progress': 'text-primary',
    'completed': 'text-success'
  };
  return classMap[status] || 'text-secondary';
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
      // 排序：未开始的会议优先（按时间），已完成的会议排在后面
      myData.value.meetings = data.data.sort((a, b) => {
        const aCompleted = a.status === 'completed';
        const bCompleted = b.status === 'completed';

        if (aCompleted !== bCompleted) {
          return aCompleted ? 1 : -1; // 未完成的在前
        }

        // 同状态的按时间排序
        return new Date(a.start_time) - new Date(b.start_time);
      });
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
  const savedSettings = localStorage.getItem('todoSettings');
  if (savedSettings) {
    try {
      const parsed = JSON.parse(savedSettings);
      settings.value = {...settings.value, ...parsed};
    } catch (error) {
      console.error('加载设置失败:', error);
    }
  }
});

const isSubModalOpen = ref(false); // 控制第二个模态框
const isMeetingDetailOpen = ref(false); // 控制会议详情模态框
const selectedMeeting = ref(null); // 选中的会议

// 打开第二个模态框的方法
const openSubModal = () => {
  isSubModalOpen.value = true;
};

// 如果你想在关闭主模态框时，同时关闭子模态框，可以修改之前的关闭逻辑
const closeMainModal = () => {
  isModalOpen.value = false;
  isSubModalOpen.value = false;
  isMeetingDetailOpen.value = false;
};

// 打开会议详情
const openMeetingDetail = (meeting) => {
  selectedMeeting.value = meeting;
  isMeetingDetailOpen.value = true;
};

// 关闭会议详情
const closeMeetingDetail = () => {
  isMeetingDetailOpen.value = false;
  selectedMeeting.value = null;
};

// 填入会议纪要到输入框
const fillMeetingSummary = () => {
  if (selectedMeeting.value && selectedMeeting.value.summary) {
    // 触发自定义事件，将会议纪要传递给父组件
    const event = new CustomEvent('fillMeetingSummary', {
      detail: { summary: selectedMeeting.value.summary }
    });
    window.dispatchEvent(event);
    closeMeetingDetail();
    isModalOpen.value = false;
  }
};

// 编辑偏好功能
const startEdit = (index, item) => {
  editingIndex.value = index;
  editItem.value = {...item};
  editCategory.value = item.category;
  editValue.value = item.value;
};

const saveEdit = async (index) => {
  if (!editCategory.value.trim() || !editValue.value.trim()) return;

  try {
    // 删除旧的偏好
    await service.delete(`/preferences/${myData.value.preferences[index].category}`);
    // 添加新的偏好（使用新的分类名）
    await service.post('/preferences', {
      category: editCategory.value,
      value: editValue.value
    });
    // 重新获取数据
    await fetchData();
    editingIndex.value = -1;
    editItem.value = null;
    editCategory.value = '';
    editValue.value = '';
  } catch (error) {
    console.error('更新偏好失败:', error);
    messageStore.setError('更新偏好失败，请稍后重试');
  }
};

const cancelEdit = () => {
  editingIndex.value = -1;
  editItem.value = null;
  editCategory.value = '';
  editValue.value = '';
};

// 添加偏好功能
const openAddModal = () => {
  newPreference.value = {category: '', value: ''};
  isAddModalOpen.value = true;
};

const addPreference = async () => {
  if (!newPreference.value.category.trim() || !newPreference.value.value.trim()) return;

  try {
    await service.post('/preferences', {
      category: newPreference.value.category,
      value: newPreference.value.value
    });
    await fetchData();
    isAddModalOpen.value = false;
    newPreference.value = {category: '', value: ''};
  } catch (error) {
    console.error('添加偏好失败:', error);
    messageStore.setError('添加偏好失败，请稍后重试');
  }
};

// 删除偏好功能
const deletePreference = async (index) => {
  if (!confirm('确定要删除这个偏好吗？')) return;

  try {
    await service.delete(`/preferences/${myData.value.preferences[index].category}`);
    myData.value.preferences.splice(index, 1);
  } catch (error) {
    console.error('删除偏好失败:', error);
    messageStore.setError('删除偏好失败，请稍后重试');
  }
};

// 待办编辑功能
const startTodoEdit = (index, item) => {
  editingIndex.value = index;
  editTodoId.value = item.todo_id;
  editTask.value = item.task;
  editDeadline.value = item.deadline ? item.deadline.slice(0, 16) : '';
  editStatus.value = item.status;
};

const saveTodoEdit = async (index) => {
  if (!editTask.value.trim()) {
    messageStore.setInfo('待办任务不能为空');
    return;
  }

  try {
    // 使用 /api/todos/update 接口进行更新
    await service.put('/todos/update', {
      todos: [{
        todo_id: editTodoId.value,
        task: editTask.value.trim(),
        deadline: editDeadline.value,
        status: editStatus.value
      }]
    });
    await fetchData();
    editingIndex.value = -1;
    editTodoId.value = null;
    editTask.value = '';
    editDeadline.value = '';
    editStatus.value = 'pending';
    messageStore.setSuccess('待办已更新');
  } catch (error) {
    console.error('更新待办失败:', error);
    messageStore.setError('更新待办失败，请稍后重试');
  }
};
</script>

<style scoped>
/* 统一卡片容器高度 */
.card {
  min-height: 180px;
  max-height: 180px;
  transition: transform 0.2s;
  cursor: pointer;
  overflow: hidden;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1) !important;
}

/* 卡片主体 */
.card-body {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1.25rem;
  overflow: hidden;
}

/* 卡片头部 */
.card-header-custom {
  flex-shrink: 0;
  margin-bottom: 12px;
}

/* 统一列表容器 */
.todo-list,
.meeting-list,
.preference-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
  max-height: 140px;
}

/* 滚动条样式 */
.todo-list::-webkit-scrollbar,
.meeting-list::-webkit-scrollbar,
.preference-list::-webkit-scrollbar {
  width: 4px;
}

.todo-list::-webkit-scrollbar-track,
.meeting-list::-webkit-scrollbar-track,
.preference-list::-webkit-scrollbar-track {
  background: transparent;
}

.todo-list::-webkit-scrollbar-thumb,
.meeting-list::-webkit-scrollbar-thumb,
.preference-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
}

.todo-list::-webkit-scrollbar-thumb:hover,
.meeting-list::-webkit-scrollbar-thumb:hover,
.preference-list::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* 统一列表项样式 */
.meeting-preview-item {
  padding: 8px 0;
  border-bottom: 1px dashed #e0e0e0;
}

.meeting-preview-item:last-child {
  border-bottom: none;
}

.meeting-preview-item .text-primary {
  font-size: 0.85rem;
  margin-bottom: 2px;
}

.meeting-preview-item .text-secondary {
  font-size: 0.8rem;
  line-height: 1.3;
}

/* 待办列表项 */
.todo-list > div {
  padding: 8px 0;
  border-bottom: 1px dashed #e0e0e0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.todo-list > div:last-child {
  border-bottom: none;
}

/* 偏好列表项 */
.preference-list > div {
  padding: 8px 0;
  border-bottom: 1px dashed #e0e0e0;
}

.preference-list > div:last-child {
  border-bottom: none;
}

/* 更多提示 */
.more-meetings {
  cursor: pointer;
  transition: opacity 0.2s;
  padding-top: 4px;
}

.more-meetings:hover {
  opacity: 0.7;
}

/* 卡片标题 */
.card-subtitle {
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

/* 统一徽章样式 */
.badge {
  font-size: 0.75rem;
  padding: 0.35em 0.65em;
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

.status-indicator.in_progress {
  background: #2196f3;
}

.status-indicator.meeting {
  background: #00acc1;
}

.status-indicator.meeting-completed {
  background: #4caf50;
}

/* 会议状态徽章 */
.meeting-status-badge {
  margin-top: 4px;
}

.meeting-status-badge .badge {
  font-size: 0.65rem;
  padding: 2px 8px;
  border-radius: 4px;
}

/* 会议纪要预览 */
.summary-preview {
  color: #666;
  font-style: italic;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 5. 按钮与标签 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.settings-btn-custom {
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

.settings-btn-custom:hover {
  background: #e8eaf6;
  color: #3f51b5;
}

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

.badge-pill.in_progress {
  background: #e3f2fd;
  color: #1565c0;
}

/* 偏好独有样式 */
.pref-label {
  font-weight: bold;
  color: #666;
  width: 40%;
  cursor: pointer;
  transition: color 0.2s;
}

.pref-label:hover {
  color: #43a047;
}

.pref-value {
  color: #333;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}

.pref-value:hover {
  color: #43a047;
}

/* 编辑模式样式 */
.edit-mode {
  display: flex;
  align-items: center;
  gap: 8px;
}

.edit-mode input {
  flex: 1;
}

/* 待办编辑按钮 */
.edit-todo-btn {
  padding: 4px 8px;
  font-size: 0.8rem;
}

/* 偏好内容容器 */
.pref-content-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 12px;
}

.pref-label {
  font-weight: bold;
  color: #666;
  min-width: 100px;
  cursor: pointer;
  transition: color 0.2s;
}

.pref-label:hover {
  color: #43a047;
}

.pref-value {
  color: #333;
  font-weight: 500;
  flex: 1;
  cursor: pointer;
  transition: color 0.2s;
}

.pref-value:hover {
  color: #43a047;
}

/* 删除按钮样式 */
.delete-btn {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
}

.detail-item-card:hover .delete-btn {
  opacity: 1;
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

/* 会议项样式优化 */
.meeting-item-wrapper {
  display: flex;
  align-items: center;
  width: 100%;
  transition: all 0.2s ease;
}

.meeting-item-wrapper.clickable {
  cursor: pointer;
}

.meeting-item-wrapper.clickable:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 172, 193, 0.1);
}

.meeting-content {
  flex: 1;
  min-width: 0;
}

.meeting-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.meeting-title {
  font-weight: bold;
  color: #212121;
  font-size: 1rem;
}

.meeting-badge {
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 600;
}

.meeting-badge.pending {
  background: #e3f2fd;
  color: #1976d2;
}

.meeting-badge.completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.meeting-info {
  display: flex;
  gap: 16px;
  font-size: 0.8rem;
  color: #757575;
  margin-bottom: 6px;
}

.meeting-time,
.meeting-duration {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meeting-time i,
.meeting-duration i {
  color: #00acc1;
}

.meeting-summary {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 0.8rem;
  color: #9e9e9e;
  font-style: italic;
}

.meeting-summary i {
  margin-top: 2px;
  color: #00acc1;
}

.view-detail-icon {
  color: #00acc1;
  font-size: 1.3rem;
  margin-left: 8px;
  flex-shrink: 0;
}

/* 会议详情模态框样式 */
.meeting-detail-modal {
  max-width: 700px;
  max-height: 85vh;
}

.meeting-detail-header {
  background: linear-gradient(135deg, #e0f7fa 0%, #e1f5fe 100%);
}

.meeting-detail-icon {
  background: linear-gradient(135deg, #00acc1 0%, #0097a7 100%);
  color: white;
}

.meeting-detail-body {
  background: white;
  padding: 24px 30px;
}

.meeting-detail-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f5f5f5;
}

.meeting-detail-section:last-of-type {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #757575;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.section-content {
  font-size: 1rem;
  color: #424242;
  line-height: 1.6;
}

.status-badge {
  padding: 6px 14px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
}

.status-badge.completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.pending {
  background: #fff3e0;
  color: #f57c00;
}

.meeting-summary-content {
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  font-size: 0.95rem;
  line-height: 1.8;
  color: #616161;
  white-space: pre-wrap;
  max-height: 300px;
  overflow-y: auto;
}

.meeting-detail-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f5f5f5;
}

.action-btn {
  flex: 1;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
  text-align: center;
  justify-content: center;
  display: flex;
  align-items: center;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 会议详情模态框的滚动条样式 */
.meeting-summary-content::-webkit-scrollbar {
  width: 6px;
}

.meeting-summary-content::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 3px;
}

.meeting-summary-content::-webkit-scrollbar-thumb {
  background: rgba(0, 172, 193, 0.3);
  border-radius: 3px;
}

.meeting-summary-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 172, 193, 0.5);
}
</style>