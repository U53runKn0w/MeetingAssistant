<template>
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
</template>

<script setup>
import {dummyMeeting} from "@/js/etc.js";
import {ref} from "vue";
import {storeToRefs} from "pinia";
import {useMeeting} from "@/store/meeting.js";

const meeting = useMeeting();
const {text: meetingText} = storeToRefs(meeting);
const isUploading = ref(false);
const error = ref(null);


const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  isUploading.value = true;
  error.value = null;

  const formData = new FormData();
  formData.append('file', file);

  try {
    // const response = await axios.post('http://localhost:5000/api/transcript', formData);
    // meetingText.value = response.data.text;

    await new Promise(resolve => setTimeout(resolve, 2000));
    meetingText.value = dummyMeeting;
  } catch (err) {
    error.value = "文件转录失败，请检查后端接口。";
  } finally {
    isUploading.value = false;
    event.target.value = ''; // 重置 file input
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

/* 优化代码块在全屏下的显示 */
.modal-body pre {
  background: #2d2d2d;
  color: #ccc;
  padding: 15px;
}

/* 确保源码查看器有手型 */
summary {
  cursor: pointer;
  outline: none;
}

/* 调整生成的 SVG 大小 */
:deep(.mermaid-viewer svg) {
  max-width: 100%;
  height: auto;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}
</style>