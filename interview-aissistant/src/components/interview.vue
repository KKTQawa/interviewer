<template>
    <div class="main_content" :class="{'isfinal': chat_status === 2,'noisfinal':chat_status != 2}">
        <div class="chat_area" ref="chatArea">
            <div v-for="(message, index) in messages" :key="index" :class="['message', message.type]">
                <div class="message-content">{{ message.content }}</div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
        </div>
        <div class="input_area">
            <textarea placeholder="请回答!" class="text-display" :value="inputText + finalTranscript" rows="3" readonly />
            <div class="controls">
                <button class="bbtn" @click="clearInput" :disabled="chat_status === 2 || isclearing || is_sending">清空
                </button>
                <button class="bbtn" @click="toggleSpeechRecognition" :disabled="chat_status === 2 || is_sending"
                    :class="{ btn_active: isListening }">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                        <line x1="12" y1="19" x2="12" y2="23"></line>
                        <line x1="8" y1="23" x2="16" y2="23"></line>
                    </svg>
                </button>
                <button class="bbtn" @click="sendMessage"
                    :disabled="!inputText && !finalTranscript || chat_status === 2 || is_sending||isListening">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="22" y1="2" x2="11" y2="13"></line>
                        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                    </svg>
                </button>
                <button class="bbtn" @click="amodel = true" style=" position: absolute;right:10px;">退出</button>
            </div>
        </div>
        <div class="report" v-if="chat_status === 2">
            <ReportView :reportData="report_data" :enter="1"></ReportView>
        </div>
        <a-modal v-model:open="amodel" title="提示">
            <p>确认退出？</p>
            <template #footer>
                <n-button @click="amodel = false">取消</n-button>
                <n-button type="error" @click="exitInterview">确认</n-button>
            </template>
        </a-modal>
    </div>
</template>
<script setup>
import axios from '../utils/axios.js';
import { ref, onMounted, onBeforeUnmount, nextTick, defineExpose } from 'vue';
import ReportView from '../components/ReportView.vue';
import { useStore } from '../store'
import { message } from 'ant-design-vue';
const store = useStore();

// 状态管理
const isListening = ref(false);
const isProcessing = ref(false);
const inputText = ref('');
const finalTranscript = ref('');
const interimTranscript = ref('');
const errorMessage = ref('');
const selectedLanguage = ref('zh-CN');
const messages = ref([]);
const chatArea = ref(null);
const chat_status = ref(0);//面试状态,0:开始,1:过程,2:结束

// SpeechRecognition 实例
let webSpeechInstance = null;
//父组件调用
const init_chat = async () => {
    messages.value = [];
    const resume = store.interview.resume;
    if (resume === '') {
        console.log('简历为空!');
        return;
    }
    inputText.value = JSON.stringify(resume);
    addMessage('assistant', "欢迎,先请坐");
    addMessage('assistant', "把简历给我看看先...");
    emit('readingText', "欢迎,先请坐")
    emit('readingText', "把简历给我看看先...")
    addMessage('user', '你好,这是我的简历');
    chat_status.value = 0;
    await sendMessage(0);
    chat_status.value = 1;
}

