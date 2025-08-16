<template>
    <div class="main_content" :class="{ 'isfinal': chat_status === 2, 'noisfinal': chat_status != 2 }">

        <div class="note">{{ sendTime }}秒后自动发送</div>
        <textarea :value="inputText + finalTranscript" placeholder="回答内容" rows="10" readonly></textarea>
        <div class="btns">
            <n-button @click="handlebegin" type="warning" :disabled="isbegin||chat_status===2">开始</n-button>
            <n-button @click="handlesendBtn" type="warning" :disabled="chat_status===2||bnsend">发送</n-button>
            <!-- <n-button @click="fixReading" type="warning" :disabled="chat_status===2">无响应?点我</n-button> -->
            <n-button @click="amodel = true" type="warning">退出</n-button>
        </div>
        <div class="tmp_note">{{ interimTranscript }}</div>
        <div ref="infosRef" class="infos">
            <transition-group name="fade" tag="div">
                <div v-for="(msg, index) in infoList" :key="index" class="message-item">
                    <!-- 图标根据 ftype 选择 -->
                    <n-icon :component="iconMap[msg.ftype]" size="18" style="margin-right: 6px;" />
                    <div class="message-text" :class="'ftype-' + msg.ftype">{{ msg.text }}</div>
                    <div class="message-time">{{ msg.time }}</div>
                </div>
            </transition-group>
        </div>
        <div class="report" v-if="chat_status === 2">
            <ReportView :reportData="report_data" :enter="2"></ReportView>
        </div>
        <a-modal v-model:open="amodel" title="提示">
            <p>确认退出？</p>
            <template #footer>
                <n-button @click="amodel = false">取消</n-button>
                <n-button type="error" @click="exitInterview">确认</n-button>
            </template>
        </a-modal>
        <a-modal v-model:open="amodel2" title="提示">
            <p>面试一经开始就无法终止,是否继续？</p>
            <template #footer>
                <n-button @click="amodel2 = false;isbegin=false">否</n-button>
                <n-button type="warning" @click="beginbegin" style="margin-left:5px;">是</n-button>
            </template>
        </a-modal>
        <video ref="videoRef" autoplay muted :width="vwidth" :height="vheight" style="display: none;"></video>
        <canvas ref="canvasRef" :width="vwidth" :height="vheight" style="display: none;"></canvas>
    </div>
</template>
<script setup>
import { ref, computed, watch, onMounted, onUnmounted, onBeforeUnmount, nextTick, defineEmits, defineProps } from 'vue'
import { NButton } from 'naive-ui'
import axios from '../utils/axios'
import ReportView from '../components/ReportView.vue';
import { useStore } from '../store'
import { message } from 'ant-design-vue'
const store = useStore()
import { NIcon } from 'naive-ui'
import {
    WarningOutline,
    CheckmarkCircleOutline,
    CloseCircleOutline,
    InformationCircleOutline
} from '@vicons/ionicons5'
const iconMap = {
    success: CheckmarkCircleOutline,
    error: CloseCircleOutline,
    warning: WarningOutline,
    info: InformationCircleOutline
}

// SpeechRecognition 实例
let webSpeechInstance = null;

const selectedLanguage = ref('zh-CN');
const isListening = ref(false);
const isProcessing = ref(false);
const inputText = ref('');
const finalTranscript = ref('');
const interimTranscript = ref('');
const errorMessage = ref('');
const chat_status = ref(0);//面试状态,0:开始,1:过程,2:结束

const emit = defineEmits(['exit-interview', 'finish-interview', 'readingText', 'handleChatText', 'startRecord', 'stopRecord', 'hangleImgChat']);

