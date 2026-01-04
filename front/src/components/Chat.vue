<template>
  <div class="col-lg-7">
    <div class="card shadow-sm border-0 h-100">
      <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0"><i class="bi bi-chat-dots me-2"></i>智能分析</h5>
        <button
            class="btn btn-sm btn-outline-secondary"
            @click="isFullScreen = true"
            title="全屏查看"
        >
          <i class="bi bi-arrows-fullscreen"></i>
        </button>
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

          <div v-if="isLoading && messages.length > 0">
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
                :disabled="isLoading"
            />
            <button type="submit" class="btn btn-primary px-4" :disabled="isLoading || !userQuery">
              <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-send-fill me-2"></i>
              {{ isLoading ? '分析中' : '发送' }}
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
import {useChat} from "@/store/chat.js";
import {storeToRefs} from "pinia";
import {nextTick, onMounted, ref, watch} from "vue";
import {useMeeting} from "@/store/meeting.js";

const url = 'http://localhost:5000/api/chat';
const chat = useChat();
const meeting = useMeeting();
const {question: userQuery} = storeToRefs(chat)
const {text: meetingText} = storeToRefs(meeting)
const {error: error} = storeToRefs(meeting)
const {messages: messages} = storeToRefs(chat)
const isLoading = ref(false);
const toResultButtonShow = ref(false);
const chatContainer = ref(null);
const isFullScreen = ref(false);
const fullChatContainer = ref(null);

onMounted(() => {
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') isFullScreen.value = false;
  });

  if (chat.messages.length > 0 && chat.question.length > 0) {
    toResultButtonShow.value = true;
  }
})

const sendMessage = async () => {
  if (!userQuery.value || isLoading.value) return;

  toResultButtonShow.value = false;

  messages.value = [];
  isLoading.value = true;
  error.value = null;
  const currentQuery = userQuery.value; // 先备份
  chat.question = currentQuery;

  let rawAgentBuffer = "";
  let agentStartIndex = -1;

  // 手动关闭连接
  const ctrl = new AbortController();

  try {
    await fetchEventSource(url, {
      method: 'POST',
      headers: createHeaders(),
      body: JSON.stringify({
        meeting: meetingText.value,
        query: currentQuery
      }),
      signal: ctrl.signal,
      openWhenHidden: true,

      onopen: async (response) => {
        if (!response.ok) {
          error.value = `请求错误: ${response.statusText}`;

          if (response.status === 401) {
            await router.push('/login');
          }
        }
      },

      onmessage: (event) => {
        const data = JSON.parse(event.data);

        switch (data.type) {
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
            isLoading.value = false;
            ctrl.abort();
            chat.buttonsShow = true;
            break;
        }
      },

      onclose: () => {
        isLoading.value = false;
        console.log("连接正常关闭");
      },

      onerror: (err) => {
        console.error("SSE 异常:", err);
        error.value = '连接中断，请检查后端服务。';
        isLoading.value = false;
        ctrl.abort();
        throw err;
      }
    });
  } catch (err) {
    console.error("Fetch Error:", err);
    error.value = err.message;
  } finally {
    toResultButtonShow.value = true;
  }
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

// 3. 额外处理：当用户点击“全屏”按钮打开弹窗时，立即滚动到底部
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
  max-height: 400px;
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