// 必须暴露方法，父组件才能访问
defineExpose({
    init_chat
});
const emit = defineEmits(['exit-interview', 'finish-interview', 'readingText', 'handleChatText', 'startRecord', 'stopRecord', 'clearRecord','uploadRecord']); // 声明要触发的事件
const report_data = ref([])
const is_sending = ref(false)
const is_summary = ref(false)
// 发送消息
const sendMessage = async (flag = 1) => {
    if (chat_status.value === 2) {
        console.log('面试已经结束')
        return;
    }
    const text = inputText.value;
    if (isListening.value) {
        webSpeechInstance.stop();
    }
     emit('stopRecord')
    if (!text.trim()) return;

    // 添加用户消息
    console.log('用户回答:', text)
    if (flag)
        addMessage('user', text);

    // 清空输入
    inputText.value = '';
    finalTranscript.value = '';
    const is_begin = chat_status.value === 0 ? true : false;
    try {
        // 这里应该是调用AI接口获取回复
        is_sending.value = true;
        const res = await axios.post('/interview/step', {
            user_input: text,
            is_begin: is_begin,
        });
        console.log('获取回复成功:', res);
        const ai_response = res?.data.data;
        // 模拟AI回复
        if (ai_response?.is_end === true) {
            is_summary.value = true;
            let voiceRes = {}
            let uid = localStorage.getItem('id')
            try {
                const voice_res = await axios.get('/interview/voice_mark');
                console.log('语言分析完成:', voice_res.data);
                voiceRes = voice_res.data
            } catch (error) {
                console.error('语言分析失败:', error);
            }
            const summary = { ...ai_response, ...voiceRes }
            let tot=summary?.total_score
            console.log('ai生成总结:', summary);

            emit('finish-interview', summary);
            if (ai_response?.request) {
                addMessage('assistant', "恩好的，面试结束，等待结果...");
                emit('readingText', "恩好的，面试结束，等待结果...")//朗读ai回复
                is_sending.value = false;
            }

            //保存记录
            try {
                let formData = new FormData();
                formData.append('user_id', uid);
                formData.append('mode', 0)
                if (store.interview.resume_type === 0) {
                    console.log('原始面试文件:', store.interview.resumefile)
                    const jsonContent = JSON.stringify(store.interview.resumefile);
                    const blob = new Blob([jsonContent], { type: "application/json" });
                    console.log('简历文件名:',store.interview.file_name)
                    formData.append("resume", blob, store.interview.file_name);
                } else {
                    formData.append('resume', store.interview.resumefile);
                }
                const resource_url = await axios.post('/interview/upload', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                });
                console.log('成功上传资源文件:', resource_url.data)
                store.interview.urls = resource_url.data;
                if (tot)
                    store.modify_score(tot)//整理分数
                else
                    store.modify_score()//整理分数
                console.log('已整理最终分数:', store.interview.total_score)
                const save_res = await axios.post("/history/save", {
                    user_id: uid,
                    mode: 0,
                    resource: {
                        videoUrl: store.interview.urls?.videoUrl ?? '',
                        audioUrl: store.interview.urls.audioUrl,
                        textUrl: store.interview.urls.textUrl,
                    },
                    total_score: store.interview.total_score,
                    score_detail: store.interview.score,
                    message: messages.value,
                    advice: store.interview.advice,
                    job:store.interview.job,
                })
                console.log('保存记录成功:', save_res)
                message.success('记录已保存！')
                //开启报告界面
                report_data.value = {
                    infos: store.interview.advice,
                    mode: 0,
                    message: messages.value,
                    ...resource_url.data,
                    score: store.interview.score,
                    weight1: store.interview.weight1,
                    weight2: store.interview.weight2,
                }
                chat_status.value = 2;
                is_sending.value = false;
                is_summary.value = false;
            } catch (error) {
                console.log('保存失败:', error);
                message.error('保存失败！')
            }

        } else {
            emit('readingText', ai_response.request)//朗读ai回复
            if (!ai_response?.is_begin) {
                emit('handleChatText', ai_response);
            }
            if (ai_response?.request) {
                console.log('ai回复:', ai_response.request);
                addMessage('assistant', ai_response.request);
            }
            is_sending.value = false;
        }
    } catch (error) {
        const errorMsg = error.response?.data?.message ||
            error.message ||
            '发送消息失败';
        errorMessage.value = `发送消息失败: ${errorMsg}`;
        console.error('API调用错误:', error);
        //5秒后自动清除错误消息
        setTimeout(() => {
            errorMessage.value = '';
        }, 5000);
    }
};

// 添加消息到聊天记录
const addMessage = (type, content) => {
    const message = {
        type,
        content,
        timestamp: new Date()
    };

    messages.value.push(message);
    scrollToBottom();
    if (type === 'assistant') {
        emit('readingText', content)
    }
};

const amodel = ref(false)
//退出面试
const exitInterview = () => {
    if (chat_status === 2)
        emit('exit-interview', 1); // 触发父组件事件
    else
        emit('exit-interview', 0);
};

// 处理文本编辑
const handleTextEdit = (event) => {
    inputText.value = event.target.innerHTML;
};

// 检查浏览器兼容性
const checkCompatibility = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        errorMessage.value = '您的浏览器不支持语音识别，请使用 Chrome 或 Edge 最新版';
        return false;
    }
    return true;
};
const isclearing = ref(false);
const clearInput = () => {
    isclearing.value = true;
    if (isListening.value) {
        webSpeechInstance.stop();

        emit('stopRecord', () => {
            // 停止录音后的回调逻辑
            console.log("语音录制已成功停止");
            finalTranscript.value = '';
            errorMessage.value = '';
            inputText.value = '';
            isclearing.value = false;
            emit('clearRecord')
        }, 0);
    } else {
        finalTranscript.value = '';
        errorMessage.value = '';
        inputText.value = '';
        isclearing.value = false;
        emit('clearRecord')

    }
};

// 初始化语音识别
const initSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    webSpeechInstance = new SpeechRecognition();

    webSpeechInstance.continuous = true;
    webSpeechInstance.interimResults = true;
    webSpeechInstance.lang = selectedLanguage.value;

    webSpeechInstance.onstart = () => {
        console.log('识别开始')
        isListening.value = true;
        isProcessing.value = true;
        finalTranscript.value = '';
        interimTranscript.value = '';
    };

    webSpeechInstance.onresult = (event) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript.value += transcript;
            }
        }
    };

    webSpeechInstance.onerror = (event) => {
        console.log('识别错误')
        isListening.value = false;
        isProcessing.value = false;
        finalTranscript.value = '';
        switch (event.error) {
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

        setTimeout(() => {
            errorMessage.value = '';
        }, 3000);
    };

    webSpeechInstance.onend = () => {
        console.log('识别结束')
        inputText.value += finalTranscript.value
        finalTranscript.value=''
        isListening.value = false;
        isProcessing.value = false;
    };
};

