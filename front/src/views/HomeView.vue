<template>
  <div class="d-flex min-vh-100">
    <History ref="historyRef"/>

    <div class="flex-grow-1 overflow-auto">
      <div class="container mt-5 mb-5">
        <header class="text-center mb-5">
          <h1 class="display-5 fw-bold text-primary">会议助手</h1>
          <p class="lead text-muted">通过智能分析和组织，轻松简化您的会议记录</p>
        </header>

        <MyInfo></MyInfo>

        <div class="row g-4">
          <MeetingInput></MeetingInput>
          <ChatBox @refresh-history="refreshHistory"></ChatBox>
          <ChatTools></ChatTools>
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

const refreshHistory = () => {
  if (historyRef.value) {
    historyRef.value.fetchHistory();
  }
};
</script>

<style scoped></style>