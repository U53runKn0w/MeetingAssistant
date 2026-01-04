<template>
  <div class="row g-4 mb-4">
    <div class="col-md-4">
      <div class="card shadow-sm border-0 border-start border-4 border-primary h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="card-subtitle text-muted fw-bold">我的待办</h6>
            <span class="badge bg-primary rounded-pill">{{ myData.todoCount }}</span>
          </div>
          <div class="todo-list small">
            <div v-for="todo in myData.todos" :key="todo.id" class="text-truncate border-bottom py-1">
              <i class="bi bi-check2-circle me-1 text-success"></i> {{ todo.title }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="col-md-4">
      <div class="card shadow-sm border-0 border-start border-4 border-info h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="card-subtitle text-muted fw-bold">我的会议</h6>
            <i class="bi bi-calendar-event text-info"></i>
          </div>
          <div class="meeting-list small">
            <p class="mb-1 fw-bold text-primary">{{ myData.nextMeeting.time }}</p>
            <p class="mb-0 text-secondary">{{ myData.nextMeeting.title }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="col-md-4">
      <div class="card shadow-sm border-0 border-start border-4 border-warning h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="card-subtitle text-muted fw-bold">我的消息</h6>
            <span class="badge bg-warning text-dark rounded-pill">{{ myData.messageCount }}</span>
          </div>
          <div class="message-preview small">
            <p v-if="myData.lastMessage" class="mb-0 italic text-muted">
              <i class="bi bi-chat-left-text me-1"></i> "{{ myData.lastMessage }}"
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref} from "vue";

const myData = ref({
  todoCount: 5,
  todos: [
    {id: 1, title: '整理产品需求文档'},
    {id: 2, title: '发送周报邮件'},
    {id: 3, title: '确认下午3点的Demo'}
  ],
  nextMeeting: {
    time: '今天 15:00 - 16:30',
    title: 'Q1 季度总结与规划会议'
  },
  messageCount: 3,
  lastMessage: '张三：会议纪要已经上传，请查收。'
});
</script>

<style scoped>
.todo-list, .meeting-list, .message-preview {
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
</style>