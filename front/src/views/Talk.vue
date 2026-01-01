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

                <div v-else-if="msg.type === 'observation'" class="alert alert-secondary py-2 mt-2">
                  <div class="fw-bold small mb-1">工具返回结果:</div>
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
    </div>
  </div>
</template>

<script setup>
import {ref, nextTick, watch} from 'vue';
import {parseReActContent} from "@/js/util.js";

// 状态管理
const meetingText = ref('');
const userQuery = ref('');
const isLoading = ref(false);
const error = ref(null);
const messages = ref([]);
const chatContainer = ref(null);
const isUploading = ref(false);

// 音频文件处理逻辑
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
    meetingText.value = `会议主题：智慧园区项目二期进度评审会
会议时间：2025年12月29日（星期一）14:30 - 15:45
会议地点：总公司第三会议室
参会人员：王总（项目经理）、李工程师（后端开发）、张设计师（UI/UX）、赵专员（测试）、刘经理（市场部）
会议内容记录：
王总：“好，大家都到齐了，我们开始吧。今天主要是同步一下项目二期的进度，看看有没有什么风险。先从李工这边开始吧，后端开发进展怎么样？”
李工程师：“王总，各位同事。我这边主要负责用户权限管理和数据看板两个模块。权限管理的接口开发已经完成了90%，预计本周三可以提测。但数据看板部分遇到个问题，因为需要对接外部API，对方服务器的响应速度不太稳定，可能会影响数据拉取的效率，这个风险需要提前知会大家。”
王总：“嗯，这是个问题。张设计，你那边呢？前端界面和用户体验方案确定了吗？”
张设计师：“UI稿已经全部完成了，和李工对接后就可以进入开发。不过关于主色调，市场部之前反馈说希望更活泼一些，我们做了两版方案，一版是沉稳的蓝色系，另一版是更有活力的橙色系，想听听刘经理的最终意见。”
刘经理：“太好了，感谢张设计。我们市场部内部讨论后，还是倾向于橙色系，感觉更符合我们想传递的创新形象。当然，最终定稿还是需要王总您这边拍板。”
王总：“可以，那就按市场部的意见，定橙色系方案。赵专员，测试这边有什么要说的吗？”
赵专员：“我一期功能的回归测试本周内能完成。关于二期的测试，我建议等李工的第一个模块提测后，我们先进行一次小范围的冒烟测试，确保基础功能稳定，这样后续集成测试会更顺畅。”
王总：“这个提议很好，就按你说的安排。好，我们总结一下今天的讨论和接下来的安排……”`;
  } catch (err) {
    error.value = "文件转录失败，请检查后端接口。";
  } finally {
    isUploading.value = false;
    event.target.value = ''; // 重置 file input
  }
};

const sendMessage = () => {
  if (!userQuery.value || isLoading.value) return;

  const url = `http://localhost:5000/api/chat?meeting=${encodeURIComponent(meetingText.value)}&query=${encodeURIComponent(userQuery.value)}`;

  const eventSource = new EventSource(url);
  messages.value = [];
  isLoading.value = true;
  userQuery.value = ''; // 清空问题输入框

  let rawAgentBuffer = "";
  let agentStartIndex = -1;

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch (data.type) {
      case 'observation':
        messages.value.push({type: 'observation', text: data.content});
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
        eventSource.close();
        break;
    }
  };

  eventSource.onerror = (err) => {
    console.error("SSE 异常:", err);
    error.value = '连接中断，请检查后端服务是否开启。';
    eventSource.close();
    isLoading.value = false;
  }
}

// 自动滚动聊天区域
watch(messages, () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
}, {deep: true});
</script>

<style scoped>
.chat-box {
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  max-height: 600px;
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