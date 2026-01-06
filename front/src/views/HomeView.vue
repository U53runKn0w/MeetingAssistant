<template>
  <div class="d-flex min-vh-100">
    <History ref="historyRef" @select-session="handleSelectSession" @new-session="handleNewSession" @settings-changed="handleSettingsChanged" @session-loaded="handleSessionLoaded"/>

    <div class="flex-grow-1 overflow-auto">
      <div class="container mt-5 mb-5">
        <header class="text-center mb-5">
          <h1 class="display-5 fw-bold text-primary">会议助手</h1>
          <p class="lead text-muted">通过智能分析和组织，轻松简化您的会议记录</p>
        </header>

        <MyInfo></MyInfo>

        <div class="row g-4">
          <MeetingInput ref="meetingInputRef"></MeetingInput>
          <ChatBox ref="chatBoxRef" @refresh-history="refreshHistory"></ChatBox>
          <ChatTools ref="chatToolsRef" @show-result="handleShowResult"></ChatTools>
        </div>
      </div>
    </div>

    <ResultModal ref="resultModalRef"></ResultModal>
  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted} from 'vue';
import MyInfo from "@/components/MyInfo.vue";
import MeetingInput from "@/components/MeetingInput.vue";
import ChatBox from "@/components/ChatBox.vue";
import ChatTools from "@/components/ChatTools.vue";
import History from "@/components/History.vue";
import ResultModal from "@/components/ResultModal.vue";

const historyRef = ref(null);
const chatBoxRef = ref(null);
const chatToolsRef = ref(null);
const meetingInputRef = ref(null);
const resultModalRef = ref(null);

const refreshHistory = () => {
  if (historyRef.value) {
    historyRef.value.fetchHistory();
  }
};

const handleSelectSession = () => {
  if (chatBoxRef.value) {
    chatBoxRef.value.stopGeneration();
  }
};

const handleSessionLoaded = () => {
  if (chatBoxRef.value) {
    // 等待 DOM 更新后滚动到底部
    setTimeout(() => {
      chatBoxRef.value.scrollToBottom();
    }, 100);
  }
};

const handleNewSession = () => {
  if (chatBoxRef.value) {
    chatBoxRef.value.newSession();
  }
};

const handleSettingsChanged = (newSettings) => {
  if (chatToolsRef.value) {
    chatToolsRef.value.loadSettings();
  }
};

const handleShowResult = () => {
  if (resultModalRef.value) {
    resultModalRef.value.openModal();
  }
};

// 处理会议纪要填入事件
const handleFillMeetingSummary = (event) => {
  const { summary } = event.detail;
  if (meetingInputRef.value && summary) {
    meetingInputRef.value.fillMeetingText(summary);
  }
};

// 组件挂载和卸载时添加/移除事件监听
onMounted(() => {
  window.addEventListener('fillMeetingSummary', handleFillMeetingSummary);
});

onUnmounted(() => {
  window.removeEventListener('fillMeetingSummary', handleFillMeetingSummary);
});
</script>

<style scoped></style>