<template>
  <form @submit.prevent="$emit('send')" class="mt-auto">
    <div class="input-group">
      <input
        v-if="!isHistorySession || isGenerating"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        type="text"
        class="form-control form-control-lg"
        placeholder="输入关于会议的问题（例如：总结待办事项）..."
        :disabled="isGenerating"
      />
      <input
        v-else
        type="text"
        class="form-control form-control-lg bg-light"
        value="当前对话已结束，点击右侧按钮开启新对话"
        readonly
      />
      <button
        v-if="isGenerating"
        type="button"
        class="btn btn-danger px-4"
        @click="$emit('stop')"
      >
        <i class="bi bi-stop-fill me-2"></i>停止
      </button>
      <button
        v-else-if="isHistorySession"
        type="button"
        class="btn btn-primary px-4"
        @click="$emit('new-session')"
      >
        <i class="bi bi-plus-circle me-2"></i>新对话
      </button>
      <button
        v-else
        type="submit"
        class="btn btn-primary px-4"
        :disabled="!modelValue"
      >
        <i class="bi bi-send-fill me-2"></i>发送
      </button>
    </div>

    <p v-if="!isHistorySession" class="text-muted small mt-2">
      提示：系统将结合左侧录入的会议内容回答您的问题。
    </p>
  </form>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  isGenerating: {
    type: Boolean,
    default: false
  },
  isHistorySession: {
    type: Boolean,
    default: false
  }
});

defineEmits(['update:modelValue', 'send', 'stop', 'new-session']);
</script>
