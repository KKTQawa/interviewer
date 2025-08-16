<template>
  <!-- 用于显示模态框的时候判断鼠标点击是否有效 -->
  <div class="home" :style="{ 'pointer-events': isModalOpen || show_card || showResumeEditor ? 'none' : 'auto' }">
    <div class="viewarea">
      <interview ref="interviewRef" v-if="mode_0" @exit-interview="handleExitInterview"
        @finish-interview="finishInterview" @readingText="readingText" @handleChatText="handleChatText"
        @startRecord="startRecord" @stopRecord="handleStopRecord" @clearRecord="handleClearRecord" @uploadRecord="uploadAudioBlob" /> <!-- 监听子组件事件 -->


      <interviewRealTime ref="interviewRealTimeRef" v-else-if="mode_1" @exit-interview="handleExitInterview"
        @finish-interview="finishInterview" @readingText="readingText" @handleChatText="handleChatText"
        @startRecord="startRecord" @stopRecord="handleStopRecord" @handleImgChat="handleImgChat" />
      <!-- <img v-else src="../assets/preview1.png" alt="马到成功" style="width:100%;height:100%;" /> -->
      <div v-else-if="viewmode===1" style="width:100%;height:100%;position:absolute;">
        <HistoryView @toReport="toReport"/>
      </div>
      <div v-else-if="viewmode===2" style="width:100%;height:100%;position:absolute;">
        <ReportView @toHistory="toHistory"  :reportData="reportData"/>
      </div>
    </div>

    <div class="controlarea">
      <button v-if="!show_card && !(mode_0 || mode_1)" @click="show_card = true" class="btn1">
        开始面试
      </button>
      <div class="reader">
        <Reader v-if="mode_0 || mode_1" ref="readerRef" @read-finished="handleReadFinished" />
      </div>
    </div>
    <!-- 简历编辑器弹窗 -->

    <Teleport to="#modal-ResumeEdit">
      <div v-if="showResumeEditor" class="resume-editor">
        <ResumeEditor @submit="handleResumeEditSubmit" @exits="exitsResumeEditor" :job="jobSelection" />
      </div>
      <div v-if="issubmitting" style="z-index:2000;position:absolute;top:50%;left:50%;">
        <n-spin />
      </div>
    </Teleport>

    <Teleport to="#modal-root">
      <n-card class="startInterview" v-if="show_card">
        <!-- 步骤1：选择岗位 -->
        <transition :name="slideDirection" mode="out-in">
          <div v-if="step === 1" class="step1-card">
            <div class="card11">
              <n-card title="请选择岗位" size="small">
                <n-radio-group v-model:value="jobTypeSelection" name="primaryGroup">
                  <n-space vertical>
                    <n-radio v-for="item in jobTypeOptions" :key="item.value" :value="item.value" class="job_type">
                      {{ item.label }}
                    </n-radio>
                  </n-space>
                </n-radio-group>
              </n-card>
            </div>

            <div class="card12">
              <n-card size="small" v-if="jobTypeSelection">
                <n-radio-group v-model:value="jobSelection" name="secondaryGroup">
                  <n-grid :cols="4" :x-gap="12" :y-gap="8">
                    <n-gi v-for="item in getjobsOptions()" :key="item.value">
                      <n-radio :value="item.value" class="jobs">
                        {{ item.label }}
                      </n-radio>
                    </n-gi>
                  </n-grid>
                </n-radio-group>
              </n-card>
              <n-card size="small" v-else>
              </n-card>
            </div>
          </div>
        </transition>
        <template v-if="step === 1" #footer>
          <div class="footer-buttons">
            <n-button type="default" ghost @click="show_card = false">
              我再想想
            </n-button>
            <n-button type="primary" :disabled="!jobSelection" @click="addstep">
              继续
            </n-button>
          </div>
        </template>
        <transition :name="slideDirection" mode="out-in">
          <!-- 步骤2：上传简历 -->
          <div v-if="step === 2" class="step2-card">
            <h2>上传简历</h2>
            <n-tooltip trigger:hover>
              <template #trigger>
                <a-upload :customRequest="handleResumeUpload" :showUploadList="false"
                  accept=".txt,.doc,.docx,.pdf,.jpg,.jpeg,.png">
                  <a-button :loading="isProcessing" :disabled="isProcessing">
                    <upload-outlined></upload-outlined>
                    {{ isProcessing ? '加载中...' : '选择简历文件' }}
                  </a-button>
                </a-upload>
              </template>
              支持.txt,.doc,.docx,.pdf,.jpg,.jpeg,.png
            </n-tooltip>
            <!-- <n-tooltip trigger:hover>
              <template #trigger>
                <a-button type="default" @click="showResumeEditor = true" :disabled="isProcessing">快速编辑信息</a-button>
              </template>
              仅编辑信息
            </n-tooltip> -->

            <div v-if="resumesuggestions.length > 0" class="resume-infos">
              <transition-group name="fade" tag="div">
                <div class="info-item" v-for="(item, index) in resumesuggestions" :key="index">{{ item }}</div>
              </transition-group>
            </div>
            <div v-else class="noresume-infos">
              <a-skeleton :active="issubmitting||isProcessing" :title="false" :paragraph="{ rows: 10, width: Array(10).fill('100%') }" />
            </div>
          </div>
        </transition>

        <template v-if="step === 2" #footer>
          <div class="footer-buttons">
            <n-button type="default" @click="reducestep" :disabled="isProcessing">上一步</n-button>
            <n-button type="primary" @click="addstep" :disabled="!hasResume||isProcessing">继续</n-button>
          </div>
        </template>

        <!-- 步骤3：选择模式 -->
        <transition :name="slideDirection" mode="out-in">
          <div v-if="step === 3" class="step3-card-wrapper">
            <h2 class="card-title">选择模式</h2>
            <div class="step3-card">
              <!-- 非实时模式 -->
              <div class="mode-card" :class="{ 'card-selected': start_mode === 0 }" @click="start_mode = 0">
                <div class="mode-background non-realtime">
                  <span ghost class="mode-button">
                    非 实 时 模 式
                  </span>
                </div>
                <span style="font-size: 12px;"> *非实时模式下，你可以停顿和查看对话历史</span>
              </div>

              <!-- 实时模式 -->
              <div class="mode-card" @click="start_mode = 1" :class="{ 'card-selected': start_mode === 1 }">
                <div class="mode-background realtime">
                  <span ghost class="mode-button">
                    实 时 模 式
                  </span>
                </div>
                <span style="font-size: 12px;"> *实时模式下，你不能查看历史，并且需要开启摄像头</span>
              </div>

            </div>
          </div>
        </transition>
        <template v-if="step === 3" #footer>
          <div class="footer-buttons">
            <n-button type="default" @click="reducestep">上一步</n-button>
            <n-button type="primary" @click="startInterview"
              :disabled="start_mode != 0 && start_mode != 1">开始</n-button>
          </div>
        </template>
      </n-card>

      <!-- 内容区域启用指针事件 -->
      <div v-if="isModalOpen" class="modal-mask" style="pointer-events: auto;" @click.stop>
        <div class="modal-header">
          <h3>提示</h3>
        </div>
        <div class="modal-content">
          <p>{{ currentModal.message }}</p>
        </div>
        <div class="modal-footer">
          <button @click="handleConfirm" class="btn confirm">是</button>
          <button @click="handleCancel" class="btn cancle">否</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>
