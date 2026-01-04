<template>
  <div class="d-flex min-vh-100">
    <Sidebar />

    <div class="flex-grow-1 overflow-auto">
      <div class="container mt-5 mb-5">
        <header class="text-center mb-5">
          <h1 class="display-5 fw-bold text-primary">会议助手</h1>
          <p class="lead text-muted">通过智能分析和组织，轻松简化您的会议记录</p>
        </header>

        <Mine></Mine>

        <div class="row g-4">
          <MeetingInput></MeetingInput>
          <ChatBox></ChatBox>
          <ChatButtons></ChatButtons>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Mine from "@/components/Mine.vue";
import MeetingInput from "@/components/MeetingInput.vue";
import ChatBox from "@/components/ChatBox.vue";
import ChatButtons from "@/components/ChatButtons.vue";
import Sidebar from "@/components/Sidebar.vue";
</script>

<style scoped>
body {
  margin: 0;
  //background-color: #ffffff;
}
</style>