// 检查浏览器兼容性
const checkCompatibility = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        errorMessage.value = '您的浏览器不支持语音识别，请使用 Chrome 或 Edge 最新版';
        return false;
    }
    return true;
};
let retryCount = 0;
const MAX_RETRY = 4;
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
        //inputText.value = '';
        finalTranscript.value = '';
        interimTranscript.value = '';
    };

    webSpeechInstance.onresult = (event) => {
        interimTranscript.value = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript.value += transcript;
            } else {
                interimTranscript.value += transcript;
            }
        }
        retryCount = 0;
    };

    webSpeechInstance.onerror = (event) => {
        isListening.value = false;
        isProcessing.value = false;
finalTranscript.value = '';
        interimTranscript.value = '';
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
        console.log('识别错误:', errorMessage.value)
        if (retryCount < MAX_RETRY) {
            retryCount++;
            setTimeout(() => {
                initSpeechRecognition();
            }, 1000); // 延迟重启，给浏览器缓冲时间
        }
        setTimeout(() => {
            errorMessage.value = '';
        }, 3000);
    };

    webSpeechInstance.onend = () => {
        console.log('识别结束')
        isListening.value = false;
        isProcessing.value = false;
         finalTranscript.value = '';
        interimTranscript.value = '';
        inputText.value+=finalTranscript.value
    };
};
const speechLock = ref(false);
// 开始/停止语音识别
const switchSpeech = () => {
    //先检查浏览器兼容性
    if (!checkCompatibility()) return;

    if (isListening.value) {
        webSpeechInstance.stop();
        emit('stopRecord');
        console.log('关闭了语言')
    } else {
        if (!webSpeechInstance) {
            initSpeechRecognition();
            console.log('初始化了语音')
        } else {
            webSpeechInstance.lang = selectedLanguage.value;
        }

        try {
            if (speechLock.value) return;
            webSpeechInstance.start();
            emit('startRecord');
            console.log('启动了语言')
        } catch (error) {
            errorMessage.value = `启动失败: ${error.message}`;
            console.log('启动失败:', error);
            setTimeout(() => {
                errorMessage.value = '';
            }, 3000);
        }
    }
};
const tmp_content = ref('');
const messages = ref([])
const report_data = ref({})
const bnsend=ref(false)
// 发送消息
const sendMessage = async (text, flag = 1) => {
      if(bnsend.value)return
      bnsend.value=true
    if (chat_status.value === 2) {
        console.log('面试已经结束')
        showModel1.value = false;
        return;
    }

    if (!text.trim()){
        bnsend.value=false
        return;//输入为空
    } 
    console.log('用户回答', text)
    sendTime.value = 10;
    // 清空输入
    inputText.value = '';
    finalTranscript.value = '';
    interimTranscript.value = '';
    if (isListening.value) {
        switchSpeech();
    }
    const is_begin = chat_status.value === 0 ? true : false;
    try {
        const res = await axios.post('/interview/step', {
            user_input: text,
            is_begin: is_begin,
        });
        if (flag)
            messages.value.push({
                type: 'user',
                content: text
            })
        console.log('获取回复成功:', res);
        sendTime.value=10;
        const ai_response = res?.data.data;
        let content = ai_response.request

        tmp_content.value = content
        speechLock.value = true
        // 模拟AI回复
        if (ai_response?.is_end === true) {

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
                        emit('readingText', "好，面试结束，等待结果...", 1)//朗读ai回复
            messages.value.push({
                type: 'assistant',
                content: "恩好的，面试结束，等待结果..."
            })
            if (webSpeechInstance) {
                webSpeechInstance.stop();
            }//关闭语言识别
            stopTime()//关闭实时计时器
            stopVideo()//关闭摄像头
            sendTime.value=10
            //保存记录
            try {
                let formData = new FormData();
                formData.append('user_id', uid);
                formData.append('mode', 1)
                formData.append('video', store.interview.videoFile)
                console.log('已经添加视频文件:',store.interview.videoFile)
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
                    mode: 1,
                    resource: {
                        videoUrl: store.interview.urls?.videoUrl ?? '',
                        audioUrl: store.interview.urls.audioUrl,
                        textUrl: store.interview.urls.textUrl,
                    },
                    total_score: store.interview.total_score,
                    score_detail: store.interview.score,
                    message: messages.value,
                    advice: store.interview.advice,
                    job: store.interview.job,
                })
                console.log('保存记录成功:', save_res)
                message.success('记录已保存！')
                //开启报告界面
                report_data.value = {
                    infos: store.interview.advice,
                    mode: 1,
                    message: messages.value,
                    ...resource_url.data,
                    score: store.interview.score,
                    weight1: store.interview.weight1,
                    weight2: store.interview.weight2,
                }
                chat_status.value = 2;
            } catch (error) {
                console.log('保存失败:', error);
                message.error('保存失败！')
            }
        } else {
            emit('readingText', content, 1)//朗读ai回复
            if (!ai_response?.is_begin) {
                emit('handleChatText', ai_response);
            }
            messages.value.push({
                type: 'assistant',
                content: content
            })
        }
    } catch (error) {
        const errorMsg = error.response?.data?.message ||
            error.message ||
            '发送消息失败';
        errorMessage.value = `发送消息失败: ${errorMsg}`;
        console.log('API调用错误:', error);
        //5秒后自动清除错误消息
        setTimeout(() => {
            errorMessage.value = '';
        }, 5000);
    }finally{
        bnsend.value=false;
    }
};
const handleReadFinished = () => {
    console.log('朗读终止')
    speechLock.value = false//允许webspeech开始记录声音
    switchSpeech()//开始录音
};
const amodel = ref(false)
const exitInterview = () => {
        if (webSpeechInstance) {
        webSpeechInstance.stop();//关闭语言识别
    }
    stopTime();//关闭摄像头计时器
    stopVideo();//关闭摄像头
    emit('exit-interview')
}
const fixReading = () => {
    if (speechLock.value && !tmp_content.value) emit('readingText', content, 1)
    else
        console.log('朗读系统良好~~~')
    if (!isListening.value && !speechLock.value) initSpeechRecognition()
    else console.log('语言检测良好')
};

