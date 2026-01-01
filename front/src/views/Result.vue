<template>
  <div class="container mt-5 mb-10">
    <header>
      <h1>Analysis Results</h1>
      <p class="subtitle">Intelligent breakdown of your meeting notes</p>
    </header>

    <div class="row row-cols-1 row-cols-md-2 g-4 mb-5">
      <div v-for="(result, key) in results" :key="key" class="col">
        <div class="card result-card">
          <div :class="['card-header', toolConfigs[key]?.class]">
            <h3>
              <i :class="['bi', toolConfigs[key]?.icon]"></i>
              {{ toolConfigs[key]?.name }}
            </h3>
          </div>
          <div class="card-body">
            <div class="result-content">{{ result }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="text-center">
      <button @click="goBack" class="btn btn-back">
        <i class="bi bi-arrow-left"></i>
        Back to Input Page
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router'; // 假设你使用 vue-router

const router = useRouter();

// 配置信息映射表
const toolConfigs = {
  extract_meeting_basic_info: {
    name: "Meeting Basic Info",
    icon: "bi-info-circle",
    class: "tool1"
  },
  parse_meeting_agenda_conclusion: {
    name: "Agenda & Conclusions",
    icon: "bi-list-check",
    class: "tool2"
  },
  generate_meeting_todo: {
    name: "Action Items",
    icon: "bi-calendar-check",
    class: "tool3"
  },
  mark_meeting_follow_up: {
    name: "Follow-up Items",
    icon: "bi-exclamation-triangle",
    class: "tool4"
  }
};

// 模拟接收到的结果数据（实际应从 API 获取或通过状态管理传参）
const results = ref({
  extract_meeting_basic_info: "Date: 2023-10-25\nLocation: Room 302\nParticipants: Alice, Bob",
  parse_meeting_agenda_conclusion: "Discussed the Q4 roadmap and finalized the budget.",
  generate_meeting_todo: "1. Alice to update docs\n2. Bob to call client",
  mark_meeting_follow_up: "Check with the legal team on contract terms."
});

const goBack = () => {
  router.push('/');
};
</script>

<style scoped src="@/assets/results.css"></style>