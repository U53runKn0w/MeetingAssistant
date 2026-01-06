<template>
  <div :class="['message-block mb-3', typeClass, { 'mt-2': isInline }]">
    <!-- 思考中 -->
    <div v-if="msg.type === 'Thought'"
         class="p-2 bg-light rounded border-start border-4 border-info">
      <small class="text-info fw-bold">
        <i class="bi bi-cpu me-1"></i>思考中:
      </small>
      <p class="mb-0 small text-secondary italic">{{ msg.text }}</p>
    </div>

    <!-- 调用工具 / 参数详情 -->
    <div v-else-if="isAction" class="mt-2">
      <span class="badge bg-secondary me-2">
        {{ msg.type === 'Action' ? '调用工具' : '参数详情' }}
      </span>
      <code class="small text-dark">{{ msg.text }}</code>
    </div>

    <!-- 工具返回结果 -->
    <div v-else-if="msg.type === 'Observation'" class="alert alert-secondary py-2 mt-2">
      <div class="fw-bold small mb-1">
        <i class="bi bi-tools me-1"></i>工具返回结果:
      </div>
      <pre class="mb-0 small" style="white-space: pre-wrap;">{{ msg.text }}</pre>
    </div>

    <!-- 最终回答 -->
    <div v-else-if="msg.type === 'Final Answer'" class="card border-primary mt-2">
      <div :class="['card-header bg-primary text-white', headerClass]">
        {{ fullScreen ? '回答内容' : '回答' }}
      </div>
      <div :class="['card-body', bodyClass]" v-html="msg.text"></div>
    </div>

    <!-- 默认内容 -->
    <div v-else class="default-content">
      <strong>{{ msg.type }}:</strong> {{ msg.text }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  msg: {
    type: Object,
    required: true
  },
  fullScreen: {
    type: Boolean,
    default: false
  }
});

const typeClass = computed(() => 
  props.msg.type.toLowerCase().replace(' ', '-')
);

const isAction = computed(() => 
  props.msg.type === 'Action' || props.msg.type === 'Action Input'
);

const isInline = computed(() => 
  isAction.value || props.msg.type === 'Observation' || props.msg.type === 'Final Answer'
);

const headerClass = computed(() => 
  props.fullScreen ? 'py-2' : 'py-1 small'
);

const bodyClass = computed(() => 
  props.fullScreen ? 'fs-5' : 'py-3'
);
</script>

<style scoped>
.message-block {
  transition: all 0.3s ease;
}

code {
  word-break: break-all;
}

pre {
  background: #f1f1f1;
  padding: 10px;
  border-radius: 4px;
}

/* 全屏模式下的样式覆盖 */
:deep(.modal-body) pre {
  background: #2d2d2d;
  color: #ccc;
  padding: 15px;
}

:deep(.modal-body) .fs-5 {
  line-height: 1.6;
}
</style>