<script setup>
import { BadgeRibbon, message } from 'ant-design-vue'
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../utils/axios'
import ResumeEditor from '../components/ResumeEditor.vue'
import HistoryView from '../components/HistoryView.vue'
import ReportView from '../components/ReportView.vue';
import Reader from '../components/Reader.vue'
// import{addModal,Notice} from '../components/Notice/index.js';
import { NCard, NRadio, NRadioGroup, NSpace, NButton, NDivider, NGrid, NGi, NUpload, NSpin, NIcon } from 'naive-ui'
import { useStore } from '../store'
const store = useStore() // 获取全局状态管理实例，一个app只有一个store实例

let readerRef = null
const router = useRouter()
//开始面试相关
const show_card = ref(false);
const showResumeEditor = ref(false);

const jobTypeSelection = ref('')
const jobSelection = ref('')
import{jobTypeOptions,jobsOptions,weight1Map,weight2Map,interview_init_score} from '../utils/score.js' 

const getjobsOptions = () => {
  return jobsOptions[jobTypeSelection.value] || []
}

const resumesuggestions = ref([])
const tmp_resume_score = ref({})
// 添加处理状态
const isProcessing = ref(false)
const hasResume = ref(false)
// if (store.interview.resume != '') {
//   hasResume.value = true
// }
//进行加分
const add_score = (in_score, thing = 1) => {
  //1:简历加分 2:语言加分 3 文本加分
  // 正确遍历方式:遍历对象使用in，数组使用forEach，对象访问可以使用.或者[key]
  for (const category in in_score) {
    // 检查 score 中是否有对应的分类
    if (store.interview.score[category]) {
      in_score[category].forEach(Item => {
        store.interview.score[category].forEach(scoreItem => {
          if (scoreItem.name === Item.name) {
            if (thing === 1)
              scoreItem.value += Item["value"] * 3;
            else if (thing === 2)
              scoreItem.value += Item["value"]*1.5;
            else if (thing === 3)
              scoreItem.value += Item["value"] * 3;
          }
        });
      });
    }
  }
  console.log('加分成功', store.interview.score)
};
// 这里上传简历文件并获取分析结果(暂时不保存简历文件到库)
async function handleResumeUpload({ file }) {
  console.log('开始上传文件:', file.name, file.type)
  isProcessing.value = true

  const formData = new FormData()
  formData.append('file', file.file || file)
  formData.append('job', jobSelection.value)
  formData.append('user_id', localStorage.getItem('id'))

  try {
    const response = await axios.post('/upload/resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.code === 200) {
      console.log("上传成功！", response.data.data)
      // 保存提取的简历信息文本
      console.log("resume:", response.data.data.resume)
      store.interview.resume = response.data.data.resume
      store.interview.resumefile = file
      store.interview.resume_type=1//文档类型
      //添加简历分数
      tmp_resume_score.value = response.data.data.resume_score
      if (response.data.data.resume_suggestion.length > 0){
        resumesuggestions.value = response.data.data.resume_suggestion
        store.interview.resume_advice = resumesuggestions.value
      }
      else resumesuggestions.value = ['您的简历堪称完美!']
      hasResume.value = true
      message.success('加载成功')
    }
  } catch (error) {
    console.error('上传错误:', {
      status: error.response?.status,
      data: error.response?.data,
      headers: error.response?.headers,
      error: error
    })

    if (error.response?.status === 400) {
      message.error('不支持的文件类型或文件格式错误：' + (error.response?.data?.detail || '仅支持txt、doc、docx、pdf、jpg、jpeg、png格式'))
    } else {
      message.error('上传失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    isProcessing.value = false
  }
}
const issubmitting = ref(false)
const handleResumeEditSubmit = async (text,file_name,callback) => {

  console.log('提交简历信息:', text)
  issubmitting.value = true
  let user_id = localStorage.getItem('id')
  try {
    const res = await axios.post('/interview/resume', {
      resume: text,
      file_name:file_name,
      user_id: user_id
    })
    console.log('成功', res)
    if (res.data.data.resume_suggestion.length > 0){
      store.interview.resume_advice = res.data.data.resume_suggestion
      resumesuggestions.value = res.data.data.resume_suggestion
    }
    else resumesuggestions.value = ['您的简历堪称完美!']
    tmp_resume_score.value = res.data.data.resume_score
    store.interview.resume = res.data.data.resume
    store.interview.resumefile = res.data.data.resume
    store.interview.file_name=file_name+'.txt'
    store.interview.resume_type=0//文字json

    hasResume.value = true
    showResumeEditor.value = false
    message.success('加载成功')
  } catch (error) {
    console.log('失败',error)
    message.error('错误: ', error)
  }
  finally {
    issubmitting.value = false
    if(callback&&typeof callback=='function')
      callback();//回调函数
  }
}

import interview from '../components/interview.vue'
import interviewRealTime from '../components/interviewRealTime.vue'
const mode_0 = ref(false)
const mode_1 = ref(false)
const start_mode = ref(-1);//开始面试的模式0:非实时全景模式,1.实时全景模式
let interviewRef = null;//面试组件对象
let interviewRealTimeRef = null;
const step = ref(1)
const slideDirection = ref('slide-right')
const reducestep = () => {
  slideDirection.value = 'slide-right'
  step.value--
}
const addstep = () => {
  slideDirection.value = 'slide-left'
  step.value++
}
//子组件跳转
const viewmode=ref(1)
const reportData=ref({})
const toHistory=()=>{
  viewmode.value=1
  reportData.value={}
}
const toReport=(data)=>{
  reportData.value=data
  viewmode.value=2
}

// 开始面试
async function startInterview() {
  show_card.value = false
  store.interview.job=jobSelection.value
  if (tmp_resume_score.value) {
    store.init_score();
    add_score(tmp_resume_score.value,1)
    console.log('更新简历分数')
  }

  if (start_mode.value == 0) {
    mode_0.value = true;
    await nextTick();//等待组件渲染完成
    // 调用子组件方法:发送简历信息
    if (interviewRef) {
      await interviewRef.init_chat();
    }
    add_score(interview_init_score)
    console.log('更新初始分数')
  }
  else if (start_mode.value == 1) {
    mode_1.value = true;
  }
  //清空卡片状态
  store.interview.weight1=weight1Map[jobSelection.value]
  store.interview.weight2=weight2Map[jobSelection.value]
  tmp_resume_score.value = {}
  resumesuggestions.value = []
  jobTypeSelection.value = ''
  jobSelection.value = ''
  step.value = 1
}
const exitsResumeEditor = () => {
  showResumeEditor.value = false
}
const readingText = (text, flag = 0) => {
  //console.log('朗读',text)
  readerRef.speakText(text, flag)
}
const handleReadFinished = () => {
  interviewRealTimeRef.handleReadFinished()
  //console.log('朗读结束')
}

const handleChatText = (chat) => {
  //console.log('handleChatText',chat)
  // 累加过程性分数
  const tmp_score = chat.tmp_score['tot'] || 0;
  //遍历对象
  for (const item in store.interview.score) {
    store.interview.score[item].forEach(sub_item => {
      if (sub_item.name in chat.tmp_score) {
        sub_item.value += chat.tmp_score[sub_item.name] * 0.01 * tmp_score*0.5;
      }
    })
  }
  console.log('更新过程分数,', store.interview.score)

};
const handleImgChat = (chat) => {
  let suggest = chat.info
  if (suggest && suggest.length > 0)
    console.log('图片建议:', suggest)
  add_score(chat.img_score)
};
function safePushAdvice(data) {
  if (typeof data === 'string') {
    store.interview.advice.push(data);
  } else {
    store.interview.advice.push(...data);
  }
}

// 完成面试
const finishInterview = async (summary) => {
  message.success('恭喜你，面试结束')
  console.log('最终结果:', summary)
  add_score(summary.voice_score)
  add_score(summary.text_score)
  
  //存储文本建议
  safePushAdvice(summary.suggestions);
  console.log('更新文本建议:', store.interview.advice)
  //存储音频建议
  safePushAdvice(summary.emo_suggest);
  safePushAdvice(summary.voice_suggest);
  safePushAdvice(summary.voice_tip);
  console.log('更新语音建议:', store.interview.advice)
  safePushAdvice(store.interview.resume_advice);
  console.log('更新简历建议:',store.interview.advice)
  return;
}

import { startRecord, stopRecord } from '../utils/recording';
import { NumberSmall1 } from '@vicons/carbon'
const blobs = ref([])

async function uploadAudioBlob(blob) {
  
    if (!(blob instanceof Blob)||!blob) {

      console.warn('不是有效的Blob对象:', blob);
      return;
    }
    const formData = new FormData();
    formData.append('file', blob, 'record.wav');
    try {
      const response = await axios.post('/upload/audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });
      console.log('录音上传成功')
    } catch (error) {
      message.error('上传录音失败：' + error)
      console.error(error)
    }
}

const handleStopRecord = async (callback = null, flag = 1) => {
  //flag为1表示要上传

  let blob = await stopRecord();
  if (!(blob instanceof Blob)||!blob) {
    console.log('录音已停止！');
  }else{
    blobs.value.push(blob);
    //console.log(blobs.value.length)
  }
  if (flag) {
    try {
      for (let blob of blobs.value) {
        await uploadAudioBlob(blob);
      }
    }
    catch (error) {
      console.error('录音上传失败:', error)
    }
    blobs.value = [];
  }
  if (callback && typeof callback === 'function') {
    callback();
  }
}
const handleClearRecord = () => { 
  blobs.value = [];
  console.log('录音记录已清空')
}
//退出面试
const handleExitInterview =async () => {
  store.init_interview()//清空单次面试信息
  blobs.value=[]
  await stopRecord();
  try{
    const res=await axios.post('/interview/init')
    console.log('初始化成功',res.data)
  }
  catch(error){
    console.log('初始化失败')
  }
  mode_0.value = false;
  mode_1.value = false;
  start_mode.value = -1;
};
onMounted(async() => { 
    await handleExitInterview();
});










//摄像相关
const isCameraActive = ref(false)
const cameraVideo = ref(null)
const sliderValue = ref(30) // 默认设为中间值

// 添加录制相关的状态
const mediaRecorder = ref(null)
const recordedChunks = ref([])
const isRecording = ref(false)
const recordingStartTime = ref(null)
const recordingDuration = ref('00:00')
let recordingTimer = null
const islatest_save = ref(false);//最新的录像是否保存

let cameraStream = null
let audioContext = null
let gainNode = null// 浏览器内置的音频处理节点
let microphone = null// 用于连接麦克风
// 面试步骤
const resumePath = ref('')
const currentQuestion = ref('')
const isAnswerComplete = ref(false)
const isInterviewComplete = ref(false)
const currentVideoPath = ref('')
// 添加面试问题相关的状态
const interviewQuestions = ref([])
const currentQuestionIndex = ref(0)
const isInterviewStarted = ref(false)

// 显示问题预览和确认对话框
function showConfirmInterview() {
  const previewQuestions = interviewQuestions.value.slice(0, 3).map((q, i) => `${i + 1}. ${q}`).join('\n')
  const totalQuestions = interviewQuestions.value.length

  addModal({
    message: `AI已根据您的简历生成了${totalQuestions}个面试问题。以下是部分问题预览：\n\n${previewQuestions}\n\n是否开始模拟面试？`,
    onConfirm: startInterview,
    onCancel: () => {
      message.info('您可以稍后点击"开始面试"按钮开始')
    }
  })
}
// 显示当前问题
function showCurrentQuestion() {
  if (currentQuestionIndex.value < interviewQuestions.value.length) {
    const question = interviewQuestions.value[currentQuestionIndex.value]
    currentQuestion.value = question
  } else {
    // 面试结束
    isInterviewComplete.value = true
    message.success('面试完成！')
    stopAnswerRecording()
    stopCamera()
  }
}

// 处理下一个问题
function nextQuestion() {
  stopAnswerRecording()
  currentQuestionIndex.value++
  isAnswerComplete.value = false
  showCurrentQuestion()

  // 如果还有问题，自动开始录制
  if (!isInterviewComplete.value) {
    startAnswerRecording()
  }
}

// 获取第一个问题
async function getFirstQuestion() {
  try {
    const response = await axios.post('/api/interview/next_question', {
      resume_path: resumePath.value
    })
    if (response.data.code === 200) {
      currentQuestion.value = response.data.data.question
      isAnswerComplete.value = false
      isInterviewComplete.value = response.data.data.completed
    }
  } catch (error) {
    message.error('获取面试问题失败：' + (error.response?.data?.detail || error.message))
    console.error('获取问题错误详情:', {
      status: error.response?.status,
      data: error.response?.data,
      headers: error.response?.headers,
      error: error
    })
  }
}

const analysisProgress = ref('准备分析...')

// 添加分析状态和进度更新函数
async function startAnalysis() {
  try {
    analysisProgress.value = '正在分析视频...'
    // 调用后端分析接口
    const response = await axios.post('/api/analyze', {
      videoPath: currentVideoPath.value,
      jobType: jobType.value
    })

    if (response.data.success) {
      analysisProgress.value = '分析完成，正在生成报告...'
      // 等待2秒后跳转到报告页面
      setTimeout(() => {
        router.push({
          path: '/report',
          query: {
            analysisId: response.data.analysisId,
            jobType: jobType.value
          }
        })
      }, 2000)
    } else {
      throw new Error(response.data.message || '分析失败')
    }
  } catch (error) {
    console.error('分析出错:', error)
    analysisProgress.value = '分析失败，请重试'
  }
}

// 修改面试完成处理函数
function handleInterviewComplete() {
  isInterviewComplete.value = true
  startAnalysis()
}

//摄像头相关
async function toggleCamera() {
  if (isCameraActive.value) {
    if (!islatest_save.value) {
      addModal({ message: '录像未保存，是否保存录像？', onConfirm: saveRecording });
    }
    addModal({ message: '是否关闭摄像头？', onConfirm: stopCamera });
  } else {
    await startCamera()
  }
}
async function startCamera() {
  try {
    // 获取摄像头和麦克风媒体流
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'environment'
      },
      audio: true // 启用音频
    })

    // 初始化Web Audio API
    audioContext = new (window.AudioContext || window.webkitAudioContext)()
    microphone = audioContext.createMediaStreamSource(stream)
    gainNode = audioContext.createGain()

    // 连接音频节点：麦克风 → 增益控制 → 目的地
    microphone.connect(gainNode)
    gainNode.connect(audioContext.destination)

    // 设置初始音量
    updateVolume(sliderValue.value)

    cameraVideo.value.srcObject = stream
    isCameraActive.value = true
    cameraStream = stream
  } catch (error) {
    console.error('设备访问错误:', error)
  }
}
function stopCamera() {
  // 断开音频节点
  if (microphone && gainNode) {
    microphone.disconnect()
    gainNode.disconnect()
  }

  if (audioContext) {
    audioContext.close()
  }
  if (cameraStream) {
    // 停止流中的所有轨道
    cameraStream.getTracks().forEach(track => track.stop())
  }

  if (cameraVideo.value) {
    cameraVideo.value.srcObject = null
  }
  stopAnswerRecording();
  isCameraActive.value = false
  cameraStream = null
  audioContext = null
  gainNode = null
  microphone = null
}

