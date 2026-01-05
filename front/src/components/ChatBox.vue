<template>
  <div class="col-lg-7">
    <div class="card shadow-sm border-0 h-100">
      <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0"><i class="bi bi-chat-dots me-2"></i>智能分析</h5>

        <div class="d-flex align-items-center">
          <div class="form-check mb-0 me-3"><label class="form-check-label" for="flexCheckDefault">
            测试
          </label>
            <input
                class="form-check-input"
                type="checkbox"
                id="flexCheckDefault"
                v-model="isTest"
            >
          </div>
          <button
              class="btn btn-sm btn-outline-secondary"
              @click="isFullScreen = true"
              title="全屏查看"
          >
            <i class="bi bi-arrows-fullscreen"></i>
          </button>
        </div>
      </div>

      <div v-if="isFullScreen" class="modal-backdrop fade show"></div>
      <div class="modal fade show" v-if="isFullScreen" style="display: block;" tabindex="-1">
        <div class="modal-dialog modal-xl modal-dialog-scrollable" style="height: 90vh;">
          <div class="modal-content h-100 shadow-lg">
            <div class="modal-header">
              <h5 class="modal-title text-primary"><i class="bi bi-robot me-2"></i>详细分析结果</h5>
              <button type="button" class="btn-close" @click="isFullScreen = false"></button>
            </div>
            <div
                class="modal-body bg-light overflow-auto"
                ref="fullChatContainer"
                style="height: 70vh;"
            >
              <div v-for="(msg, i) in messages" :key="'full-'+i"
                   :class="['message-block mb-3', msg.type.toLowerCase().replace(' ', '-')]">

                <div v-if="msg.type === 'Thought'"
                     class="p-3 bg-white rounded border-start border-4 border-info shadow-sm">
                  <small class="text-info fw-bold"><i class="bi bi-cpu me-1"></i>思考中:</small>
                  <p class="mb-0 text-secondary italic">{{ msg.text }}</p>
                </div>

                <div v-else-if="msg.type === 'Action' || msg.type === 'Action Input'" class="mt-2">
                  <span class="badge bg-secondary me-2">{{ msg.type === 'Action' ? '调用工具' : '参数详情' }}</span>
                  <code class="small text-dark">{{ msg.text }}</code>
                </div>

                <div v-else-if="msg.type === 'Observation'" class="alert alert-secondary py-2 mt-2">
                  <div class="fw-bold small mb-1">
                    <i class="bi bi-tools me-1"></i>工具返回结果:
                  </div>
                  <pre class="mb-0 small" style="white-space: pre-wrap;">{{ msg.text }}</pre>
                </div>

                <div v-else-if="msg.type === 'Final Answer'" class="card border-primary shadow-sm">
                  <div class="card-header bg-primary text-white py-2">回答内容</div>
                  <div class="card-body fs-5" v-html="msg.text"></div>
                </div>

                <div v-else class="p-2 text-muted small">
                  <strong>{{ msg.type }}:</strong> {{ msg.text }}
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="isFullScreen = false">关闭</button>
            </div>
          </div>
        </div>
      </div>

      <div class="card-body d-flex flex-column" style="min-height: 500px;">
        <div class="chat-box flex-grow-1 overflow-auto mb-3 p-2" ref="chatContainer">
          <div v-if="messages.length === 0" class="text-center text-muted mt-5">
            <i class="bi bi-robot display-4"></i>
            <p class="mt-2">准备就绪，请在下方输入关于会议的问题。</p>
          </div>

          <div v-for="(msg, i) in messages" :key="i"
               :class="['message-block mb-3', msg.type.toLowerCase().replace(' ', '-')]">

            <div v-if="msg.type === 'Thought'" class="p-2 bg-light rounded border-start border-4 border-info">
              <small class="text-info fw-bold"><i class="bi bi-cpu me-1"></i>思考中:</small>
              <p class="mb-0 small text-secondary italic">{{ msg.text }}</p>
            </div>

            <div v-else-if="msg.type === 'Action' || msg.type === 'Action Input'" class="mt-2">
              <span class="badge bg-secondary me-2">{{ msg.type === 'Action' ? '调用工具' : '参数详情' }}</span>
              <code class="small text-dark">{{ msg.text }}</code>
            </div>

            <div v-else-if="msg.type === 'Observation'" class="alert alert-secondary py-2 mt-2">
              <div class="fw-bold small mb-1">
                <i class="bi bi-tools me-1"></i>工具返回结果:
              </div>
              <pre class="mb-0 small" style="white-space: pre-wrap;">{{ msg.text }}</pre>
            </div>

            <div v-else-if="msg.type === 'Final Answer'" class="card border-primary mt-2">
              <div class="card-header bg-primary text-white py-1 small">回答</div>
              <div class="card-body py-3" v-html="msg.text"></div>
            </div>

            <div v-else class="default-content">
              <strong>{{ msg.type }}:</strong> {{ msg.text }}
            </div>
          </div>

          <div v-if="isGenerating && messages.length > 0">
            <template v-if="messages[messages.length - 1].type === 'Action Input'">
              <div class="alert alert-secondary py-2 mt-2 border-0 shadow-sm opacity-75">
                <div class="d-flex align-items-center">
                  <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                  <span class="small text-muted">调用工具中，请稍候...</span>
                </div>
              </div>
            </template>
          </div>
        </div>

        <form @submit.prevent="sendMessage" class="mt-auto">
          <div class="input-group">
            <input
                v-model="userQuery"
                type="text"
                class="form-control form-control-lg"
                placeholder="输入关于会议的问题（例如：总结待办事项）..."
                :disabled="isGenerating"
            />
            <button
                v-if="isGenerating"
                type="button"
                class="btn btn-danger px-4"
                @click="stopGeneration"
            >
              <i class="bi bi-stop-fill me-2"></i>停止
            </button>
            <button v-else type="submit" class="btn btn-primary px-4" :disabled="!userQuery">
              <i class="bi bi-send-fill me-2"></i>发送
            </button>
          </div>

          <p class="text-muted small mt-2">提示：系统将结合左侧录入的会议内容回答您的问题。</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import {fetchEventSource} from "@microsoft/fetch-event-source";
