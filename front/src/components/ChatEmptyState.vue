<template>
  <div class="empty-state-container">
    <div class="empty-state-content">
      <div class="robot-icon-wrapper">
        <i class="bi bi-robot"></i>
      </div>
      <h4 class="empty-state-title">智能会议分析助手</h4>
      <p class="empty-state-subtitle">准备就绪，请在下方输入关于会议的问题</p>

      <QuickQuestions
          :questions="commonQuestions"
          @quick-send="quickSend"
          :disabled="isGenerating"
      />
    </div>
  </div>
</template>

<script setup>
import QuickQuestions from './QuickQuestions.vue';

defineProps({
  commonQuestions: {
    type: Array,
    default: () => []
  },
  isGenerating: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['quick-send']);

const quickSend = (question) => {
  emit('quick-send', question);
};
</script>

<style scoped>
.empty-state-container {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  height: 100%;
  padding: 30px 20px;
  overflow-y: auto;
}

.empty-state-content {
  text-align: center;
  max-width: 600px;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.robot-icon-wrapper {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
  animation: pulse 2s ease-in-out infinite;
}

.robot-icon-wrapper i {
  font-size: 2.5rem;
  color: white;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 12px 28px rgba(102, 126, 234, 0.4);
  }
}

.empty-state-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
}

.empty-state-subtitle {
  color: #7f8c8d;
  font-size: 1rem;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .robot-icon-wrapper {
    width: 60px;
    height: 60px;
  }

  .robot-icon-wrapper i {
    font-size: 2rem;
  }

  .empty-state-title {
    font-size: 1.25rem;
  }
}
</style>
