<template>
  <div class="container mt-5 mb-5">
    <header class="text-center mb-5">
      <h1 class="display-5 fw-bold text-primary">会议助手</h1>
      <p class="lead text-muted">通过智能分析和组织，轻松简化您的会议记录</p>
    </header>

    <div class="row g-4 mb-4">
      <div class="col-md-4">
        <div class="card shadow-sm border-0 border-start border-4 border-primary h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h6 class="card-subtitle text-muted fw-bold">我的待办</h6>
              <span class="badge bg-primary rounded-pill">{{ myData.todoCount }}</span>
            </div>
            <div class="todo-list small">
              <div v-for="todo in myData.todos" :key="todo.id" class="text-truncate border-bottom py-1">
                <i class="bi bi-check2-circle me-1 text-success"></i> {{ todo.title }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card shadow-sm border-0 border-start border-4 border-info h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h6 class="card-subtitle text-muted fw-bold">我的会议</h6>
              <i class="bi bi-calendar-event text-info"></i>
            </div>
            <div class="meeting-list small">
              <p class="mb-1 fw-bold text-primary">{{ myData.nextMeeting.time }}</p>
              <p class="mb-0 text-secondary">{{ myData.nextMeeting.title }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card shadow-sm border-0 border-start border-4 border-warning h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h6 class="card-subtitle text-muted fw-bold">我的消息</h6>
              <span class="badge bg-warning text-dark rounded-pill">{{ myData.messageCount }}</span>
            </div>
            <div class="message-preview small">
              <p v-if="myData.lastMessage" class="mb-0 italic text-muted">
                <i class="bi bi-chat-left-text me-1"></i> "{{ myData.lastMessage }}"
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

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

      <div v-if="toResultButtonShow" class="text-center mt-4">
        <button @click="generateMindMap" class="btn btn-outline-success px-5 py-2 rounded-pill"
                :disabled="isMindMapLoading">
          <span v-if="isMindMapLoading" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-diagram-3 me-2"></i>
          生成思维导图
        </button>
        &nbsp;&nbsp;&nbsp;&nbsp;
        <button @click="toResult" class="btn btn-outline-primary px-5 py-2 rounded-pill">
          <i class="bi bi-arrow-right me-2"></i>
          前往结果页面
        </button>
      </div>

      <div v-if="showMindMapModal" class="modal-backdrop fade show"></div>
      <div class="modal fade show" v-if="showMindMapModal" style="display: block;" tabindex="-1">
        <div class="modal-dialog modal-xl modal-dialog-centered">
          <div class="modal-content shadow-lg" style="height: 85vh;">
            <div class="modal-header bg-success text-white">
              <h5 class="modal-title"><i class="bi bi-diagram-3 me-2"></i>会议思维导图 (Mermaid)</h5>
              <button type="button" class="btn-close btn-close-white" @click="showMindMapModal = false"></button>
            </div>
            <div class="modal-body bg-white d-flex flex-column overflow-hidden">
              <div v-if="isMindMapLoading && !mindMapData" class="text-center my-auto">
                <div class="spinner-border text-success mb-3" role="status"></div>
                <p>正在接收 Mermaid 数据并绘制...</p>
              </div>

              <div
                  ref="mermaidContainer"
                  class="mermaid-viewer flex-grow-1 overflow-auto d-flex justify-content-center align-items-start p-3"
                  v-show="mindMapData"
              >
              </div>

              <details class="mt-2" v-if="mindMapData">
                <summary class="small text-muted cursor-pointer">查看 Mermaid 源码</summary>
                <pre class="small bg-light p-2 mt-1"><code>{{ mindMapData }}</code></pre>
              </details>
            </div>
            <div class="modal-footer">
              <button class="btn btn-outline-primary" @click="downloadMindMap" :disabled="!mindMapData">
                <i class="bi bi-download me-1"></i> 导出源码 (.mmd)
              </button>
              <button class="btn btn-secondary" @click="showMindMapModal = false">关闭</button>
            </div>
          </div>
        </div>
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
const isFullScreen = ref(false);

onMounted(() => {
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') isFullScreen.value = false;
  });

  meetingText.value = dummyMeeting;
  if (conversation.messages.length > 0 && conversation.question.length > 0) {
    messages.value = conversation.messages;
    toResultButtonShow.value = true;
    userQuery.value = conversation.question;
    if (conversation.meeting.length === 0) {
      meetingText.value = dummyMeeting;
    }
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
    conversation.meeting = meetingText.value;
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
  conversation.question = currentQuery;

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

// 1. 定义新的 ref
const fullChatContainer = ref(null);


// 2. 修改后的统一滚动监听
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

const toResult = async () => {
  conversation.messages = messages.value;
  await router.push('/result');
}

import mermaid from 'mermaid';

// 初始化 mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'forest', // 可选：default, forest, dark, neutral
  securityLevel: 'loose',
});

const showMindMapModal = ref(false);
const isMindMapLoading = ref(false);
const mindMapData = ref("");
const mermaidContainer = ref(null);
const mindMapUrl = 'http://localhost:5000/api/mindmap';

// 渲染 Mermaid 图形的方法
const renderMermaid = async () => {
  if (!mindMapData.value || !mermaidContainer.value) return;

  try {
    const {svg} = await mermaid.render(
        'mermaid-svg-' + Date.now(),
        mindMapData.value
    );
    mermaidContainer.value.innerHTML = svg;
  } catch (e) {
    // 渲染失败通常是因为 SSE 流还没传完，导致语法不完整，可以忽略中间报错
    console.warn("Mermaid 渲染中...");
  }
};

const generateMindMap = async () => {
  const finalAnswerMsg = [...messages.value].reverse().find(m => m.type === 'Final Answer');
  if (!finalAnswerMsg) return alert("未发现分析结果");

  showMindMapModal.value = true;
  isMindMapLoading.value = true;
  mindMapData.value = "";

  const token = localStorage.getItem('token');
  let headers = {
    'Content-Type': 'application/json',
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const ctrl = new AbortController();
  let timer;

  try {
    await fetchEventSource(mindMapUrl, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({conclusion: finalAnswerMsg.text}),
      openWhenHidden: true,
      signal: ctrl.signal,

      onopen: async (response) => {
        if (!response.ok) {
          error.value = `请求错误: ${response.statusText}`;

          if (response.status === 401) {
            await router.push('/login');
          }
        } else {
          timer = setInterval(() => {
            renderMermaid();
          }, 500);
        }
      },

      onmessage: (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'stream') {
          mindMapData.value += data.content;
        } else if (data.type === 'done') {
          isMindMapLoading.value = false;
          renderMermaid();
          ctrl.abort();
        }
      },

      onclose: () => {
        isMindMapLoading.value = false;
        clearInterval(timer);
        console.log("连接正常关闭");
      },

      onerror: (err) => {
        console.error("SSE 异常:", err);
        error.value = '连接中断，请检查后端服务。';
        isMindMapLoading.value = false;
        ctrl.abort();
        clearInterval(timer);
        throw err;
      }
    });
  } catch (err) {
    isMindMapLoading.value = false;
  }
};

const downloadMindMap = () => {
  const blob = new Blob([mindMapData.value], {type: 'text/plain'});
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `mindmap.mmd`;
  a.click();
};

// 新增：“我的”模块模拟数据
const myData = ref({
  todoCount: 5,
  todos: [
    { id: 1, title: '整理产品需求文档' },
    { id: 2, title: '发送周报邮件' },
    { id: 3, title: '确认下午3点的Demo' }
  ],
  nextMeeting: {
    time: '今天 15:00 - 16:30',
    title: 'Q1 季度总结与规划会议'
  },
  messageCount: 3,
  lastMessage: '张三：会议纪要已经上传，请查收。'
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

/* 按钮动画 */
.btn-outline-success:hover {
  transform: translateY(-2px);
  transition: all 0.2s;
}

/* 确保源码查看器有手型 */
summary {
  cursor: pointer;
  outline: none;
}

/* 渲染区域 */
.mermaid-viewer {
  background-image: radial-gradient(#d1d1d1 1px, transparent 1px);
  background-size: 20px 20px; /* 背景网格感 */
  border-radius: 8px;
}

/* 调整生成的 SVG 大小 */
:deep(.mermaid-viewer svg) {
  max-width: 100%;
  height: auto;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}
</style>