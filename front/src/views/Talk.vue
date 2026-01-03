<template>
  <div class="container mt-5 mb-5">
    <header class="text-center mb-5">
      <h1 class="display-5 fw-bold text-primary">会议助手</h1>
      <p class="lead text-muted">通过智能分析和组织，轻松简化您的会议记录</p>
    </header>

    <div class="row g-4">
      <div class="col-lg-5">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0"><i class="bi bi-journal-text me-2"></i>会议内容</h5>
            <div>
              <input
                  type="file"
                  ref="fileInput"
                  @change="handleFileUpload"
                  accept="audio/*"
                  style="display: none"
              >
              <button
                  @click="$refs.fileInput.click()"
                  class="btn btn-sm btn-outline-primary"
                  :disabled="isUploading"
              >
                <span v-if="isUploading" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-file-earmark-music me-1"></i>
                {{ isUploading ? '转录中...' : '上传音频' }}
              </button>
            </div>
          </div>

          <div class="card-body d-flex flex-column">
            <div v-if="error" class="alert alert-danger py-2 small mb-3">
              <i class="bi bi-exclamation-circle me-2"></i>{{ error }}
            </div>

            <div class="flex-grow-1">
              <label class="form-label small fw-bold text-secondary">会议纪要文本</label>
              <textarea
                  v-model="meetingText"
                  class="form-control"
                  style="height: 400px; resize: none;"
                  placeholder="在此处粘贴会议记录，或点击上方按钮上传音频自动转录..."
              ></textarea>
            </div>

            <div class="mt-3 p-2 bg-light rounded">
              <p class="small text-muted mb-0">
                <i class="bi bi-info-circle me-1"></i>
                支持直接编辑转录后的文本以修正错误。
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-7">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-white py-3">
            <h5 class="card-title mb-0"><i class="bi bi-chat-dots me-2"></i>智能分析</h5>
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
                  <span class="badge bg-secondary me-2">{{ msg.type === 'Action' ? '调用工具' : '参数' }}</span>
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

      <div v-if="toResultButtonShow" class="text-center mt-4">
        <button @click="toResult" class="btn btn-outline-primary px-5 py-2 rounded-pill">
          <i class="bi bi-arrow-right me-2"></i>
          前往结果页面
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import {ref, nextTick, watch, onMounted} from 'vue';
import {parseReActContent} from "@/js/util.js";
import {fetchEventSource} from '@microsoft/fetch-event-source';
import router from "@/router/index.js";
import {dummyMeeting} from "@/js/etc.js";
import {useConversation} from "@/js/store.js";


const meetingText = ref('');
const userQuery = ref('');
const isLoading = ref(false);
const error = ref(null);
const messages = ref([]);
const chatContainer = ref(null);
const isUploading = ref(false);
const toResultButtonShow = ref(false);
const url = 'http://localhost:5000/api/chat';
const conversation = useConversation();

onMounted(() => {
  if (conversation.messages.length > 0) {
    messages.value = conversation.messages;
    toResultButtonShow.value = true;
  }
})

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  isUploading.value = true;
  error.value = null;

  const formData = new FormData();
  formData.append('file', file);

  try {
    // 这里替换为你真实的录音转文字 API 接口
    // const response = await axios.post('http://localhost:5000/api/transcript', formData);
    // meetingText.value = response.data.text;

    // 模拟延时和返回结果
    await new Promise(resolve => setTimeout(resolve, 2000));
    meetingText.value = dummyMeeting;
  } catch (err) {
    error.value = "文件转录失败，请检查后端接口。";
  } finally {
    isUploading.value = false;
    event.target.value = ''; // 重置 file input
  }
};

const sendMessage = async () => {
  if (!userQuery.value || isLoading.value) return;

  toResultButtonShow.value = false;
  const token = localStorage.getItem('token');
  let headers = {
    'Content-Type': 'application/json',
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  messages.value = [];
  isLoading.value = true;
  error.value = null;
  const currentQuery = userQuery.value; // 先备份

  let rawAgentBuffer = "";
  let agentStartIndex = -1;

  // 手动关闭连接
  const ctrl = new AbortController();

  try {
    await fetchEventSource(url, {
      method: 'POST',
      headers: headers,
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

// 自动滚动聊天区域
watch(messages, () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
}, {deep: true});

const toResult = async () => {
  conversation.messages = messages.value;
  await router.push('/result');
}
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
</style>