const handlesendBtn =async () => {
    if((inputText.value+finalTranscript.value)===''||bnsend.value)return;
    await sendMessage(inputText.value+finalTranscript.value)
};
//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>摄像头相关
const cv = window.cv;
const videoRef = ref(null)
const canvasRef = ref(null)
const vwidth = ref(320)
const vheight = ref(240)
const rate = ref(0.1)
const threshold = computed(() => {
    return vwidth.value * vheight.value * rate.value
})// 默认差异阈值

console.log('阀值:', threshold.value)
const lastDiffValue = ref(0) // 记录最后一帧的差异值

let cap = null // OpenCV VideoCapture 对象
let streaming = false
let mediaStream = null;//用于关闭摄像头
let prevFrame = null // 存储前一帧用于比较
let cnt = 1;
let mediaRecorder = null
let recordedChunks = []//用于保存录制的记录
function getNewestImg() {
    const canvas = document.createElement('canvas')
    canvas.width = vwidth.value
    canvas.height = vheight.value

    const ctx = canvas.getContext('2d')
    ctx.drawImage(videoRef.value, 0, 0, canvas.width, canvas.height)

    // 返回 base64 图片（可用于展示或上传）
    const dataURL = canvas.toDataURL('image/png')
    return dataURL
}

function startVideo() {
    navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
        videoRef.value.srcObject = stream
        videoRef.value.play()
        streaming = true
         mediaStream = stream; // 保存下来，方便后续关闭摄像头
        cap = new cv.VideoCapture(videoRef.value)

        // 初始化 MediaRecorder
        recordedChunks = []
        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'video/webm; codecs=vp9' // 或 'video/webm; codecs=vp8'，取决于浏览器支持
        })

        mediaRecorder.ondataavailable = event => {
            if (event.data && event.data.size > 0) {
                recordedChunks.push(event.data)
            }
        }

        mediaRecorder.start() // 开始录制
    })
}
function stopVideo() {
    if (!mediaRecorder || mediaRecorder.state !== 'recording') return
    mediaRecorder.stop()
    // 关闭摄像头
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
    const timestamp = Date.now(); // 当前时间戳
    const randomStr = Math.random().toString(36).substring(2, 8); // 随机字符串
    const uniqueFilename = `record_${timestamp}_${randomStr}.webm`;

    mediaRecorder.onstop = () => {
        const blob = new Blob(recordedChunks, { type: 'video/webm' })

        const video_file = new File([blob], uniqueFilename, { type: "video/webm" });
        store.interview.videoFile = video_file;
        console.log('已保存文件:', uniqueFilename)
    }
}
// 计算两帧之间的差异
function calculateFrameDiff(src) {
    if (!prevFrame) {
        prevFrame = new cv.Mat()
        src.copyTo(prevFrame)
        return 0
    }

    // 转换为灰度图减少计算量
    const gray1 = new cv.Mat()
    const gray2 = new cv.Mat()
    cv.cvtColor(prevFrame, gray1, cv.COLOR_RGBA2GRAY)
    cv.cvtColor(src, gray2, cv.COLOR_RGBA2GRAY)

    // 计算绝对差异
    const diff = new cv.Mat()
    cv.absdiff(gray1, gray2, diff)

    // 阈值处理
    const thresholded = new cv.Mat()
    cv.threshold(diff, thresholded, 10, 1, cv.THRESH_BINARY)//只要大于10就设为1

    // 计算差异值
    let diffValue = 0
    for (let i = 0; i < thresholded.data.length; i++) {
        diffValue += thresholded.data[i]
    }
    //console.log('差异值:',diffValue)

    // 更新前一帧
    src.copyTo(prevFrame)

    // 释放内存
    gray1.delete()
    gray2.delete()
    diff.delete()
    thresholded.delete()

    return diffValue
}
//提取关键帧
async function captureFrame() {
    if (!cap) return
    const src = new cv.Mat(videoRef.value.height, videoRef.value.width, cv.CV_8UC4)
    cap.read(src)

    // 计算与前一帧的差异
    const diffValue = calculateFrameDiff(src)

    // 如果差异大于阈值，则认为是关键帧
    if (diffValue > threshold.value) {
        cv.imshow(canvasRef.value, src)
        let tmp = canvasRef.value.toDataURL('image/png')
        //let base64Data = tmp.split(',')[1]  // 去掉前缀
        //console.log('生成关键帧:',base64Data)
        //console.log('生成关键帧',tmp)
        try {
            const res = await axios.post('upload/img', {
                img: tmp,
                flag: 1
            })
            console.log('上传关键帧成功!', res.data)
            emit('handleImgChat', res.data)
            for (let item of res.data.info) {
                addInfo(item, 'info');
            }
            messages.value.push(...res.data.info)
        } catch (error) {
            console.log('上传关键帧失败!', error)
        }
        lastDiffValue.value = diffValue
        console.log('捕获到关键帧', cnt++)
    }

    src.delete()
}

