<template>
  <div class="quick-questions-wrapper">
    <div class="quick-questions-header">
      <i class="bi bi-lightbulb-fill"></i>
      <span>常用问题</span>
    </div>
    <div class="quick-questions-grid">
      <button
          v-for="(question, index) in questions"
          :key="index"
          class="quick-question-card"
          @click="$emit('quick-send', question)"
          :disabled="disabled"
      >
        <i class="bi bi-chat-quote-fill card-icon"></i>
        <span>{{ question }}</span>
        <i class="bi bi-arrow-right-circle-fill arrow-icon"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  questions: {
    type: Array,
    default: () => []
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

defineEmits(['quick-send']);
</script>

<style scoped>
.quick-questions-wrapper {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.quick-questions-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #667eea;
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 20px;
}

.quick-questions-header i {
  font-size: 1.1rem;
}

.quick-questions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.quick-question-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
  border: 2px solid #e8ecf3;
  border-radius: 12px;
  color: #2c3e50;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.quick-question-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.5s ease;
}

.quick-question-card:hover:not(:disabled)::before {
  left: 100%;
}

.quick-question-card:hover:not(:disabled) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.35);
}

.quick-question-card .card-icon {
  font-size: 1.2rem;
  color: #667eea;
  transition: color 0.3s ease;
}

.quick-question-card:hover:not(:disabled) .card-icon {
  color: white;
}

.quick-question-card .arrow-icon {
  font-size: 1.1rem;
  color: #bdc3c7;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
}

.quick-question-card:hover:not(:disabled) .arrow-icon {
  opacity: 1;
  transform: translateX(0);
  color: white;
}

.quick-question-card:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #f8f9fa;
}

@media (max-width: 768px) {
  .quick-questions-grid {
    grid-template-columns: 1fr;
  }

  .quick-questions-wrapper {
    padding: 18px;
  }
}
</style>
