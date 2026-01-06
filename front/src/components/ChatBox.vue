<template>
  <div class="col-lg-7">
    <div class="card shadow-sm border-0 h-100">
      <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0"><i class="bi bi-chat-dots me-2"></i>智能分析</h5>

        <div class="d-flex align-items-center">
          <div class="form-check mb-0 me-3">
            <label class="form-check-label" for="flexCheckDefault">测试</label>
            <input
              class="form-check-input"
              type="checkbox"
              id="flexCheckDefault"
              v-model="isTest"
            >
          </div>
          <button
            class="btn btn-sm btn-outline-secondary"
            @click="openFullScreen"
            title="全屏查看"
          >
            <i class="bi bi-arrows-fullscreen"></i>
          </button>
        </div>
      </div>

      <ChatFullScreen
        :is-visible="isFullScreen"
        :messages="messages"
        @close="closeFullScreen"
      />

      <div class="card-body d-flex flex-column" style="min-height: 500px;">
        <div
          class="chat-box flex-grow-1 overflow-auto mb-3 p-2"
          ref="chatContainer"
          @scroll.passive="handleScroll"
        >
          <ChatEmptyState
            v-if="messages.length === 0"
            :common-questions="commonQuestions"
            :is-generating="isGenerating"
            @quick-send="quickSend"
          />

          <ChatMessage
            v-for="(msg, i) in messages"
            :key="i"
            :msg="msg"
          />

          <LoadingIndicator
            v-if="isGenerating && messages.length > 0"
            :last-message="messages[messages.length - 1]"
          />
        </div>

        <ChatInput
          v-model="userQuery"
          :is-generating="isGenerating"
          @send="sendMessage"
          @stop="stopGeneration"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { fetchEventSource } from "@microsoft/fetch-event-source";
import router from "@/router/index.js";
import { createHeaders, parseReActContent } from "@/js/util.js";
import { useChatStore } from "@/store/chat.js";
import { storeToRefs } from "pinia";
import { ref, onMounted } from "vue";
import { useMessageStore } from "@/store/error.js";
import { useScroll } from "@/composables/useScroll.js";

import ChatMessage from "./ChatMessage.vue";
import ChatEmptyState from "./ChatEmptyState.vue";
import ChatFullScreen from "./ChatFullScreen.vue";
import ChatInput from "./ChatInput.vue";
import LoadingIndicator from "./LoadingIndicator.vue";

const productUrl = 'http://localhost:5000/api/chat';
const testUrl = 'http://localhost:5000/api/chat/test';

const emit = defineEmits(['refresh-history']);

const chatStore = useChatStore();
const { question: userQuery } = storeToRefs(chatStore);
const { messages } = storeToRefs(chatStore);
const messageStore = useMessageStore();

const isGenerating = ref(false);
const chatContainer = ref(null);
const isFullScreen = ref(false);
const isTest = ref(false);
const abortController = ref(null);

// SSE 流处理状态
const rawAgentBuffer = ref("");
const agentStartIndex = ref(-1);

const { autoScroll, handleScroll, watchMessages, initScrollListener } = useScroll(chatContainer);

const commonQuestions = ref([
  '总结会议的待办事项',
  '提取会议的关键决策',
  '分析会议的主要议题',
  '列出会议参与者及其观点',
  '生成会议摘要'
]);

// 初始化滚动监听
initScrollListener();
watchMessages(messages);

const openFullScreen = () => isFullScreen.value = true;
const closeFullScreen = () => isFullScreen.value = false;

const quickSend = (question) => {
  if (isGenerating.value) return;
  userQuery.value = question;
  sendMessage();
};

onMounted(() => {
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeFullScreen();
    if (e.key === 'Delete') openFullScreen();
  });
});