import router from "@/router/index.js";
import {createHeaders, parseReActContent} from "@/js/util.js";
import {useChatStore} from "@/store/chat.js";
import {storeToRefs} from "pinia";
import {nextTick, onMounted, ref, watch} from "vue";
import {useMessageStore} from "@/store/error.js";


const productUrl = 'http://localhost:5000/api/chat';
const testUrl = 'http://localhost:5000/api/chat/test';
let url;

// 定义 emit 用于触发父组件的事件
const emit = defineEmits(['refresh-history']);

const chatStore = useChatStore();
const {question: userQuery} = storeToRefs(chatStore)
const messageStore = useMessageStore()
const {messages: messages} = storeToRefs(chatStore)

const isGenerating = ref(false);
const chatContainer = ref(null);
const isFullScreen = ref(false);
const fullChatContainer = ref(null);
const isTest = ref(false);
const abortController = ref(null);

onMounted(() => {
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') isFullScreen.value = false;
    if (e.key === 'Delete') isFullScreen.value = true;
  });
})

const sendMessage = async (isResume = false) => {
  if (!userQuery.value || isGenerating.value) return;

  if (isTest.value) {
    url = testUrl;
  } else {
    url = productUrl;
  }
  chatStore.buttonsShow = false;
  if (!isResume) {
    messages.value = [];
  }
  isGenerating.value = true;
  const currentQuery = userQuery.value; // 先备份
  chatStore.question = currentQuery;

  let rawAgentBuffer = "";
  let agentStartIndex = -1;

  // 手动关闭连接
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
        }
      },

      onmessage: (event) => {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case 'meta':
            chatStore.sessionId = data.content;
            // 收到 sessionId 后立即刷新历史记录
            emit('refresh-history');
            break;

          case 'resumed':
            // 恢复成功，从数据库获取已保存的步骤
            console.log(`已恢复到步骤 ${data.content}`);
            // 从数据库加载历史步骤（可选，如果前端已缓存则不需要）
            break;

          case 'observation':
            let content = data.content
            content = content.substring(content.indexOf(':') + 1).trim();
            messages.value.push({type: 'Observation', text: content});
            rawAgentBuffer = "";
            agentStartIndex = -1;
            break;

          case 'stream':
            const chunk = data.content;
            rawAgentBuffer += chunk;
            const parsedSegments = parseReActContent(rawAgentBuffer);

            if (agentStartIndex === -1) {
              agentStartIndex = messages.value.length;
              messages.value.push(...parsedSegments);
            } else {
              messages.value.splice(agentStartIndex, messages.value.length - agentStartIndex, ...parsedSegments);
            }
            break;

          case 'done':
            isGenerating.value = false;
            ctrl.abort();
            chatStore.buttonsShow = true;
            break;
        }
      },

      onclose: () => {
        if (!isGenerating.value) {
          console.log("连接正常关闭");
        }
      },

      onerror: async (err) => {
        console.error("SSE异常：", err);
        // 如果有 session_id，尝试重连
        if (chatStore.sessionId && isGenerating.value) {
          console.log("尝试断线重连...");
          messageStore.setWarning('连接中断，正在重新连接...');
          await new Promise(resolve => setTimeout(resolve, 2000)); // 等待2秒
          await sendMessage(true); // 重连时传入 isResume=true
        } else {
          messageStore.setNetworkError('failed');
          messageStore.setInfo('提示：如果问题持续存在，请联系管理员');
          isGenerating.value = false;
          ctrl.abort();
          throw err;
        }
      }
    });
  } catch (err) {
    console.error("Fetch Error:", err);
    if (err.name === 'AbortError') {
      messageStore.setInfo('已停止生成');
    } else {
      messageStore.setError('发生未知错误，请刷新页面后重试');
    }
  }
};

