<template>
  <div class="resume-editor-container">
    <!-- 双栏布局 -->
    <div class="editor-column">
      <!-- 基本信息 -->
      <a-card title="基本信息" size="big" class="section-card">
        <a-form :model="resumeData" layout="vertical">
          <div class="basic-info-grid">
            <a-form-item label="姓名" class="grid-item">
              <a-input v-model:value="resumeData.name" placeholder="请输入姓名" />
            </a-form-item>
            <a-form-item label="年龄" class="grid-item">
              <a-input-number v-model:value="resumeData.age" :min="16" :max="70" />
            </a-form-item>
            <a-form-item label="性别" class="grid-item">
              <a-select v-model:value="resumeData.gender" placeholder="请选择">
                <a-select-option value="male">男</a-select-option>
                <a-select-option value="female">女</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="手机号" class="grid-item">
              <a-input v-model:value="resumeData.phone" placeholder="手机/邮箱" />
            </a-form-item>
            <a-form-item label="意向岗位" class="grid-item">
              <div v-if="props.job">
                <span>{{ props.job }}</span>
              </div>
              <div v-else>
                <a-cascader :options="cascaderOptions" placeholder="请选择意向岗位" :display-render="labelRender" />
              </div>
            </a-form-item>
          </div>
          <a-form-item label="照片上传">
            <a-upload v-model:file-list="fileList" list-type="picture-card" :before-upload="beforeUpload"
              @preview="handlePreview">
              <div v-if="fileList.length < 1">
                <plus-outlined />
                <div style="margin-top: 8px">上传照片</div>
              </div>
            </a-upload>
          </a-form-item>
        </a-form>
      </a-card>

      <!-- 学历背景 -->
      <a-card title="学历背景" size="big" class="section-card">
        <a-form-item v-for="(edu, index) in resumeData.education" :key="index">
          <div class="edu-item">
            <a-input v-model:value="edu.school" placeholder="学校名称" style="width: 40%" />
            <a-input v-model:value="edu.major" placeholder="专业" style="width: 30%; margin: 0 8px" />
            <a-input-number v-model:value="edu.gpa" :min="0" :max="4" :step="0.1" placeholder="GPA" />
            <a-button type="link" danger @click="removeEdu(index)" style="margin-left: 8px">
              <delete-outlined />
            </a-button>
          </div>
        </a-form-item>
        <a-button type="dashed" @click="addEdu">
          <plus-outlined /> 添加学历
        </a-button>
      </a-card>

      <!-- 个人成果 -->
      <a-card title="个人成果" size="big" class="section-card">
        <a-tabs>
          <a-tab-pane key="awards" tab="获奖情况">
            <draggable v-model="resumeData.awards" item-key="id">
              <template #item="{ element, index }">
                <div class="achievement-item">
                  <a-input v-model:value="element.text" placeholder="例: 2023年全国大学生数学竞赛一等奖" />
                  <a-button type="link" danger @click="removeAward(index)">
                    <delete-outlined />
                  </a-button>
                </div>
              </template>
            </draggable>
            <a-button type="dashed" @click="addAward">
              <plus-outlined /> 添加获奖
            </a-button>
          </a-tab-pane>
          <a-tab-pane key="research" tab="科研成果">
            <draggable v-model="resumeData.research" item-key="id">
              <template #item="{ element, index }">
                <div class="achievement-item">
                  <a-input v-model:value="element.text" placeholder="例: 发表SCI论文《...》于《Nature》期刊" />
                  <a-button type="link" danger @click="removeResearch(index)">
                    <delete-outlined />
                  </a-button>
                </div>
              </template>
            </draggable>
            <a-button type="dashed" @click="addResearch">
              <plus-outlined /> 添加成果
            </a-button>
          </a-tab-pane>
        </a-tabs>
      </a-card>

      <!-- 个人经历 -->
      <a-card title="个人经历" size="big" class="section-card">
        <editor-content :editor="experienceEditor" class="editor-content" />
      </a-card>

      <!-- 自我介绍 -->
      <a-card title="自我介绍/职业期望" size="big" class="section-card">
        <editor-content :editor="introductionEditor" class="editor-content" />
      </a-card>
    </div>

    <!-- 预览区 -->
    <div class="preview-column" id="preview-column">
      <table class="resume-table">
        <tbody>
          <!-- 基本信息 -->
          <tr>
            <td class="label">姓名</td>
            <td colspan="2">{{ resumeData.name || '' }}</td>
            <td class="label">性别</td>
            <td>{{ genderMap[resumeData.gender] || '' }}</td>
            <td class="photo-cell" rowspan="3" colspan="5">
              <img v-if="fileList.length > 0" :src="fileList[0].thumbUrl" alt="个人照片" />
              <div v-else>个人照片</div>
            </td>
          </tr>
          <tr>
            <td class="label" colspan="1">电话</td>
            <td colspan="2">{{ resumeData.phone || '' }}</td>
            <td class="label">年龄</td>
            <td>{{ resumeData.age ? resumeData.age + '岁' : '' }}</td>
          </tr>
          <tr>
            <td class="label">意向岗位</td>
            <td colspan="4">{{ resumeData.job || '' }}</td>
          </tr>

          <!-- 教育背景 -->
          <tr>
            <td colspan="10" class="section-title">教育背景</td>
          </tr>
          <tr v-for="(edu, index) in resumeData.education" :key="'edu' + index">
            <td class="label">学校</td>
            <td colspan="2">{{ edu.school || '学校名称' }}</td>
            <td class="label">专业</td>
            <td colspan="2">{{ edu.major || '专业' }}</td>
            <td class="label" colspan="2">GPA</td>
            <td colspan="2">{{ edu.gpa }}</td>
          </tr>

          <!-- 获奖情况和科研成果 -->
          <tr>
            <td colspan="10" class="section-title">个人成果</td>
          </tr>
          <tr>
            <td class="label" colspan="1">获奖情况</td>
            <td colspan="9">
              <ul>
                <li v-for="(award, index) in resumeData.awards" :key="'award' + index">
                  {{ award.text || '获奖内容' }}
                </li>
              </ul>
            </td>
          </tr>
          <tr>
            <td class="label" colspan="1">科研成果</td>
            <td colspan="9">
              <ul>
                <li v-for="(research, index) in resumeData.research" :key="'research' + index">
                  {{ research.text || '科研成果' }}
                </li>
              </ul>
            </td>
          </tr>

          <!-- 个人经历 -->
          <tr>
            <td colspan="10" class="section-title">个人经历</td>
          </tr>
          <tr>
            <td colspan="10">
              <div class="content-text" v-html="experienceHtml"></div>
            </td>
          </tr>

          <!-- 自我介绍 -->
          <tr>
            <td colspan="10" class="section-title">自我介绍</td>
          </tr>
          <tr>
            <td colspan="10">
              <div class="content-text" v-html="introductionHtml"></div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 操作按钮 -->
    <div class="editor-actions">
      <!-- <n-button @click="exportDOCX">
        <file-word-outlined /> 导出Word
      </n-button>
      <n-button @click="exportPDF">
        <file-pdf-outlined /> 导出PDF
      </n-button> -->
      <n-button type="primary" @click="avisible = true;" :disabled="spinning">
        <save-outlined /> 保存
      </n-button>
      <n-button type="error" @click="exits">
        取消
      </n-button>
    </div>

    <a-modal v-model:open="avisible" title="请输入文件名（不带后缀）">
      <a-spin :spinning="spinning" tip="请稍等">
        <a-input v-model:value="file_name" placeholder="file_name" />
      </a-spin>
      <template #footer>
        <n-button @click="ahandleCancel">
          取消
        </n-button>
        <n-button type="warning" @click="ahandleOk" :disabled="spinning" style="margin-left: 8px;">
          确认
        </n-button>
      </template>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, computed } from 'vue';
