<template>
  <div class="tts-container">
    <div class="voice-controls" v-if="voices.length > 0">
      <select v-model="selectedVoice">
        <option v-for="voice in chineseVoices" :key="voice.name" :value="voice">
          {{voiceNameMap[voice.name]}}
        </option>
      </select>
      
      <label>
        <span style="width:30px;">语速</span>
        <input type="range" v-model="rate" class="ranges" min="1.5" max="2" step="0.01" >
       <span>{{ rate }}</span>
      </label>
      <label>
        <span style="width:30px;">音调</span>
        <input type="range" v-model="pitch" class="ranges" min="0.5" max="2" step="0.1" >
       <span>{{ pitch }}</span>
      </label>
    </div>
  </div>
  <button @click="pauseSpeak" v-if="isSpeaking && !isPaused" class="pause-btn">暂停</button>
</template>

<script setup>
import { rateProps } from 'naive-ui'
import { ref, onMounted ,defineExpose,defineEmits} from 'vue'
//const text = '你好，我是语音朗读系统'
const text=''
const isSpeaking = ref(false)
const isPaused = ref(false)
const voices = ref([])
const selectedVoice = ref(null)
const chineseVoices = ref([])
const rate = ref(1.5)
const pitch = ref(1.5)
const voiceNameMap = {
  'Microsoft Huihui - Chinese (Simplified, PRC)': '普通话女声（慧慧）（慢速）',
  'Microsoft Kangkang - Chinese (Simplified, PRC)': '普通话男声（康康）（较慢）',
  'Microsoft Yaoyao - Chinese (Simplified, PRC)': '普通话女声（瑶瑶）（较慢）',
  'Microsoft Xiaoxiao Online (Natural) - Chinese (Mainland)': '自然女声（晓晓）（中速）',
  'Microsoft Xiaoyi Online (Natural) - Chinese (Mainland)': '自然女声（小艺）（中速）',
  'Microsoft Yunjian Online (Natural) - Chinese (Mainland)': '自然男声（云健）（中速）',
  'Microsoft Yunxi Online (Natural) - Chinese (Mainland)': '自然男声（云希）（较快）',
  'Microsoft Yunxia Online (Natural) - Chinese (Mainland)': '自然女声（云霞）（较快）',
  'Microsoft Yunyang Online (Natural) - Chinese (Mainland)': '自然男声（云阳）（较快）',
  'Microsoft Xiaobei Online (Natural) - Chinese (Northeastern Mandarin)': '东北话（小贝）（中速）',
  'Microsoft HsiaoChen Online (Natural) - Chinese (Taiwan)': '台湾女声（晓甄）（中速）',
  'Microsoft YunJhe Online (Natural) - Chinese (Taiwan)': '台湾男声（云哲）（中速）',
  'Microsoft HsiaoYu Online (Natural) - Chinese (Taiwanese Mandarin)': '台湾女声（晓渝）（中速）',
  'Microsoft Xiaoni Online (Natural) - Chinese (Zhongyuan Mandarin Shaanxi)': '陕西话（小妮）（较快）'
}

// 初始化语音合成
onMounted(() => {
  // 等待语音列表加载
  speechSynthesis.onvoiceschanged = () => {
    voices.value = speechSynthesis.getVoices()
    filterChineseVoices()
  }
  
  // 立即尝试获取语音列表
  voices.value = speechSynthesis.getVoices()
  filterChineseVoices()
  selectedVoice.value = chineseVoices.value[4]
})

// 过滤中文语音
const filterChineseVoices = () => {
  chineseVoices.value = voices.value.filter(voice => 
    !voice.lang.includes('zh-HK')&&(voice.lang.includes('zh') || voice.lang.includes('cmn'))
  )
  if (chineseVoices.value.length > 0&&selectedVoice.value==null) {
    selectedVoice.value = chineseVoices.value[4]
  }
}
const emit = defineEmits(['read-finished']) // 声明自定义事件
const pauseSpeak = () => {
  if (isSpeaking.value) {
    if (isPaused.value) {
      speechSynthesis.resume()
      isPaused.value = false
    } else {
      speechSynthesis.pause()
      isPaused.value = true
      emit('read-finished')
    }
  }
}

// 核心朗读函数
const speakText = (textToSpeak,flag=0) => {
  //console.log('textToSpeak',textToSpeak)
  //console.log('flag',flag)
  //console.log('kkk')
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel()
  }
  
  const utterance = new SpeechSynthesisUtterance(textToSpeak)
  utterance.lang = 'zh-CN'//默认中文
  utterance.rate = rate.value
  utterance.pitch = pitch.value
    if (selectedVoice.value) {
    utterance.voice = selectedVoice.value
    //console.log('已选择:',selectedVoice.value)
  }
  utterance.onstart = () => {
    isSpeaking.value = true
    isPaused.value = false
  }
  
  utterance.onend = () => {
    isSpeaking.value = false
    isPaused.value = false
    if(flag){
      //console.log('朗读结束')
      emit('read-finished')
    }
  }
  
  utterance.onerror = (event) => {
    console.warn('语音合成错误:', event)
    isSpeaking.value = false
    isPaused.value = false
    if(flag){
      //console.log('朗读结束')
       emit('read-finished')
    }
  }
  //console.log('朗读',textToSpeak)
  speechSynthesis.speak(utterance)
}
defineExpose({
  speakText
})
</script>

<style lang="scss" scoped>
.tts-container {
    position:relative;
    width:100%;
    height:80%;
    min-width:100px;
    min-height:50px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 400px;
  margin: 0px;
  padding: 0px;
  border-radius: 8px;
  background-color: #dbc818;
}

button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #45a049;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.pause-btn {
  background-color: #ff9800;
  width:100%;
}

.pause-btn:hover {
  background-color: #e68a00;
}

.voice-controls {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
  width:100%;
  position:relative;
}
select{
  width:90%;
  margin:0 auto;
background-color: #f0d83c00;
}
label {
  height: 32px;
  /* 给足高度避免滑动时被挤压 */
  display: flex;
  align-items: center;
  gap: 5px;
  width: 100%;
}
input[type="range"].ranges {
  -webkit-appearance: none;
  appearance: none;
  width: 70%;
  height: 20px; /* 给控件本身足够空间 */
  background: transparent;
  padding: 0;
  margin: 0;
  display: block;
}

/* 滑轨 */
input[type="range"].ranges::-webkit-slider-runnable-track {
  height: 4px;
  border-radius: 2px;
  background: linear-gradient(to right, #4dd0e1, #00796b);
}

/* 滑块 */
input[type="range"].ranges::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  height: 14px;
  width: 14px;
  border-radius: 50%;
  background: linear-gradient(#4dd0e1, #00796b);
  margin-top: -5px; /* 关键：垂直对齐轨道 */
  box-shadow: 0 0 2px rgba(229, 189, 189, 0.3);
  cursor: pointer;
  position: relative;
  z-index: 1; /* 防止影响布局层级 */
}
</style>