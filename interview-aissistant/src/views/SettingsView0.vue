<template>
  <div class="tts-container">
    <button @click="toggleSpeak" :disabled="isSpeaking && !isPaused">
      {{ isPaused ? '继续' : (isSpeaking ? '停止' : '朗读') }}
    </button>
    <button @click="pauseSpeak" v-if="isSpeaking && !isPaused" class="pause-btn">暂停</button>
    
    <div class="voice-controls" v-if="voices.length > 0">
      <select v-model="selectedVoice" @change="updateVoice">
        <option v-for="voice in chineseVoices" :key="voice.name" :value="voice">
          {{voiceNameMap[voice.name]}}
        </option>
      </select>
      
      <label>
        语速:
        <input type="range" v-model="rate" min="1.5" max="2" step="0.01" @input="updateSettings">
        {{ rate}}
      </label>
      
      <label>
        音调:
        <input type="range" v-model="pitch" min="1" max="2" step="0.01" @input="updateSettings">
        {{ pitch }}
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const text = '你好，我是语音朗读系统,今天要来测试你的面试能力'
const isSpeaking = ref(false)
const isPaused = ref(false)
const voices = ref([])
const selectedVoice = ref(null)
const chineseVoices = ref([])
const rate = ref(1.5)
const pitch = ref(1.5)

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
})
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
// 过滤中文语音
const filterChineseVoices = () => {
  chineseVoices.value = voices.value.filter(voice => 
    !voice.lang.includes('zh-HK')&&(voice.lang.includes('zh') || voice.lang.includes('cmn'))
  )
  console.log(chineseVoices.value)
  if (chineseVoices.value.length > 0) {
    selectedVoice.value = chineseVoices.value[0]
  }
}

// 朗读控制
const toggleSpeak = () => {
  if (isSpeaking.value && !isPaused.value) {
    speechSynthesis.cancel()
    isSpeaking.value = false
    isPaused.value = false
  } else {
    speakText(text)
  }
}

const pauseSpeak = () => {
  if (isSpeaking.value) {
    if (isPaused.value) {
      speechSynthesis.resume()
      isPaused.value = false
    } else {
      speechSynthesis.pause()
      isPaused.value = true
    }
  }
}

// 更新语音设置
const updateSettings = () => {

  if (isSpeaking.value) {
    speechSynthesis.cancel()
    speakText(text)
  }
}

// 更新语音选择
const updateVoice = () => {
  if (isSpeaking.value) {
    speechSynthesis.cancel()
    speakText(text)
  }
}

// 核心朗读函数
const speakText = (textToSpeak) => {
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel()
  }
  
  const utterance = new SpeechSynthesisUtterance(textToSpeak)
  utterance.lang = 'zh-CN'
  utterance.rate = rate.value
  utterance.pitch = pitch.value
  
  if (selectedVoice.value) {
    utterance.voice = selectedVoice.value
  }
  
  utterance.onstart = () => {
    isSpeaking.value = true
    isPaused.value = false
  }
  
  utterance.onend = () => {
    isSpeaking.value = false
    isPaused.value = false
  }
  
  utterance.onerror = (event) => {
    console.error('语音合成错误:', event)
    isSpeaking.value = false
    isPaused.value = false
  }
  
  speechSynthesis.speak(utterance)
}
</script>

<style scoped>
.tts-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 400px;
  margin: 20px;
  padding: 15px;
  border-radius: 8px;
  background-color: #f5f5f5;
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
}

.pause-btn:hover {
  background-color: #e68a00;
}

.voice-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

select, input[type="range"] {
  width: 100%;
}

label {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>