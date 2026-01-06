<template>
  <div v-if="isVisible">
    <div class="modal-backdrop fade show"></div>
    <div class="modal fade show" style="display: block;" tabindex="-1">
      <div class="modal-dialog modal-xl modal-dialog-scrollable" style="height: 90vh;">
        <div class="modal-content h-100 shadow-lg">
          <div class="modal-header">
            <h5 class="modal-title text-primary">
              <i class="bi bi-robot me-2"></i>详细分析结果
            </h5>
            <button type="button" class="btn-close" @click="close"></button>
          </div>
          <div
              class="modal-body bg-light overflow-auto"
              ref="fullChatContainer"
              style="height: 70vh;"
              @scroll.passive="handleScroll"
          >
            <ChatMessage
                v-for="(msg, i) in messages"
                :key="'full-'+i"
                :msg="msg"
                :full-screen="true"
            />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="close">关闭</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  messages: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['close']);

const fullChatContainer = ref(null);
const autoScrollFull = ref(true);

const close = () => {
  emit('close');
};

const handleScroll = () => {
  if (!fullChatContainer.value) return;

  const { scrollTop, scrollHeight, clientHeight } = fullChatContainer.value;
  const distanceToBottom = scrollHeight - (scrollTop + clientHeight);

  autoScrollFull.value = distanceToBottom < 100;
};

// 打开时自动滚动到底部
watch(() => props.isVisible, (newVal) => {
  if (newVal) {
    autoScrollFull.value = true;
    nextTick(() => {
      if (fullChatContainer.value) {
        fullChatContainer.value.scrollTop = fullChatContainer.value.scrollHeight;
      }
    });
  }
});

// 监听 messages 变化，自动滚动
watch(() => props.messages, () => {
  nextTick(() => {
    if (props.isVisible && fullChatContainer.value && autoScrollFull.value) {
      fullChatContainer.value.scrollTop = fullChatContainer.value.scrollHeight;
    }
  });
}, { deep: true });
</script>

<style scoped>
.modal-backdrop {
  z-index: 1050;
}

.modal {
  z-index: 1055;
  background: rgba(0, 0, 0, 0.2);
}

.modal-body {
  scroll-behavior: smooth;
}
</style>