//录像相关
function toggleRecording() {
  if (isRecording.value) {
    stopAnswerRecording()
    addModal({ message: '是否保存录像？', onConfirm: saveRecording });
  } else {
    startAnswerRecording()
  }
}
// 开始录制函数
function startAnswerRecording() {
  // if (!cameraStream) {
  //   message.error('请先开启摄像头')
  //   return
  // }

  try {
    recordedChunks.value = []
    // mediaRecorder.value = new MediaRecorder(cameraStream)

    // mediaRecorder.value.ondataavailable = (event) => {
    //   if (event.data.size > 0) {
    //     recordedChunks.value.push(event.data)
    //   }
    // }

    // mediaRecorder.value.start(1000) // 每1s记录一次数据
    isRecording.value = true
    recordingStartTime.value = Date.now()
    updateRecordingDuration()
    message.success('开始录制')
  } catch (error) {
    console.error('录制失败:', error)
    message.error('录制失败')
  }
}

// 停止录制
function stopAnswerRecording() {
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop()
    isRecording.value = false
    clearInterval(recordingTimer)
    message.success('回答录制完成')

    // 如果面试还未结束，显示下一题按钮
    if (!isInterviewComplete.value) {
      isAnswerComplete.value = true
    }
  }
}

// 更新录制时长
function updateRecordingDuration() {
  recordingTimer = setInterval(() => {
    const duration = Math.floor((Date.now() - recordingStartTime.value) / 1000)
    const minutes = Math.floor(duration / 60).toString().padStart(2, '0')
    const seconds = (duration % 60).toString().padStart(2, '0')
    recordingDuration.value = `${minutes}:${seconds}`
  }, 1000)
}

