<template>
  <div v-if="buttonsShow" class="text-center mt-4">
    <button @click="generateMindMap" class="btn btn-outline-success px-5 py-2 rounded-pill"
            :disabled="isMindMapLoading">
      <span v-if="isMindMapLoading" class="spinner-border spinner-border-sm me-2"></span>
      <i v-else class="bi bi-diagram-3 me-2"></i>
      生成思维导图
    </button>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <button @click="toResult" class="btn btn-outline-primary px-5 py-2 rounded-pill">
      <i class="bi bi-clipboard-data me-2"></i>
      查看分析结果
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
        <div class="modal-body bg-white d-flex flex-column overflow-hidden position-relative">
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

          <details class="mt-2" v-if="mindMapData" :open="mindmapSettings.showSourceCode">
            <summary class="small text-muted cursor-pointer">查看 Mermaid 源码</summary>
            <pre class="small bg-light p-2 mt-1 source-code-container"><code>{{ mindMapData }}</code></pre>
          </details>

          <!-- 右下角设置区域 -->
          <div class="settings-corner">
            <button class="settings-toggle" @click="showSettingsModal = true" title="思维导图设置">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                <path
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="modal-footer">
          <button v-if="isMindMapLoading" @click="stopGeneration" class="btn btn-outline-danger me-auto">
            <i class="bi bi-stop-circle me-1"></i> 停止生成
          </button>
          <button class="btn btn-outline-primary" @click="downloadMindMap" :disabled="!mindMapData">
            <i class="bi bi-download me-1"></i> 导出源码 (.mmd)
          </button>
          <button class="btn btn-secondary" @click="showMindMapModal = false">关闭</button>
        </div>
      </div>
    </div>
  </div>

  <!-- 设置模态框 -->
  <div v-if="showSettingsModal" class="modal-backdrop fade show"></div>
  <div class="modal fade show" v-if="showSettingsModal" style="display: block;" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content shadow-lg">
        <div class="modal-header">
          <h5 class="modal-title"><i class="bi bi-gear me-2"></i>思维导图设置</h5>
          <button type="button" class="btn-close" @click="showSettingsModal = false"></button>
        </div>
        <div class="modal-body">
          <div class="settings-form">
            <div class="form-group">
              <label class="form-label">主题样式</label>
              <select v-model="mindmapSettings.theme" class="form-input">
                <option value="default">默认</option>
                <option value="forest">森林</option>
                <option value="dark">暗色</option>
                <option value="neutral">中性</option>
              </select>
              <small class="form-hint">选择思维导图的配色主题</small>
            </div>

            <div class="form-group">
              <label class="form-label">渲染间隔（毫秒）</label>
              <input
                  type="number"
                  v-model.number="mindmapSettings.renderInterval"
                  class="form-input"
                  placeholder="请输入渲染间隔"
                  min="100"
                  step="100"
              />
              <small class="form-hint">思维导图刷新渲染的时间间隔</small>
            </div>

            <div class="form-group">
              <label class="form-label">显示设置</label>
              <div class="toggle-group">
                <label class="toggle-label">
                  <input type="checkbox" v-model="mindmapSettings.autoRender"/>
                  <span>自动渲染导图</span>
                </label>
                <label class="toggle-label">
                  <input type="checkbox" v-model="mindmapSettings.showSourceCode"/>
                  <span>显示源代码</span>
                </label>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showSettingsModal = false">取消</button>
          <button class="btn btn-primary" @click="saveSettings" :disabled="isSaving">
            <span v-if="isSaving" class="spinner-border spinner-border-sm me-1"></span>
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, ref, watch} from "vue";
import mermaid from 'mermaid';
import {storeToRefs} from "pinia";
import {useChatStore} from "@/store/chat.js";
import {fetchEventSource} from "@microsoft/fetch-event-source";
import {createHeaders} from "@/js/util.js";
import {useMessageStore} from "@/store/error.js";

const mindMapUrl = 'http://localhost:5000/api/mindmap';
const showMindMapModal = ref(false);
const isMindMapLoading = ref(false);
const mindMapData = ref("");
const mermaidContainer = ref(null);
const chat = useChatStore();
const {buttonsShow} = storeToRefs(chat);
const messageStore = useMessageStore();

// 定义 emit 事件
const emit = defineEmits(['showResult']);
const abortController = ref(null);
const renderTimer = ref(null);

// 设置模态框
const showSettingsModal = ref(false);
const isSaving = ref(false);

// 思维导图设置
const mindmapSettings = ref({
  theme: 'forest',
  renderInterval: 500,
  autoRender: true,
  showSourceCode: false
});

// 加载设置
const loadSettings = () => {
  const savedSettings = localStorage.getItem('mindmapSettings');
  if (savedSettings) {
    try {
      const parsed = JSON.parse(savedSettings);
      mindmapSettings.value = {...mindmapSettings.value, ...parsed};
    } catch (error) {
      console.error('加载思维导图设置失败:', error);
    }
  }
  reinitializeMermaid();
};

// 暴露 loadSettings 方法供父组件调用
defineExpose({
  loadSettings
});

// 重新初始化 Mermaid（应用主题设置）
const reinitializeMermaid = () => {
  mermaid.initialize({
    startOnLoad: false,
    theme: mindmapSettings.value.theme,
    securityLevel: 'loose',
    suppressErrorRendering: true,
  });
};

