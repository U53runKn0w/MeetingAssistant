<template>
  <div v-if="visible" class="modal-backdrop fade show"></div>
  <div class="modal fade show" v-if="visible" style="display: block;" tabindex="-1">
    <div class="modal-dialog modal-xl modal-dialog-centered">
      <div class="modal-content shadow-lg" style="height: 85vh;">
        <div class="modal-header bg-success text-white">
          <h5 class="modal-title"><i class="bi bi-diagram-3 me-2"></i>会议思维导图 (Mermaid)</h5>
          <button type="button" class="btn-close btn-close-white" @click="handleClose"></button>
        </div>
        <div class="modal-body bg-white d-flex flex-column overflow-hidden position-relative">
          <div v-if="isLoading && !mindMapData" class="text-center my-auto">
            <div class="spinner-border text-success mb-3" role="status"></div>
            <p>正在接收 Mermaid 数据并绘制...</p>
          </div>

          <div
              ref="mermaidContainer"
              class="mermaid-viewer flex-grow-1 overflow-auto d-flex justify-content-center align-items-start p-3"
              v-show="mindMapData"
          >
          </div>

          <details class="mt-2" v-if="mindMapData" :open="settings.showSourceCode">
            <summary class="small text-muted cursor-pointer">查看 Mermaid 源码</summary>
            <pre class="small bg-light p-2 mt-1 source-code-container"><code>{{ mindMapData }}</code></pre>
          </details>

          <!-- 右下角设置区域 -->
          <div class="settings-corner">
            <button class="settings-toggle" @click="showSettings = true" title="思维导图设置">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                <path
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="modal-footer">
          <button v-if="isLoading" @click="handleStopGeneration" class="btn btn-outline-danger me-auto">
            <i class="bi bi-stop-circle me-1"></i> 停止生成
          </button>
          <button class="btn btn-outline-primary" @click="downloadMindMap" :disabled="!mindMapData">
            <i class="bi bi-download me-1"></i> 导出源码 (.mmd)
          </button>
          <button class="btn btn-secondary" @click="handleClose">关闭</button>
        </div>
      </div>
    </div>
  </div>

  <!-- 设置模态框 -->
  <MindMapSettings v-model:visible="showSettings" :settings="settings" @save="handleSaveSettings" />
</template>

<script setup>
import {ref, watch, nextTick} from "vue";
import mermaid from 'mermaid';
import MindMapSettings from './MindMapSettings.vue';
import {useMessageStore} from "@/store/error.js";

const props = defineProps({
  visible: Boolean,
  isLoading: Boolean,
  mindMapData: String,
  settings: Object
});

const emit = defineEmits(['close', 'stop-generation', 'update:settings']);

const mermaidContainer = ref(null);
const showSettings = ref(false);
const messageStore = useMessageStore();

const handleClose = () => {
  emit('close');
};

const handleStopGeneration = () => {
  emit('stop-generation');
};

const handleSaveSettings = (newSettings) => {
  emit('update:settings', newSettings);
  showSettings.value = false;
};

const downloadMindMap = () => {
  const blob = new Blob([props.mindMapData], {type: 'text/plain'});
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `mindmap.mmd`;
  a.click();
};

const renderMermaid = async () => {
  if (!props.mindMapData || !mermaidContainer.value) return;

  try {
    const {svg} = await mermaid.render(
        'mermaid-svg-' + Date.now(),
        props.mindMapData
    );
    mermaidContainer.value.innerHTML = svg;

    // 渲染完成后，移除 document.body 末尾的 Mermaid 错误元素
    setTimeout(() => {
      // 查找整个页面中 id 以 dmermaid-svg- 开头的元素
      const mermaidDivs = document.querySelectorAll('[id^="dmermaid-svg-"]');

      mermaidDivs.forEach(mermaidDiv => {
        // 检查内部 SVG 是否有错误标识
        const svgElement = mermaidDiv.querySelector('svg');
        if (svgElement && svgElement.getAttribute('aria-roledescription') === 'error') {
          // 是错误状态，移除整个元素
          mermaidDiv.remove();
        }
      });
    }, 0);
  } catch (e) {
    console.warn(e);
  }
};

const reinitializeMermaid = () => {
  mermaid.initialize({
    startOnLoad: false,
    theme: props.settings.theme,
    securityLevel: 'loose',
    suppressErrorRendering: true,
  });
};

watch(() => props.visible, (newVal) => {
  if (newVal && props.mindMapData) {
    nextTick(() => {
      renderMermaid();
    });
  }
});

watch(() => props.settings.theme, () => {
  reinitializeMermaid();
  if (props.mindMapData) {
    renderMermaid();
  }
});

watch(() => props.mindMapData, () => {
  if (props.mindMapData && mermaidContainer.value) {
    renderMermaid();
  }
});

defineExpose({
  renderMermaid
});
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
  background: rgba(0, 0, 0, 0.2);
}

.modal-body pre {
  background: #2d2d2d;
  color: #ccc;
  padding: 15px;
}

.modal-body {
  overflow-y: auto;
}

summary {
  cursor: pointer;
  outline: none;
}

.mermaid-viewer {
  background-image: radial-gradient(#d1d1d1 1px, transparent 1px);
  background-size: 20px 20px;
  border-radius: 8px;
}

:deep(.mermaid-viewer svg) {
  max-width: 100%;
  height: auto;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}

.source-code-container {
  max-height: 200px;
  overflow-y: auto;
}

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