let time1 = null
let time2 = null
let time3 = null
const time1Lock = ref(false)
const time2Lock = ref(false)
const time3Lock = ref(false)
const sendTime = ref(10)//计时器秒数
let stopWatcher = null
function startTime() {
    time3 = setInterval(async () => {
        if (time3Lock.value) return
        time3Lock.value = true
        sendTime.value--;
        if (sendTime.value < 0) {
            sendTime.value = 10
            await sendMessage(inputText.value+finalTranscript.value)
        }
        time3Lock.value = false
    }, 1000)
    stopWatcher = watch(
        [interimTranscript],
        ([newInterim]) => {
            if (newInterim !== '') {
                sendTime.value = 10
                console.log('更新计时:', sendTime.value)
            }
        }
    )
    // 每隔500ms执行一次captureFrame
    time1 = setInterval(async () => {
        if (time1Lock.value) return
        time1Lock.value = true
        await captureFrame()
        time1Lock.value = false
    }, 1000)
    time2 = setInterval(async () => {
        if (time2Lock.value) return
        time2Lock.value = true
        const img = getNewestImg()
        //console.log('获取base64数据;',img)
        //console.log('base64数据:',img)
        try {
            const res = await axios.post('upload/img', {
                img: img,
                flag: 2
            })
            console.log('上传间隔帧成功!', res.data)
            emit('handleImgChat', res.data)
            for (let item of res.data.info) {
                addInfo(item, 'warning');
            }
            messages.value.push(...res.data.info)
        } catch (error) {
            console.log('上传间隔帧失败!', error)
        }
        time2Lock.value = false
    }, 1000)

}
function stopTime() {
    if (time1) {
        clearInterval(time1)
        time1 = null
    }
    if (time2) {
        clearInterval(time2)
        time2 = null
    }
    if (time3) {
        clearInterval(time3)
        time3 = null
    }
    if (stopWatcher) {
        stopWatcher()
        stopWatcher = null
    }
}
const isbegin = ref(false)
const amodel2=ref(false)
const handlebegin =() => { 
amodel2.value = true;
}
const beginbegin = async () => {
    amodel2.value = false;
    isbegin.value=true;
    const resume = store.interview.resume;
    if (resume === '') {
        console.log('简历为空!');
        return;
    }
    inputText.value = JSON.stringify(resume);
    chat_status.value = 0;
    await sendMessage(inputText.value, 0);
    chat_status.value = 1;

    startVideo()//启动摄像头
    startTime()//启动实时计时器
}

const infosRef = ref(null)
const infoList = ref([])
// 模拟添加消息
function addInfo(msg, type) {
    const now = new Date().toLocaleTimeString()
    infoList.value.push({ text: msg, time: now, ftype: type })

    // 等DOM渲染完，再滚动到底部
    nextTick(() => {
        const el = infosRef.value
        el.scrollTop = el.scrollHeight
    })
}
defineExpose({
    handleReadFinished
});
onMounted(() => {
    emit('readingText', "欢迎,先请坐")
    emit('readingText', "把简历给我...")
    addInfo("温馨提示:请保持环境安静，专心面试", 'success')
    addInfo("温馨提示:请吐字清晰，面带微笑~~~", 'success')
    addInfo("温馨提示:实时模式下,你无需操作鼠标...", 'success')
    addInfo("面试即将开始...", 'info')
    addInfo("请注意音量大小是否合适...", 'warning')
    //     addInfo("面试即将开始...",'success')
    // addInfo("面试即将开始...",'error')
});
onBeforeUnmount(() => {
    if (webSpeechInstance) {
        webSpeechInstance.stop();//关闭语言识别
    }
    stopTime();//关闭摄像头计时器
    stopVideo();//关闭摄像头
});
</script>
<style scoped lang="scss">
.main_content {
    position: relative;
    width: 100%;
    height: 100%;

    background-color: rgb(194, 157, 157);
    background-image: url('../assets/interviewRealTimeBack.png');
    background-size: cover;
    /* 背景图铺满 */
    background-position: center;
    /* 居中显示 */
    background-repeat: no-repeat;

    /* 不重复 */
    &::-webkit-scrollbar {
        width: 10px;
    }

    &::-webkit-scrollbar-track {
        background: transparent;
    }

    &::-webkit-scrollbar-thumb {
        background-color: rgb(6, 226, 17);
        border-radius: 3px;
    }
}