// 开始/停止语音识别
const toggleSpeechRecognition = () => {
    //先检查浏览器兼容性
    if (!checkCompatibility()) return;

    if (isListening.value) {
        webSpeechInstance.stop();
        emit('stopRecord', () => {}, 0);//默认先不上传  
    } else {
        if (!webSpeechInstance) {
            initSpeechRecognition();
        } else {
            webSpeechInstance.lang = selectedLanguage.value;
        }

        try {
            webSpeechInstance.start();
            emit('startRecord');
        } catch (error) {
            errorMessage.value = `启动失败: ${error.message}`;
            setTimeout(() => {
                errorMessage.value = '';
            }, 3000);
        }
    }
};

// 滚动到聊天区域底部
const scrollToBottom = () => {
    nextTick(() => {
        if (chatArea.value) {
            chatArea.value.scrollTop = chatArea.value.scrollHeight;
        }
    });
};

// 格式化时间
const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

// 组件卸载时清理
onBeforeUnmount(() => {
    if (webSpeechInstance) {
        webSpeechInstance.stop();
    }
    clearInput()
});

</script>

<style lang="scss" scoped>
.main_content {
    display: flex;
    flex-direction: column;
    position: relative;
    height: 100%;
    width: 100%;
    
    background-color: rgb(194, 157, 157);
    background-image: url('../assets/interviewBack.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    &::-webkit-scrollbar {
        width: 10px;
    }

    &::-webkit-scrollbar-track {
        background: transparent;
    }

    &::-webkit-scrollbar-thumb {
        background-color: rgb(110, 56, 245);
        border-radius: 3px;
    }
}

.chat_area {
    width:100%;
    
    padding: 20px;
    margin:0;
    overflow-y: auto;
    //background-color: #f0f2f5;
    display: flex;
    flex-direction: column;
    gap: 12px;

    &::-webkit-scrollbar {
        width: 6px;
    }

    &::-webkit-scrollbar-track {
        background: transparent;
    }

    &::-webkit-scrollbar-thumb {
        background-color: rgb(231, 76, 76);
        border-radius: 3px;
    }

    .message {
        max-width: 80%;
        padding: 12px 16px;
        border-radius: 18px;
        position: relative;
        word-wrap: break-word;
        line-height: 1.4;

        &.user {
            align-self: flex-end;
            //background-color: rgba(255, 255, 255, 0.374);
            backdrop-filter: blur(30px);
            color: rgba(28, 255, 3, 0.955);
            border-bottom-right-radius: 4px;
        }

        &.assistant {
            align-self: flex-start;
            //background-color: rgba(255, 255, 255, 0.374);
            backdrop-filter: blur(30px);
            color: rgba(239, 213, 15, 0.955);
            border-bottom-left-radius: 4px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .message-time {
            font-size: 0.75rem;
            color: rgba(248, 248, 249, 0.7);
            margin-top: 4px;
            text-align: right;
        }

    }
}

.input_area {
    padding: 12px 16px;
    position:relative;
    width:100%;
    display:flex;
    flex-direction: column;
    //background-color: rgba(232, 234, 228, 0.108);
    backdrop-filter: blur(5px);
    border-top: 1px solid #01f5dd;
    position: relative;

    .text-display {
        flex: 5;
        min-height: 40px;
        width: 100%;
        padding: 8px 2px;
        background-color: rgba(230, 231, 221, 0);

        border-color: rgb(2, 251, 222);
        outline: none;
        resize: none;
        backdrop-filter: blur(3px);
        color: #c6f606;
        font-size: 1rem;

        &::placeholder {
            color: #ccff00;
        }
    }

    .controls {
        flex:2;
        display:flex;
        flex-direction: row;
        gap: 8px;
        margin-top:20px;
        margin-left: 10px;
        
    }

    button {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;

        &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        svg {
            width: 20px;
            height: 20px;
        }
    }

    .bbtn {
        background-color: #d8d5d500;
        color: #1af905;

        &:hover:not(:disabled) {
            color: #f93e05;
        }
    }

    .btn_active {
        color: #f93e05;
    }
}

.noisfinal{
   overflow:hidden;
    .chat_area{
       flex:8;
    }
    .input_area{
       flex:2;
    }
}
.isfinal {
    overflow-y: auto;

    .chat_area {
        flex: 8;
        min-height:430px;
    }

    .input_area {
        flex: 2;
        height: 200px;
    }

    .report {
        flex: 15;
        width: 100%;
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>