const stopGeneration = () => {
  if (abortController.value) {
    abortController.value.abort();
    abortController.value = null;
  }
  isGenerating.value = false;
  chatStore.messages = [];
  chatStore.buttonsShow = true;
};


watch(messages, () => {
  nextTick(() => {
    // 滚动主界面的聊天框
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }

    // 滚动全屏弹窗的聊天框（如果弹窗当前是打开状态）
    if (isFullScreen.value && fullChatContainer.value) {
      fullChatContainer.value.scrollTop = fullChatContainer.value.scrollHeight;
    }
  });
}, {deep: true});

// 全屏打开弹窗时，立即滚动到底部
watch(isFullScreen, (newVal) => {
  if (newVal) {
    nextTick(() => {
      if (fullChatContainer.value) {
        fullChatContainer.value.scrollTop = fullChatContainer.value.scrollHeight;
      }
    });
  }
});
</script>

<style scoped>
.chat-box {
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  height: 360px;
}

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

.modal-backdrop {
  z-index: 1050;
}

.modal {
  z-index: 1055;
  background: rgba(0, 0, 0, 0.2); /* 简单的遮罩层 */
}

/* 让全屏下的回答字体稍大，方便阅读 */
.modal-body .fs-5 {
  line-height: 1.6;
}

/* 优化代码块在全屏下的显示 */
.modal-body pre {
  background: #2d2d2d;
  color: #ccc;
  padding: 15px;
}

.chat-box,
.modal-body {
  scroll-behavior: smooth;
}

/* 确保 Modal Body 在内容超出时出现滚动条 */
.modal-body {
  overflow-y: auto;
}

/* 确保源码查看器有手型 */
summary {
  cursor: pointer;
  outline: none;
}

/* 调整生成的 SVG 大小 */
:deep(.mermaid-viewer svg) {
  max-width: 100%;
  height: auto;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}
</style>