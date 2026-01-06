<template>
  <div class="d-flex min-vh-100">
    <History ref="historyRef" @select-session="handleSelectSession" @new-session="handleNewSession" @settings-changed="handleSettingsChanged"/>

    <div class="flex-grow-1 overflow-auto">
      <div class="container mt-5 mb-5">
        <header class="text-center mb-5">
          <h1 class="display-5 fw-bold text-primary">会议助手</h1>
          <p class="lead text-muted">通过智能分析和组织，轻松简化您的会议记录</p>
        </header>

        <MyInfo></MyInfo>

        <div class="row g-4">
          <MeetingInput></MeetingInput>
          <ChatBox ref="chatBoxRef" @refresh-history="refreshHistory"></ChatBox>
          <ChatTools ref="chatToolsRef"></ChatTools>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue';
import MyInfo from "@/components/MyInfo.vue";
import MeetingInput from "@/components/MeetingInput.vue";
import ChatBox from "@/components/ChatBox.vue";
import ChatTools from "@/components/ChatTools.vue";
import History from "@/components/History.vue";

const historyRef = ref(null);
const chatBoxRef = ref(null);
const chatToolsRef = ref(null);

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
</script>

<style scoped></style>