import { Editor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import { PlusOutlined, DeleteOutlined, FilePdfOutlined, FileWordOutlined, SaveOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import draggable from 'vuedraggable';
import { NButton } from 'naive-ui';
const props = defineProps({
  job: String
})
const emit = defineEmits(['exits', 'submit'])
const exits = () => {
  emit('exits')
}
import { jobTypeOptions, jobsOptions } from '../utils/score.js'

// 转换成 Cascader 使用的格式
const cascaderOptions = jobTypeOptions.map(group => ({
  value: group.value,
  label: group.label,
  children: jobsOptions[group.value]
}))
const labelRender = (labels) => {
  return labels.labels[labels.labels.length - 1]; // 只显示最后一级
};
//console.log('cascaderOptions', cascaderOptions)
// 表单数据
const resumeData = reactive({
  name: '',
  age: null,
  gender: undefined,
  phone: '',
  job: props.job,
  education: [
    { school: '', major: '', gpa: null }
  ],
  awards: [],
  research: []
});

const genderMap = {
  male: '男',
  female: '女',
};

// 照片上传
const fileList = ref([]);
const beforeUpload = file => {
  fileList.value = [file];
  return false;
};

// 学历管理
const addEdu = () => {
  resumeData.education.push({ school: '', major: '', gpa: null });
};
const removeEdu = index => {
  resumeData.education.splice(index, 1);
};

// 成果管理
const addAward = () => {
  resumeData.awards.push({ id: Date.now(), text: '' });
};
const removeAward = index => {
  resumeData.awards.splice(index, 1);
};
const addResearch = () => {
  resumeData.research.push({ id: Date.now(), text: '' });
};
const removeResearch = index => {
  resumeData.research.splice(index, 1);
};

// 编辑器实例
const experienceEditor = ref(null);
const experienceHtml = ref('');
const introductionEditor = ref(null);
const introductionHtml = ref('');

onMounted(() => {
  experienceEditor.value = new Editor({
    content: '<p>请详细描述您的工作/项目经历...</p>',
    extensions: [StarterKit],
    onUpdate: ({ editor }) => {
      experienceHtml.value = editor.getHTML();
    }
  });

  introductionEditor.value = new Editor({
    content: '<p>请描述您的优点、兴趣爱好、职业目标等...</p>',
    extensions: [StarterKit],
    onUpdate: ({ editor }) => {
      introductionHtml.value = editor.getHTML();
    }
  });
});

onBeforeUnmount(() => {
  experienceEditor.value?.destroy();
  introductionEditor.value?.destroy();
});

import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

const exportPDF = () => {
  const resumeContent = document.querySelector('.preview-column')
  html2canvas(resumeContent, {
    scale: 2,
    useCORS: true
  }).then(canvas => {
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    const pageWidth = 210 // A4 width in mm
    const pageHeight = 297 // A4 height in mm
    const imgWidth = pageWidth
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    let heightLeft = imgHeight
    let position = 0

    // 添加第一页
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight

    // 添加更多页
    while (heightLeft > 0) {
      position -= pageHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }

    pdf.save('resume.pdf')
  })
}

const exportDOCX = async () => {
  console.log('jjj')
};

// 计算纯文本内容
const experienceText = computed(() => {
  return resumeData.experience ? resumeData.experience.replace(/<[^>]*>/g, '\n') : '';
});

const introductionText = computed(() => {
  return resumeData.introduction ? resumeData.introduction.replace(/<[^>]*>/g, '\n') : '';
});
const avisible = ref(false);
const file_name = ref('my_resume')
const ahandleCancel = () => {
  avisible.value = false;
  spinning.value = false;
  file_name.value = 'my_resume'
};
const spinning = ref(false);
const ahandleOk = () => {

  if (!file_name.value.trim()) {
    message.warning("文件名不能为空！");
    return;
  }
  spinning.value = true;
  emit('submit', {
    ...resumeData,
    experience: experienceHtml.value,
    introduction: introductionHtml.value
  }, file_name.value, () => {
    // 回调内容，例如关闭 modal 或显示提示
    spinning.value = false;
    avisible.value = false;
  });
};

</script>

<style lang="scss" scoped>
.resume-editor-container {
  position: fixed;
  transform: translate(-50%, -50%);
  display: flex;
  margin: 0 auto;
  gap: 24px;
  padding: 24px;

  margin: 0 auto;
  width: 90vw;
  height: 90vh;
  max-width: 1200px;
  max-height: 800px;
  min-width: 500px;
  min-height: 300px;
  background-color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  overflow: hidden;

  /* 编辑器列 */
  .editor-column {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    padding-right: 12px;

    /* 卡片样式 */
    .section-card {
      margin-bottom: 16px;
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);

      /* 基本信息网格 */
      .basic-info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin-bottom: 12px;

        .grid-item {
          margin-bottom: 0;
        }
      }

      /* 教育经历项 */
      .edu-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        :deep(.ant-input-number) {
          width: 80px;
        }
      }

      /* 成果项 */
      .achievement-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
      }

      /* 编辑器内容区 */
      .editor-content {
        min-height: 200px;
        border: 1px solid #d9d9d9;
        border-radius: 4px;
        padding: 12px;
        background: #fff;
      }

      /* 添加按钮 */
      .ant-btn-dashed {
        width: 100%;
        margin-top: 8px;
      }
    }
  }

  /* 预览列 */
  .preview-column {
    flex: 1;
    min-width: 0;
    background: #f9f9f9;
    border-radius: 8px;
    overflow-y: auto;
    padding: 20px;

    .resume-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
      table-layout: fixed;
    }

    .resume-table td {
      border: 1px solid #ccc;
      padding: 8px;
      word-break: break-word;
      vertical-align: top;
    }

    .resume-table .label {
      font-weight: bold;
      background-color: #f5f5f5;
      width: 80px;
    }

    .photo-cell {
      text-align: center;
      vertical-align: middle;
      width: 120px;
    }

    .photo-cell img {
      width: 100px;
      height: 120px;
      object-fit: cover;
      border: 1px solid #ddd;
    }

    .resume-table .section-title {
      font-size: 16px;
      font-weight: bold;
      background-color: #e8e8e8;
      text-align: left;
      padding: 10px;
    }

    ul {
      margin: 0;
      padding-left: 16px;
    }

    .content-text {
      white-space: pre-wrap;
      word-break: break-word;
    }
  }

  /* 操作按钮 */
  .editor-actions {
    position: fixed;
    right: 32px;
    bottom: 32px;
    display: flex;
    gap: 12px;
    z-index: 2000;

    button {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      transition: all 0.3s;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
      }
    }
  }
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f2f3f3;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #f5ed09;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #e2cb03;
}
</style>