<template>
  <div class="preference-generator d-flex flex-column h-100">
    <div class="d-flex justify-content-between align-items-center mb-2 px-1">
      <span class="badge" :class="isGenerating ? 'bg-primary-soft text-primary' : 'bg-light text-muted'">
        <i v-if="isGenerating" class="spinner-border spinner-border-sm me-1"></i>
        {{ isGenerating ? '正在生成偏好...' : '智能助手已就绪' }}
      </span>
      <button v-if="messages.length > 0" class="btn btn-sm btn-link text-decoration-none p-0" @click="clearAll">
        清空
      </button>
    </div>

    <div class="display-container flex-grow-1 overflow-auto mb-3 border rounded bg-light p-2" ref="scrollContainer">
      <div v-if="messages.length === 0"
           class="h-100 d-flex flex-column justify-content-center align-items-center text-muted opacity-50">
        <i class="bi bi-magic display-6 mb-2"></i>
        <p class="small">描述您的偏好，AI 将为您生成配置</p>
      </div>

      <div v-for="(msg, i) in messages" :key="i" class="mb-2">
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
    </div>

    <div class="input-area border-top pt-3">
      <div class="input-group">
        <textarea
            v-model="userQuery"
            class="form-control"
            rows="2"
            placeholder="例如：我喜欢暗黑模式，字体要大一些..."
            :disabled="isGenerating"
            @keydown.enter.ctrl="generatePreference"
        ></textarea>
        <button
            class="btn btn-primary d-flex flex-column justify-content-center align-items-center px-3"
            :disabled="isGenerating || !userQuery"
            @click="generatePreference"
        >
          <i v-if="!isGenerating" class="bi bi-stars mb-1"></i>
          <span v-else class="spinner-border spinner-border-sm mb-1"></span>
          <span>{{ isGenerating ? '生成中' : '生成' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, watch, nextTick} from 'vue';
import {fetchEventSource} from "@microsoft/fetch-event-source";
import {createHeaders, parseReActContent} from "@/js/util.js";
import router from "@/router/index.js";
import {useMessageStore} from "@/store/error.js";

const apiURL = 'http://localhost:5000/api/preference'; // 您的SSE接口

const userQuery = ref('');
const messages = ref([]);
const isGenerating = ref(false);
const scrollContainer = ref(null);
const messageStore = useMessageStore();

const clearAll = () => {
  messages.value = [];
  userQuery.value = '';
};

const generatePreference = async () => {
  if (!userQuery.value || isGenerating.value) return;

  const currentQuery = userQuery.value;
  messages.value = [];
  isGenerating.value = true;

  let rawBuffer = "";
  let agentIndex = -1;
  const ctrl = new AbortController();

  try {
    await fetchEventSource(apiURL, {
      method: 'POST',
      headers: createHeaders(),
      body: JSON.stringify({
        query: currentQuery
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
          case 'observation':
            let content = data.content
            content = content.substring(content.indexOf(':') + 1).trim();
            messages.value.push({type: 'Observation', text: content});
            rawBuffer = "";
            agentIndex = -1;
            break;

          case 'stream':
            const chunk = data.content;
            rawBuffer += chunk;
            const parsedSegments = parseReActContent(rawBuffer);

            if (agentIndex === -1) {
              agentIndex = messages.value.length;
              messages.value.push(...parsedSegments);
            } else {
              messages.value.splice(agentIndex, messages.value.length - agentIndex, ...parsedSegments);
            }
            break;

          case 'done':
            isGenerating.value = false;
            ctrl.abort();
            break;
        }
      },

      onclose: () => {
        isGenerating.value = false;
        console.log("连接正常关闭");
      },

      onerror: (err) => {
        console.error("SSE 异常:", err);
        messageStore.setNetworkError('failed');
        messageStore.setInfo('提示：生成偏好时发生错误，请稍后重试');
        isGenerating.value = false;
        ctrl.abort();
        throw err;
      }
    });
  } catch (err) {
    isGenerating.value = false;
  }
};

// 自动滚动到底部
watch(messages, () => {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
    }
  });
}, {deep: true});
</script>

<style scoped>
.preference-generator {
  min-height: 450px; /* 适合模态框的高度 */
  max-height: 80vh;
}

.display-container {
  background-image: radial-gradient(#dee2e6 0.5px, transparent 0.5px);
  background-size: 10px 10px; /* 细微的点阵背景提升质感 */
}

.thought-bubble summary {
  cursor: pointer;
  list-style: none;
  outline: none;
  transition: color 0.2s;
}

.thought-bubble summary:hover {
  color: #0dcaf0 !important;
}

.result-content {
  line-height: 1.5;
  font-size: 0.95rem;
}

.bg-primary-soft {
  background-color: rgba(13, 110, 253, 0.1);
}

.italic {
  font-style: italic;
}

/* 隐藏 details 的默认箭头 */
summary::-webkit-details-marker {
  display: none;
}
</style>