.noisfinal {
    overflow: hidden;

}

.isfinal {
    overflow-y: auto;
}

textarea {
    width: 60%;
    display: block; // block 块级元素，会自动换行
    margin: 0 auto; // 水平居中
    height: 300px; // 控制高度，让滚动更明显
    padding: 15px;
    font-size: 16px;
    color: rgb(234, 255, 0);
    background-color: rgba(209, 204, 204, 0.05); // 几乎透明
    border: 1px solid rgb(0, 255, 255); // 类似激光轮廓
    box-shadow:
        0 0 5px rgba(0, 255, 255, 0.3),
        0 0 10px rgba(0, 255, 255, 0.2) inset;
    border-radius: 8px;

    overflow-y: auto; // 允许垂直滚动
    backdrop-filter: blur(4px); // 更有未来感的半透明效果
    outline: none;

    &::placeholder {
        color: rgba(204, 248, 7, 0.94)
    }

    scrollbar-width: thin;
    scrollbar-color: #0ff transparent;
}

.note {
    font-size: 20px;
    color: rgba(84, 255, 4, 0.914);
    font-family: 'Courier New', Courier, monospace;
}

/* Webkit 滚动条样式 */
textarea::-webkit-scrollbar {
    width: 6px;
}

textarea::-webkit-scrollbar-track {
    background: transparent;
}

textarea::-webkit-scrollbar-thumb {
    background-color: #0ff;
    border-radius: 3px;
}

.btns {
    width: 60%;
    margin: 10px auto;
    display: flex;
    justify-content: space-between; // 或 space-around
    gap: 10px; // 按需调整按钮之间的间距
}

.tmp_note {
    width: 70%;
    height: 70px;
    display: block;
    margin: 10px auto;
    align-items: left;
    color: rgba(84, 255, 4, 0.914);
    padding: 15px;
    font-size: 16px;
    background-color: rgba(0, 0, 0, 0.05); // 几乎透明
    border: 1px solid rgb(0, 255, 255); // 类似激光轮廓
    box-shadow:
        0 0 5px rgba(0, 255, 255, 0.3),
        0 0 10px rgba(0, 255, 255, 0.2) inset;
    border-radius: 8px;
}

.infos {
    width: 95%;
    height: 150px;
    margin: 10px auto 0 auto; //依次为上、右、下、左
    display: block;
    font-size: 16px;
    color: rgb(234, 255, 0);
    background-color: rgba(209, 204, 204, 0.05); // 几乎透明
    border: 1px solid rgb(0, 255, 255); // 类似激光轮廓
    box-shadow:
        0 0 5px rgba(0, 255, 255, 0.3),
        0 0 10px rgba(0, 255, 255, 0.2) inset;
    border-radius: 8px;

    &::-webkit-scrollbar {
        width: 6px;
    }

    &::-webkit-scrollbar-track {
        background: transparent;
    }

    &::-webkit-scrollbar-thumb {
        background-color: #0ff;
        border-radius: 3px;
    }

    overflow-y: auto;
    padding: 3px;
}

.report {
    height: 600px;
    width: 100%;
}

// 每条信息
.message-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1px;
    padding: 1px 0px;
    border-radius: 6px;
    font-size: 14px;
    animation: fadeIn 0.3s ease-in-out;

    .iconfont {
        margin-right: 6px;
    }

    .message-text {
        flex: 1;
        font-size: 16px;
        word-break: break-word;
    }

    .message-time {
        font-size: 16px;
        margin-left: 10px;
        white-space: nowrap;
        opacity: 0.7;
        font-weight: bold;
        color: #00ff04fa;
    }
}

// 按 ftype 控制颜色风格
.ftype-error {
    color: #ff0000;
}

.ftype-success {
    color: #56ff02;
}

.ftype-info {
    color: #bbff00;
}

.ftype-warning {
    color: #ff01b3;
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
</style>