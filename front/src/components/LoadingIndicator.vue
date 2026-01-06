<template>
  <div v-if="shouldShow" class="alert alert-secondary py-2 mt-2 border-0 shadow-sm opacity-75">
    <div class="d-flex align-items-center">
      <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
      <span class="small text-muted">调用工具中，请稍候...</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  lastMessage: {
    type: Object,
    required: true
  }
});

const shouldShow = computed(() => 
  props.lastMessage?.type === 'Action Input'
);
</script>