// 监听设置变化
watch(() => mindmapSettings.value.theme, () => {
  reinitializeMermaid();
  if (mindMapData.value && mermaidContainer.value) {
    renderMermaid();
  }
});

onMounted(() => {
  loadSettings();
  if (chat.messages.length > 0 && chat.question.length > 0) {
    buttonsShow.value = true;
  }
  
  // 监听 localStorage 变化（当 History 组件保存设置时）
  window.addEventListener('storage', (e) => {
    if (e.key === 'mindmapSettings') {
      loadSettings();
    }
  });
})

const toResult = async () => {
  // 触发自定义事件，让父组件打开结果模态框
  emit('showResult');
  await router.push('/result');
}

const stopGeneration = () => {
  if (abortController.value) {
    abortController.value.abort();
    abortController.value = null;
  }
  if (renderTimer.value) {
    clearInterval(renderTimer.value);
    renderTimer.value = null;
  }
  isMindMapLoading.value = false;
  messageStore.setError('已停止生成思维导图');
}


const renderMermaid = async () => {
  if (!mindMapData.value || !mermaidContainer.value) return;

  try {
    const {svg} = await mermaid.render(
        'mermaid-svg-' + Date.now(),
        mindMapData.value
    );
    mermaidContainer.value.innerHTML = svg;
  } catch (e) {
    console.warn(e);
  }
};

const generateMindMap = async () => {
  const finalAnswerMsg = [...chat.messages].reverse().find(m => m.type === 'Final Answer');
  if (!finalAnswerMsg) return alert("未发现分析结果");

  showMindMapModal.value = true;
  isMindMapLoading.value = true;
  mindMapData.value = "";

  const ctrl = new AbortController();
  abortController.value = ctrl;

  try {
    await fetchEventSource(mindMapUrl, {
      method: 'POST',
      headers: createHeaders(),
      body: JSON.stringify({conclusion: finalAnswerMsg.text}),
      openWhenHidden: true,
      signal: ctrl.signal,

      onopen: async (response) => {
        if (!response.ok) {
          messageStore.setError(`请求错误: ${response.statusText}`);

          if (response.status === 401) {
            await router.push('/login');
          }
        } else {
          // 根据设置决定是否自动渲染
          if (mindmapSettings.value.autoRender) {
            renderTimer.value = setInterval(() => {
              renderMermaid();
            }, mindmapSettings.value.renderInterval);
          }
        }
      },

      onmessage: (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'stream') {
          mindMapData.value += data.content;
        } else if (data.type === 'done') {
          isMindMapLoading.value = false;
          // 根据设置决定是否渲染
          if (mindmapSettings.value.autoRender) {
            renderMermaid();
          }
          if (renderTimer.value) {
            clearInterval(renderTimer.value);
            renderTimer.value = null;
          }
          ctrl.abort();
        }
      },

      onclose: () => {
        isMindMapLoading.value = false;
        if (renderTimer.value) {
          clearInterval(renderTimer.value);
          renderTimer.value = null;
        }
        console.log("连接正常关闭");
      },

      onerror: (err) => {
        console.error("SSE异常:", err);
        messageStore.setError('连接中断，请检查后端服务。');
        isMindMapLoading.value = false;
        abortController.value = null;
        if (renderTimer.value) {
          clearInterval(renderTimer.value);
          renderTimer.value = null;
        }
        ctrl.abort();
        throw err;
      }
    });
  } catch (err) {
    isMindMapLoading.value = false;
    abortController.value = null;
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

const saveSettings = async () => {
  isSaving.value = true;
  try {
    localStorage.setItem('mindmapSettings', JSON.stringify(mindmapSettings.value));
    messageStore.setSuccess('思维导图设置已保存');
    showSettingsModal.value = false;
    // 触发 storage 事件，让其他组件感知到设置变化
    window.dispatchEvent(new StorageEvent('storage', {
      key: 'mindmapSettings',
      newValue: JSON.stringify(mindmapSettings.value)
    }));
  } catch (error) {
    messageStore.setClientError('badRequest');
    console.error('保存设置失败:', error);
  } finally {
    isSaving.value = false;
  }
};
</script>

<style scoped>
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

/* 优化代码块在全屏下的显示 */
.modal-body pre {
  background: #2d2d2d;
  color: #ccc;
  padding: 15px;
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

/* 源码容器滚动条 */
.source-code-container {
  max-height: 200px;
  overflow-y: auto;
}

/* 设置表单样式 */
.settings-form {
  text-align: left;
  margin-top: 8px;
  max-height: 60vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.2s;
  outline: none;
}

.form-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-hint {
  display: block;
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 6px;
}

.toggle-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #1f2937;
  cursor: pointer;
  user-select: none;
  padding: 6px 0;
}

.toggle-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #3b82f6;
}

.toggle-label span {
  line-height: 1.5;
}

/* 右下角设置区域 */
.settings-corner {
  position: absolute;
  bottom: 16px;
  right: 16px;
  z-index: 10;
}

.settings-toggle {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  color: #495057;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.settings-toggle:hover {
  background: #fff;
  color: #3b82f6;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.settings-toggle:active {
  transform: scale(0.95);
}

</style>