// 保存录像函数
async function saveRecording() {
  if (recordedChunks.value.length === 0) {
    console.log('没有可保存的录制内容')
    return
  }

  try {
    const blob = new Blob(recordedChunks.value, { type: 'video/webm' })
    const formData = new FormData()
    formData.append('video', blob, 'interview.webm')
    formData.append('jobType', jobType.value)

    const response = await axios.post('/api/save-video', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      currentVideoPath.value = response.data.videoPath
      islatest_save.value = true
      message.success('视频保存成功')
      // 保存成功后自动开始分析
      handleInterviewComplete()
    } else {
      throw new Error(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存视频出错:', error)
    message.error('保存视频失败，请重试')
  }
}

// 组件卸载时清理
onBeforeUnmount(async () => {
  stopAnswerRecording()
  stopCamera()
  if (recordingTimer) {
    clearInterval(recordingTimer)
  }

  await stopRecord();
})

//弹窗队列相关
// 状态
const modalQueue = ref([]);
const currentModal = ref(null);
const isModalOpen = ref(false);

// 方法
const addModal = (modalConfig) => {
  modalQueue.value.push(modalConfig);
  if (!currentModal.value) showNextModal();
};

const showNextModal = () => {
  if (modalQueue.value.length === 0) {
    currentModal.value = null;
    isModalOpen.value = false;
    return;
  }
  currentModal.value = modalQueue.value.shift();
  isModalOpen.value = true;
};

const handleConfirm = () => {
  currentModal.value?.onConfirm?.();
  showNextModal();
};

const handleCancel = () => {
  currentModal.value?.onCancel?.();
  showNextModal();
};

</script>

<style scoped lang="scss">
.home {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100%;
  border: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  background-color: #f4f4f9;
  position: relative;
}

.viewarea {
  height: 100%;
  width: 100%;
  padding: 0%;
  margin: 0%;
  background: #fff;
  flex: 8;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-radius: 4px;

  .camera {
    width: 80%;
    height: auto;
    aspect-ratio: 16/9;
    object-fit: cover;
    background: #000;
    transform: scaleX(-1);
    margin: 0 auto;
  }

  .camera-pip {
    position: fixed;
    right: 20px;
    bottom: 20px;
    width: 180px;
    height: auto;
    border: 1px solid #fff;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    background-color: #000;

    &:hover {
      transform: scale(1.02);
      transition: transform 0.2s;
    }
  }

  .placeholder {
    color: #999;
    font-size: 1rem;
  }
}

.controlarea {
  background-color: #04191a;
  /* 混合过渡的蓝色渐变 */
  height: 100%;
  display: flex;
  flex-direction: column;
  flex: 2;
  gap: 8px;
  padding: 16px;

  /* 添加阴影和圆角边框 */
  box-shadow: 0 2px 4px rgba(230, 6, 6, 0.1);
  border-radius: 12px;
  /* 更圆一点的边角 */
  border: 1px solid rgb(0, 252, 218);
  /* 淡蓝色边框 */
}


.btn1 {
  background: #1890ff;
  width: auto;
  height: 36px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: white;
  font-size: 14px;
  transition: all 0.3s;

  &:hover {
    background: #40a9ff;
  }

  &:active {
    background: #096dd9;
  }

  &.recording {
    background: #ff4d4f;

    &:hover {
      background: #ff7875;
    }

    &:active {
      background: #d9363e;
    }
  }
}

.reader {
  position: relative;
  height: 150px;
  width: 100%;
  padding: 0px;
  margin: 0px;
}

.modal-mask {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 320px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  z-index: 1000;

  .modal-header {
    background: #f5f5f5;
    height: 40px;
    width: 100%;
    display: flex;
    align-items: center;
    padding: 0 16px;
    border-bottom: 1px solid #e8e8e8;

    h3 {
      margin: 0;
      color: #262626;
      font-size: 14px;
    }
  }

  .modal-content {
    padding: 16px;
    background: white;

    p {
      margin: 0;
      color: #595959;
      font-size: 14px;
      line-height: 1.5;
    }
  }

  .modal-footer {
    padding: 8px 16px;
    background: #f5f5f5;
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    border-top: 1px solid #e8e8e8;

    .btn {
      min-width: 64px;
      height: 32px;
      font-size: 14px;
      padding: 0 12px;
      border-radius: 2px;
      transition: all 0.3s;

      &.confirm {
        background: #1890ff;
        color: white;

        &:hover {
          background: #40a9ff;
        }

        &:active {
          background: #096dd9;
        }
      }

      &.cancle {
        background: #f5f5f5;
        color: #595959;
        border: 1px solid #d9d9d9;

        &:hover {
          background: #fafafa;
          border-color: #40a9ff;
          color: #40a9ff;
        }

        &:active {
          background: #f5f5f5;
          border-color: #096dd9;
          color: #096dd9;
        }
      }
    }
  }
}

.startInterview {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 680px;
  min-height: 480px;
  height: 540px;
  overflow: hidden;
  z-index: 1000;
  background: white;

  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);

  .step1-card {
    display: flex;
    flex-direction: column;
    height: 100%;
    gap: 16px;

    .card11 {
      height: 120px;
      overflow-y: auto;

      .n-card {
        height: 100%;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

        &__content {
          padding-top: 5px;
        }
      }
    }

    .card12 {
      height: 280px;
      overflow-y: auto;

      .n-card {
        height: 100%;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

        &__content {
          padding-top: 5px;
        }
      }
    }

    .card11 .n-radio-group {
      .n-space {
        flex-direction: row !important;
        /* 强制横向排列 */
        flex-wrap: wrap;
        /* 允许换行 */
        gap: 8px;
        /* 设置间距 */
      }
    }

    .job_type {
      padding: 10px 16px;
      margin: 4px 0;
      border-radius: 4px;
      transition: all 0.3s;

      &:hover {
        background-color: #f5f5f5;
      }

      &.n-radio--checked {
        background-color: #e6f4ff;
        color: #1890ff;
      }
    }

    .jobs {
      display: block;
      padding: 8px 12px;
      margin: 4px 0;
      border: 1px solid #f0f0f0;
      border-radius: 4px;
      text-align: center;
      transition: all 0.3s;

      &:hover {
        border-color: #d9d9d9;
      }

      &.n-radio--checked {
        border-color: #1890ff;
        background-color: #e6f4ff;
        color: #1890ff;
      }
    }
  }

  .step2-card {
    text-align: center;
    position: relative;
    margin: 32px 0;
    height: 100%;

    display:flex h2 {
      margin-bottom: 16px;
      font-size: 16px;
      color: #262626;
    }
  }

  .step3-card-wrapper {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;

    .card-title {
      font-size: 24px;
      margin: 20px 0;
      text-align: center;
    }

    .step3-card {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      width: 100%;
      max-width: 800px;
      padding: 0 20px;
      box-sizing: border-box;
    }

    .mode-card {
      position: relative;
      border-radius: 16px;
      overflow: hidden;
      cursor: pointer;
      transition: box-shadow 0.3s ease;

      &:hover {
        box-shadow: 0 0 12px rgba(24, 144, 255, 0.6);
      }

      .mode-background {
        width: 100%;
        height: 300px;
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;

        .mode-button {
          // width:30px;
          // height: 200px; 
          writing-mode: vertical-rl;
          text-orientation: upright;
          font-weight: bold;
          font-size: 18px;
          border: none;
          background-color: rgba(0, 0, 0, 0.4);
          color: #fff;
          padding: 8px;
          border-radius: 8px;
        }
      }

      .non-realtime {
        background-image: url('../assets/interviewBack2.png');
      }

      .realtime {
        background-image: url('../assets/interviewRealTimeBack2.png');
      }
    }

    .card-selected {
      box-shadow: 0 0 12px rgba(24, 144, 255, 0.6);
    }
  }

  .footer-buttons {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-top: 1px solid #f0f0f0;

    .n-button {
      min-width: 120px;
      height: 40px;
    }
  }
}

/* --- step 横向滑动动画 --- */
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.1s ease;
  position: absolute;
  width: 100%;
}

