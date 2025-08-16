<template>
  <div class="container">
    <h1>🎤 Vosk.js 语音识别演示</h1>
    <button @click="toggleRecognition" :disabled="isLoading || (!model && !error)">
      {{ getButtonText() }}
    </button>
    <button @click="add">
      累加{{ x }}次
    </button>
    <div v-if="partialResult">📝 部分识别：{{ partialResult }}</div>
    <div v-if="finalResult">✅ 最终结果：{{ finalResult }}</div>
    <div v-if="error" class="error">❌ 错误：{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount, onBeforeMount } from 'vue'
import * as Vosk from 'vosk-browser/dist/vosk.js'
import { createAudioWorkletNode } from '../utils/audioWorkletNode.js'

// 状态管理
const isLoading = ref(false)
const isRunning = ref(false)
const partialResult = ref('')
const finalResult = ref('')
const error = ref('')
const x = ref(0)

// 音频相关实例
let recognizer = null
let audioContext = null
let model = null
let stream = null
let audioWorkletNode = null

// 安全的消息验证
const validateMessage = (msg) => {
  if (!msg || typeof msg !== 'object') {
    console.error('无效的消息格式:', msg)
    throw new Error('无效的识别结果格式')
  }
  return msg
}

// 结果处理函数 
const handleResult = (event) => {
  try {
    // 1. 从CustomEvent的detail属性获取真实数据
    const msg = event.detail;
    console.log('原始事件结构:', JSON.parse(JSON.stringify(event)));

    // 2. 深度验证数据结构
    if (!msg || !msg.result) {
      throw new Error(`无效的消息结构: ${JSON.stringify(msg)}`);
    }

    // 3. 处理Vosk的特殊结果格式
    const textResult = msg.result.text ||
      msg.result.result?.[0]?.text ||
      msg.result.alternatives?.[0]?.text;

    if (!textResult) {
      console.warn('未找到文本结果，完整消息:', msg);
      finalResult.value = '无有效识别结果';
      return;
    }

    // 4. 更新结果并记录置信度
    finalResult.value = textResult;
    console.log('识别成功:', {
      text: textResult,
      confidence: msg.result.confidence,
      raw: msg.result
    });

  } catch (err) {
    console.error('结果处理错误:', err, '原始事件:', event);
    error.value = `识别错误: ${err.message}`;
    // 调试用 - 临时显示原始数据
    finalResult.value = `DEBUG: ${JSON.stringify(event.detail, null, 2)}`;
  }
};

const handlePartial = (msg) => {
  try {
    const validMsg = validateMessage(msg)
    //console.log('原始部分识别结果:', msg)
    partialResult.value = validMsg?.detail?.result?.partial || '识别中...'
    console.log('部分结果:', partialResult.value)
  } catch (err) {
    console.error('部分结果处理错误:', err)
  }
}

// 清理资源
const cleanup = () => {
  if (audioWorkletNode) {
    audioWorkletNode.disconnect()
    audioWorkletNode.port.close()
    audioWorkletNode = null
  }

  if (recognizer) {
    // 安全移除事件监听
    try {
      recognizer.removeEventListener('result', handleResult)
      recognizer.removeEventListener('partialresult', handlePartial)
      recognizer.remove()
    } catch (err) {
      console.error('清理识别器时出错:', err)
    }
    recognizer = null
  }

  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }

  if (audioContext?.state !== 'closed') {
    audioContext?.close()
  }
  audioContext = null

  isRunning.value = false
}

// 模型加载
onBeforeMount(async () => {
  console.log('开始初始化')
  cleanup()
  console.log('开始加载模型')
  isLoading.value = true
  error.value = ''

  try {
    if (!model) {
      model = await Vosk.createModel('/model/vosk-model-cn-0.22.tar.gz')

      model.on('load', (message) => {
        console.log('模型加载消息:', message)
        if (message.result) {
          console.log('模型加载成功')
        } else {
          console.error('模型加载失败')
          error.value = '模型加载失败'
        }
        isLoading.value = false
      })

      model.on('error', (message) => {
        console.error('模型加载错误:', message.error)
        error.value = `模型加载错误: ${message.error}`
        isLoading.value = false
      })
    } else {
      console.log('模型已就绪')
      isLoading.value = false
    }
  } catch (err) {
    console.error('模型创建失败:', err)
    error.value = `模型创建失败: ${err.message}`
    isLoading.value = false
  }
})

// 辅助函数
function getButtonText() {
  if (isLoading.value) return '模型加载中...'
  if (!model && !error.value) return '等待模型加载...'
  if (isRunning.value) return '停止识别'
  return '开始识别'
}

function add() {
  x.value += 1
  if (model?.ready) {
    console.log('模型加载完毕')
    isLoading.value = false
  }
}

// 主识别功能
const toggleRecognition = async () => {
  if (isRunning.value) {
    cleanup()
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    // 确保模型已加载
    if (!model?.ready) {
      throw new Error('语音模型未准备好')
    }

    // 创建识别器
    recognizer = new model.KaldiRecognizer(16000)
    recognizer.setWords(true)

    // 添加事件监听
    recognizer.addEventListener('result', (event) => {
      handleResult(event);
    });
    recognizer.addEventListener('partialresult', handlePartial)

    // 获取音频流
    stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: 16000,
        echoCancellation: true,
        noiseSuppression: true
      },
      video: false
    })


    // 创建音频上下文
    audioContext = new (window.AudioContext || window.webkitAudioContext)({
      sampleRate: 16000
    })
    //console.log('音频轨道设置:', stream.getAudioTracks()[0].getSettings());
    // 确保输出包含：{ sampleRate: 16000, channelCount: 1 }
    // 初始化AudioWorklet
    audioWorkletNode = await createAudioWorkletNode(audioContext, stream)

    // 处理音频数据
    audioWorkletNode.port.onmessage = (e) => {
      if (e.data.type === 'audio' && recognizer) {
        try {
          const float32Array = new Float32Array(e.data.buffer)
          recognizer.acceptWaveformFloat(float32Array, e.data.sampleRate)
        } catch (err) {
          console.error('音频处理错误:', err)
          error.value = '音频处理失败'
        }
      }
    }

    isRunning.value = true
  } catch (err) {
    console.error('初始化失败:', err)
    error.value = err.message || '初始化失败'
    cleanup()
  } finally {
    isLoading.value = false
  }
}

// 组件卸载时清理
onBeforeUnmount(cleanup)
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: auto;
  padding: 2rem;
  font-family: Arial, sans-serif;
  text-align: center;
  background-color: aquamarine;
}

button {
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
  margin: 1rem 0;
  cursor: pointer;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-top: 1rem;
}
</style>