const sendMessage = async (isResume = false) => {
  if (!userQuery.value || isGenerating.value) return;

  const url = isTest.value ? testUrl : productUrl;
  chatStore.buttonsShow = false;

  if (!isResume) {
    messages.value = [];
  }
  chatStore.messages = [];
  isGenerating.value = true;

  const currentQuery = userQuery.value;
  chatStore.question = currentQuery;

  rawAgentBuffer.value = "";
  agentStartIndex.value = -1;

  const ctrl = new AbortController();
  abortController.value = ctrl;

  try {
    await fetchEventSource(url, {
      method: 'POST',
      headers: createHeaders(),
      body: JSON.stringify({
        meeting: chatStore.text,
        query: currentQuery,
        session_id: chatStore.sessionId,
        step_offset: isResume ? messages.value.length : 0
      }),
      signal: ctrl.signal,
      openWhenHidden: true,

      onopen: async (response) => {
        if (!response.ok) {
          await handleResponseError(response);
        }
      },

      onmessage: (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
      },

      onclose: () => {
        if (!isGenerating.value) console.log("连接正常关闭");
      },

      onerror: async (err) => {
        console.error("SSE异常：", err);
        await handleConnectionError(err, ctrl);
      }
    });
  } catch (err) {
    console.error("Fetch Error:", err);
    handleFetchError(err);
  }
};

const handleResponseError = async (response) => {
  if (response.status === 401) {
    messageStore.setAuthError('tokenExpired');
    await router.push('/login');
  } else if (response.status >= 500) {
    messageStore.setServerError('internal');
  } else if (response.status >= 400) {
    messageStore.setClientError('badRequest');
  } else {
    messageStore.setError(`请求失败: ${response.statusText || '未知错误'}`);
  }
};

const handleMessage = (data) => {
  switch (data.type) {
    case 'meta':
      chatStore.sessionId = data.content;
      emit('refresh-history');
      break;

    case 'resumed':
      console.log(`已恢复到步骤 ${data.content}`);
      break;

    case 'observation':
      let content = data.content;
      content = content.substring(content.indexOf(':') + 1).trim();
      messages.value.push({ type: 'Observation', text: content });
      rawAgentBuffer.value = "";
      agentStartIndex.value = -1;
      break;

    case 'stream':
      const chunk = data.content;
      rawAgentBuffer.value += chunk;
      const parsedSegments = parseReActContent(rawAgentBuffer.value);

      if (agentStartIndex.value === -1) {
        agentStartIndex.value = messages.value.length;
        messages.value.push(...parsedSegments);
      } else {
        messages.value.splice(agentStartIndex.value, messages.value.length - agentStartIndex.value, ...parsedSegments);
      }
      break;

    case 'done':
      isGenerating.value = false;
      abortController.value?.abort();
      chatStore.buttonsShow = true;
      break;
  }
};

const handleConnectionError = async (err, ctrl) => {
  if (chatStore.sessionId && isGenerating.value) {
    console.log("尝试断线重连...");
    messageStore.setWarning('连接中断，正在重新连接...');
    await new Promise(resolve => setTimeout(resolve, 2000));
    await sendMessage(true);
  } else {
    messageStore.setNetworkError('failed');
    messageStore.setInfo('提示：如果问题持续存在，请联系管理员');
    isGenerating.value = false;
    ctrl.abort();
    throw err;
  }
};

const handleFetchError = (err) => {
  if (err.name === 'AbortError') {
    messageStore.setInfo('已停止生成');
  } else {
    messageStore.setError('发生未知错误，请刷新页面后重试');
  }
};

const stopGeneration = () => {
  abortController.value?.abort();
  abortController.value = null;
  isGenerating.value = false;
  chatStore.buttonsShow = true;
};

const newSession = () => {
  if (isGenerating.value) return;
  messages.value = [];
  chatStore.question = '';
  chatStore.sessionId = '';
  chatStore.buttonsShow = true;
};

defineExpose({
  stopGeneration,
  newSession
});
</script>

<style scoped>
.chat-box {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf3 100%);
  border-radius: 12px;
  border: none;
  height: 360px;
  position: relative;
  scroll-behavior: smooth;
}

summary {
  cursor: pointer;
  outline: none;
}

:deep(.mermaid-viewer svg) {
  max-width: 100%;
  height: auto;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}
</style>
