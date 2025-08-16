<template>
  <div class="speech-container">
    <h1>Web Speech API 语音识别演示</h1>
    
    <div class="control-panel">
      <button 
        @click="togglewebSpeechInstance"

        :class="{ 'active': isListening }"
      >
        {{ isListening ? '停止识别' : '开始语音识别' }}
      </button>
      
      <select v-model="selectedLanguage" class="language-select">
        <option value="zh-CN">中文 (普通话)</option>
        <option value="en-US">English (US)</option>
        <option value="ja-JP">日本語</option>
      </select>
    </div>

    <div v-if="statusMessage" class="status">
      {{ statusMessage }}
    </div>

    <div class="result-container">
      <h3>实时识别结果：</h3>
      <div class="result-content">
        {{ inputt }}{{ finalTranscript }}
      </div>
    </div>

    <div v-if="errorMessage" class="error">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue';

// 状态管理
const isListening = ref(false);
const isProcessing = ref(false);
const finalTranscript = ref('');
const interimTranscript = ref('');
const inputt=ref('')
const statusMessage = ref('');
const errorMessage = ref('');
const selectedLanguage = ref('zh-CN');

// SpeechRecognition 实例
let webSpeechInstance = null;

// 检查浏览器兼容性
const checkCompatibility = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    errorMessage.value = '您的浏览器不支持 Web Speech API，请使用 Chrome 或 Edge 最新版';
    return false;
  }
  return true;
};

// 初始化语音识别
const initwebSpeechInstance = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  webSpeechInstance = new SpeechRecognition();
  
  // 配置参数
  webSpeechInstance.continuous = true; // 持续识别
  webSpeechInstance.interimResults = true; // 返回临时结果
  webSpeechInstance.lang = selectedLanguage.value; // 设置语言

  // 事件处理
  webSpeechInstance.onstart = () => {
    console.log('开始')
    isListening.value = true;
    isProcessing.value = true;
    statusMessage.value = '语音识别已启动...';
    interimTranscript.value = '';
    finalTranscript.value = '';
  };

  webSpeechInstance.onresult = (event) => {
    interimTranscript.value = '';

    // 处理识别结果
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal)
        finalTranscript.value += transcript;
    }
  };

  webSpeechInstance.onerror = (event) => {
    console.error('错误')
    isListening.value = false;
    isProcessing.value = false;
    
    // 常见错误处理
    switch(event.error) {
      case 'no-speech':
        errorMessage.value = '未检测到语音';
        break;
      case 'audio-capture':
        errorMessage.value = '无法捕获音频';
        break;
      case 'not-allowed':
        errorMessage.value = '麦克风访问被拒绝';
        break;
      default:
        errorMessage.value = `识别错误: ${event.error}`;
    }
  };

  webSpeechInstance.onend = () => {
    console.log('终止')
    isProcessing.value = false;
    inputt.value+=finalTranscript.value
    finalTranscript.value = '';
    if (isListening.value) {
      // 如果仍在监听状态但识别结束，自动重启
      statusMessage.value = '重新连接中...';
      webSpeechInstance.start();
    } else {
      statusMessage.value = '语音识别已停止';
    }
  };
};

// 开始/停止识别
const togglewebSpeechInstance = () => {
  if (!checkCompatibility()) return;

  if (isListening.value) {
    // 停止识别
    webSpeechInstance.stop();
    isListening.value = false;
  } else {
    // 开始识别
    finalTranscript.value = '';
    interimTranscript.value = '';
    errorMessage.value = '';
    
    if (!webSpeechInstance) {
      initwebSpeechInstance();
    } else {
      webSpeechInstance.lang = selectedLanguage.value;
    }
    
    try {
      webSpeechInstance.start();
    } catch (error) {
      errorMessage.value = `启动失败: ${error.message}`;
    }
  }
};

// 组件卸载时清理
onBeforeUnmount(() => {
  if (webSpeechInstance) {
    webSpeechInstance.stop();
  }
});
</script>

<style lang="scss" scoped>
.speech-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Arial', sans-serif;
}

.control-panel {
  display: flex;
  gap: 1rem;
  margin: 2rem 0;
  
  button {
    padding: 0.75rem 1.5rem;
    background-color: #4285f4;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.3s;
    
    &:hover {
      background-color: #3367d6;
    }
    
    &:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
    }
    
    &.active {
      background-color: #34a853;
    }
  }
  
  .language-select {
    padding: 0.5rem;
    border-radius: 4px;
    border: 1px solid #ddd;
  }
}

.status {
  margin: 1rem 0;
  padding: 0.5rem;
  color: #666;
  font-style: italic;
}

.error {
  margin: 1rem 0;
  padding: 1rem;
  background-color: #ffebee;
  color: #d32f2f;
  border-radius: 4px;
}

.result-container {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #f5f5f5;
  border-radius: 8px;
  
  h3 {
    margin-top: 0;
    color: #333;
  }
  
  .result-content {
    min-height: 100px;
    
    .final {
      font-size: 1.2rem;
      color: #000;
      margin-bottom: 0.5rem;
    }
    
    .interim {
      color: #666;
      font-style: italic;
    }
  }
}
</style>