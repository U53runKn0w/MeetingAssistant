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

  <MindMapModal
      v-model:visible="showMindMapModal"
      :is-loading="isMindMapLoading"
      :mind-map-data="mindMapData"
      :settings="mindmapSettings"
      @close="handleModalClose"
      @stop-generation="stopGeneration"
      @update:settings="handleSettingsUpdate"
      ref="mindMapModalRef"
  />
</template>

<script setup>
import {onMounted, ref} from "vue";
import {storeToRefs} from "pinia";
import {useChatStore} from "@/store/chat.js";
import {fetchEventSource} from "@microsoft/fetch-event-source";
import {createHeaders} from "@/js/util.js";
import {useMessageStore} from "@/store/error.js";
import MindMapModal from "./MindMapModal.vue";

const mindMapUrl = 'http://localhost:5000/api/mindmap';
const showMindMapModal = ref(false);
const isMindMapLoading = ref(false);
const mindMapData = ref("");
const chat = useChatStore();
const {buttonsShow} = storeToRefs(chat);
const messageStore = useMessageStore();
const mindMapModalRef = ref(null);

const emit = defineEmits(['showResult']);
const abortController = ref(null);
const renderTimer = ref(null);

const mindmapSettings = ref({
  theme: 'forest',
  renderInterval: 500,
  autoRender: true,
  showSourceCode: false
});

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
};

defineExpose({
  loadSettings
});

const handleModalClose = () => {
  showMindMapModal.value = false;
};

const handleSettingsUpdate = (newSettings) => {
  mindmapSettings.value = {...newSettings};
};

const triggerRender = () => {
  if (mindMapModalRef.value) {
    mindMapModalRef.value.renderMermaid();
  }
};

onMounted(() => {
  loadSettings();
  if (chat.messages.length > 0 && chat.question.length > 0) {
    buttonsShow.value = true;
  }

  window.addEventListener('storage', (e) => {
    if (e.key === 'mindmapSettings') {
      loadSettings();
    }
  });
});

const toResult = async () => {
  emit('showResult');
};

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
};

const generateMindMap = async () => {
  const finalAnswerMsg = [...chat.messages].reverse().find(m => m.type === 'Final Answer');
  if (!finalAnswerMsg) return alert("未发现分析结果");

  showMindMapModal.value = true;
  mindMapData.value = "";

  if (!isMindMapLoading.value) {
    isMindMapLoading.value = true;
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
            if (mindmapSettings.value.autoRender) {
              renderTimer.value = setInterval(() => {
                triggerRender();
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
            if (mindmapSettings.value.autoRender) {
              triggerRender();
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
  }
}
</script>

<style scoped>
.btn-outline-success:hover {
  transform: translateY(-2px);
  transition: all 0.2s;
}
</style>