.slide-left-enter-from {
  transform: translateX(30%);
  opacity: 0;
}

.slide-left-enter-to {
  transform: translateX(0%);
  opacity: 1;
}

.slide-left-leave-from {
  transform: translateX(0%);
  opacity: 1;
}

.slide-left-leave-to {
  transform: translateX(-30%);
  opacity: 0;
}

.slide-right-enter-from {
  transform: translateX(-30%);
  opacity: 0;
}

.slide-right-enter-to {
  transform: translateX(0%);
  opacity: 1;
}

.slide-right-leave-from {
  transform: translateX(0%);
  opacity: 1;
}

.slide-right-leave-to {
  transform: translateX(30%);
  opacity: 0;
}

// 动画定义
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-enter-to {
  opacity: 1;
  transform: translateY(0);
}

.resume-editor {
  position: fixed;
  top: 50%;
  left: 50%;
  z-index: 1000;
}

.noresume-infos {
  height: 250px;
  width: 80%;
  display: block;
  margin: 0 auto;
  margin-top: 30px;
}

.resume-infos {
  height: 250px;
  width: 80%;
  display: block;
  margin: 0 auto;
  margin-top:30px;
  overflow-y: auto;
  padding: 3px;
  font-size: 16px;
  color: rgb(238, 40, 5);
  background: linear-gradient(rgba(221, 215, 158, 0.448), rgb(45, 191, 98));
  //background-color: rgba(243, 228, 24, 0.536); // 几乎透明
  border: 1px solid rgb(31, 99, 15); // 类似激光轮廓
  box-shadow:
    0 0 5px rgba(197, 189, 115, 0.3),
    0 0 10px rgba(189, 173, 95, 0.2) inset;
  border-radius: 8px;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background-color: rgb(22, 172, 172);
    border-radius: 3px;
  }

  .info-item {
    padding: 10px;
    width: 100%;
    border-bottom: 1px solid #295907;
    margin-top: 3px;
     text-align: left;
    margin-bottom: 3px;
    padding: 2px 0px;
    border-radius: 6px;
    font-size: 16px;
    animation: fadeIn 0.3s ease-in-out;
  }
}

@keyframes blink {
  0% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }

  100% {
    opacity: 1;
  }
}

@keyframes pulse {
  0% {
    opacity: 1;
  }

  50% {
    opacity: 0.7;
  }

  100% {
    opacity: 1;
  }
}

.analysis-status {
  text-align: center;
  padding: 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.analysis-progress {
  color: #666;
  margin-top: 10px;
  font-size: 14px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}
</style>