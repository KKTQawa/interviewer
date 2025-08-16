<template>
  <div>
    <video ref="videoRef" autoplay muted :width="vwidth" :height="vheight"></video>
    <button @click="startVideo">开始视频</button>
    <button @click="startCaptureInterval">开始抽取</button>
    <canvas ref="canvasRef" width="320" height="240" style="display: none;"></canvas>
    <div>
      <label>
        差异阈值: 
        <input  v-model="rate" min="0" max="1" step="0.01">
        {{ threshold }}
      </label>
    </div>
    <div v-if="capturedImage">
      <h3>捕获帧：</h3>
      <img :src="capturedImage" alt="关键帧" />
      <p>与前一帧的差异值: {{ lastDiffValue }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted,onBeforeUnmount, computed } from 'vue'
const cv = window.cv;
const videoRef = ref(null)
const canvasRef = ref(null)
const capturedImage = ref(null)
const vwidth=ref(320)
const vheight=ref(240)
const rate=ref(0.1)
const threshold = computed(()=>{
  return vwidth.value*vheight.value*rate.value
})// 默认差异阈值
console.log('阀值:',threshold.value)
const lastDiffValue = ref(0) // 记录最后一帧的差异值

let cap = null // OpenCV VideoCapture 对象
let streaming = false
let prevFrame = null // 存储前一帧用于比较
let cnt=1;
function startVideo() {
  navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
    videoRef.value.srcObject = stream
    videoRef.value.play()
    streaming = true
    cap = new cv.VideoCapture(videoRef.value)
  })
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
  cv.threshold(diff, thresholded, 10, 1, cv.THRESH_BINARY)

  // 计算差异值
  let diffValue = 0
  for (let i = 0; i < thresholded.data.length; i++) {
    diffValue += thresholded.data[i]
  }
  console.log('差异值:',diffValue)
  if(diffValue>threshold.value){
    capturedImage. value = canvasRef.value.toDataURL('image/png')
    lastDiffValue.value = diffValue
    console.log('捕获到关键帧:',cnt++)
  }
  // 更新前一帧
  src.copyTo(prevFrame)
  
  // 释放内存
  gray1.delete()
  gray2.delete()
  diff.delete()
  thresholded.delete()
  
  return diffValue
}

function captureFrame() {
  if (!cap) return

  const src = new cv.Mat(videoRef.value.height, videoRef.value.width, cv.CV_8UC4)
  cap.read(src)
  
  // 计算与前一帧的差异
  const diffValue = calculateFrameDiff(src)
  lastDiffValue.value = diffValue
  
  // 如果差异大于阈值，则认为是关键帧
  if (diffValue > threshold.value) {
    cv.imshow(canvasRef.value, src)
    capturedImage.value = canvasRef.value.toDataURL('image/png')
    console.log('捕获到关键帧',cnt++)
  } 
  
  src.delete()
}
let timerId=null
function startCaptureInterval() {
  // 每隔500ms执行一次captureFrame
  timerId = setInterval(() => {
    captureFrame()
  }, 500)
}

function stopCaptureInterval() {
  if (timerId) {
    clearInterval(timerId)
    timerId = null
  }
}

// 组件卸载时清理资源
onBeforeUnmount(() => {
  if (prevFrame) {
    prevFrame.delete()
  }
   stopCaptureInterval()
})
</script>

<style scoped>
video {
  border: 1px solid #ccc;
  margin-bottom: 10px;
}
img {
  border: 1px solid #333;
  max-width: 100%;
}
</style>