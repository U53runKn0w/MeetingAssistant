<template>
  <form @submit.prevent="$emit('send')" class="mt-auto">
    <div class="input-group">
      <input
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        type="text"
        class="form-control form-control-lg"
        placeholder="输入关于会议的问题（例如：总结待办事项）..."
        :disabled="isGenerating"
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
        v-else
        type="submit"
        class="btn btn-primary px-4"
        :disabled="!modelValue"
      >
        <i class="bi bi-send-fill me-2"></i>发送
      </button>
    </div>

    <p class="text-muted small mt-2">
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
  }
});

defineEmits(['update:modelValue', 'send', 'stop']);
</script>
