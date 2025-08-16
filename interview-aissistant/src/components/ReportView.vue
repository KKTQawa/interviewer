<template>
  <div class="exits" v-if="props.enter === 0" @click="exits">
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.7; cursor:pointer;">
      <polyline points="15 18 9 12 15 6"></polyline>
    </svg>
  </div>
  <div class="main-content" :class="{ 'noenter': props.enter === 0 }">
    <div class="result">
      <Graph class="graph" :level2Data="props.reportData?.score ?? null" :weight1="props.reportData?.weight1"
        :weight2="props.reportData?.weight2" />
      <div class="infos">
        <transition-group name="fade" tag="div">
          <div class="info-item" v-if="infos.length > 0" v-for="(item, index) in infos" :key="index">{{ item }}</div>
          <n-empty size="huge" description="面试官无建议" v-else style="
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
   --n-icon-color:red"></n-empty>
        </transition-group>
      </div>
    </div>
    <div class="review">
      <div class="rleft">
        <div class="chat_area">
          <div v-if="messages.length > 0" v-for="(message, index) in messages" :key="index" :class="[
            'message',
            message.type,
            { real: props.enter === 2, noreal: props.enter === 1, nono: props.enter === 0 }
          ]">
            <div class="message-content">{{ message.content }}</div>
          </div>
          <n-empty v-else size="huge" description="暂无对话历史" style="
    position: relative;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    --n-icon-color:red"></n-empty>
          " />
        </div>
      </div>
      <div class="rright">
        <div class="ibtn">
          <n-tooltip trigger:hover>
            <template #trigger>
              <span style="background-color:#FA8072" v-if="mode === 1" @click="showvideo">
                <videoIcon />
              </span>
              <span style="background-color:#FA8072" v-else>
                <novideoIcon />
              </span>
            </template>
            回放录像
          </n-tooltip>
          <n-tooltip trigger:hover>
            <template #trigger>
              <span style="background-color:#B0E0E6" @click="showaudio">
                <audioIcon />
              </span>
            </template>
            回放录音
          </n-tooltip>
        </div>
        <div class="ibtn">
          <n-tooltip trigger:hover>
            <template #trigger>
              <span style="background-color:#98FB98" @click="showresume">
                <resumeIcon />
              </span>
            </template>
            查看简历
          </n-tooltip>
          <n-tooltip trigger:hover>
            <template #trigger>
              <span style="background-color:#FFDAB9" @click="toprofile">
                <ProfileIcon />
              </span>
            </template>
            个人中心
          </n-tooltip>
        </div>
      </div>
    </div>
    <div class="avreview">
      <div class="video-review">
        <video v-if="showV" id="plyr-video" controls playsinline :poster="posterUrl">
          <source :src="videoUrl" type="video/mp4" />
        </video>
        <n-empty v-if="!showV" size="huge" description="暂无" />
        <button v-if="showV" @click="() => download(videoUrl)">下载</button>
      </div>
      <div class="audio-review">
        <div id="waveform" v-show="showa"></div>
        <n-empty size="huge" description="暂无" v-show="!showa" style="
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    " />
        <div class="audio-controls" v-if="showa">
          <button @click="toggleAudioPlay">播放 / 暂停</button>
          <button v-if="showa" id="downloadV" @click="() => download(audioUrl)">下载</button>
        </div>
      </div>
    </div>
  </div>
  <n-drawer v-model:show="nactive" :width="502">
    <n-drawer-content title="在线预览" closable :native-scrollbar="false">
      <!-- 操作按钮区域 -->
      <div class="ndrawer">
        <a :href="googleViewUrl" target="_blank" class="drawer-btn">在新窗口中打开</a>
        <a :href="textUrl" download class="drawer-btn">下载</a>
      </div>

      <!-- 预览区域 -->
      <div>
        <iframe :src="googleViewUrl" width="100%" height="600px" style="border: none;"></iframe>
      </div>
    </n-drawer-content>
  </n-drawer>
</template>
<script setup>
import { ref, onMounted, nextTick } from 'vue'
import Graph from '../components/Graph.vue';
import { NTooltip, NEmpty, NDrawer, NDrawerContent } from 'naive-ui'
import {
  PlayOutline as videoIcon,
  CloseCircleOutline as novideoIcon,
  MicOutline as audioIcon,
  DocumentTextOutline as resumeIcon,
  PersonCircleOutline as ProfileIcon
} from '@vicons/ionicons5';
const props = defineProps({
  reportData: Object,
  enter: {
    type: Number,
    default: 0
  }
})
console.log('传入子组件:', props.reportData)
import { useRouter } from 'vue-router';
import router from '../router';
import { useStore } from '../store'
import { message } from 'ant-design-vue'
const store = useStore();

// const infos = props.reportData?.infos ? ref(props.reportData.infos) :
//   ref(['yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes', 'yes'])
const infos = props.reportData?.infos ? ref(props.reportData.infos) : ref([])


const mode = props.reportData?.mode ? ref(props.reportData.mode) : ref(1)
const emits = defineEmits(['toHistory'])
const exits = () => {
  emits('toHistory')
}
// const messages = props.reportData?.message ? ref(props.reportData.message) : ref(
//   [{ type: 'user', content: '开始' },
//   { type: 'assistant', content: '好的' },
//   { type: 'user', content: '加我诶附件哦我IE合格佛' },
//   { type: 'assistant', content: '都发了我就发个哦让我i和光' },
//   { type: 'user', content: '阿胶哦覅我和哦i' },
//   { type: 'assistant', content: '打飞机另外IE放假哦i未付合计哦UI和叫哦发' },
//   { type: 'user', content: '开始' },
//   { type: 'assistant', content: '好的' },
//   { type: 'user', content: '加我诶附件哦我IE合格佛' },
//   { type: 'assistant', content: '都发了我就发个哦让我i和光' },
//   { type: 'user', content: '阿胶哦覅我和哦i' },
//   { type: 'assistant', content: '打飞机另外IE放假哦i未付合计哦UI和叫哦发' }
//   ]);
const messages = props.reportData?.message ? ref(props.reportData.message) : ref([])
import WaveSurfer from 'wavesurfer.js'
import 'plyr/dist/plyr.css'
import Plyr from 'plyr'

// const videoUrl = props.reportData?.videoUrl ? ref(props.reportData.videoUrl) : ref('https://interviewresource.oss-cn-beijing.aliyuncs.com/video/9_demo2-video.mp4')
// const audioUrl = props.reportData?.audioUrl ? ref(props.reportData.audioUrl) : ref('https://interviewresource.oss-cn-beijing.aliyuncs.com/audio/9_tmp1.wav')
// const textUrl = props.reportData?.textUrl ? ref(props.reportData.textUrl) : ref('https://interviewresource.oss-cn-beijing.aliyuncs.com/document/9_%E3%80%8A%E7%BC%96%E7%A8%8B%E7%BB%BC%E5%90%88%E5%AE%9E%E8%B7%B5%E3%80%8B%E5%B0%8F%E7%BB%84%E9%A1%B9%E7%9B%AE%E6%8A%A5%E5%91%8A%E4%B9%A6-%E6%99%BA%E8%83%BD%E9%80%89%E8%AF%BE%E7%B3%BB%E7%BB%9F-10245102512-10245102403.docx')
const videoUrl = props.reportData?.videoUrl ? ref(props.reportData.videoUrl) : ref('')
const audioUrl = props.reportData?.audioUrl ? ref(props.reportData.audioUrl) : ref('')
const textUrl = props.reportData?.textUrl ? ref(props.reportData.textUrl) : ref('')

const posterUrl = '../assets/flag.png' // 封面图（可选）

const googlefileUrl = textUrl.value
const msfileUrl = textUrl.value
const googleViewUrl = `https://docs.google.com/gview?url=${encodeURIComponent(googlefileUrl)}&embedded=true`
const msViewUrl = `https://view.officeapps.live.com/op/view.aspx?src=${encodeURIComponent(msfileUrl)}`

const showV = ref(false)
const showa = ref(false)
let wavesurfer = null
const toggleAudioPlay = () => {
  if (wavesurfer) {
    wavesurfer.playPause()
  }
}
onMounted(() => {
  // 初始化 Wavesurfer.js
  wavesurfer = WaveSurfer.create({
    container: '#waveform',       // 指定波形图渲染的 DOM 元素容器（通过选择器）
    waveColor: '#ff0000',            // 音频波形的基本颜色（未播放部分）
    progressColor: '#44d6e6',     // 音频波形中已播放部分的颜色
    height: 180,                  // 波形图的高度（单位：像素）
    barWidth: 2,                  // 每根波形柱的宽度，单位像素（越小越细，越大越粗）
    responsive: true              // 是否根据容器大小自动调整宽度（响应式）
  })
})
let ppl = null
const showvideo = async () => {
  if (showV.value) {
    showV.value = false
    if (ppl) {
      ppl.destroy(); // 销毁播放器实例
      ppl = null;    // 清除引用
    }
  } else {
    showV.value = true
    await nextTick()
    ppl = new Plyr('#plyr-video', {
      controls: [
        'play',
        'progress',
        'current-time',
        'duration',
        'mute',
        'volume',
        'captions',
        'settings',
        'fullscreen',
      ],
      settings: ['quality', 'speed', 'loop'],
      speed: { selected: 1, options: [0.5, 1, 1.5, 2] },
    })
  }
}
const showaudio = () => {
  if (showa.value) {
    wavesurfer.empty()
    showa.value = false
  } else {
    showa.value = true
    wavesurfer.load(audioUrl.value)
  }
}
const download = (target) => {
  const link = document.createElement('a');
  link.href = target;

  // 提取原始文件名，例如 https://example.com/path/audio.mp3 -> audio.mp3
  // console.log(target)
  const filename = target.split('/').pop().split('?')[0]; // 也剥离 query 参数
  link.download = filename;

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
const nactive = ref(false)
const showresume = () => {
  nactive.value = true
}
const toprofile = () => {
  if (props.enter && props.enter === 1) {
    message.info('您还在面试中，请勿操作')
  } else {
    router.push({
      path: '/myProfile',
    })
  }
}

</script>
<style scoped lang="scss">
.noenter {
  background-image: url('../assets/report.png');
  background-attachment: fixed;
  background-size: 100% 100%;
  background-repeat: no-repeat;
}

.main-content {
  height: 100%;
  width: 100%;
  min-width: 400px;
  min-height: 300px;
  position: absolute;
  overflow-y: auto;
  padding: 5px;
  background-color: rgba(250, 235, 215, 0); //默认无背景图、透明

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

  .result {
    position: relative;
    height: 500px;
    width: 100%;
    display: flex;
    gap: 5px;
    margin: 0px;
    padding: 0px;
    background-color: rgba(250, 235, 215, 0);
    box-sizing: border-box; // ✅ 防止 padding 计算额外宽度

    .graph {
      border: 2px solid rgb(22, 172, 172);
      border-radius: 8px;
      height: 100%;
      flex: 1;

    }

    .infos {
      height: 100%;
      width: 30%;
      position: relative;
      font-size: 16px;
      color: rgb(238, 40, 5);
      background: linear-gradient(rgba(221, 215, 158, 0.448), rgb(45, 191, 98));
      //background-color: rgba(243, 228, 24, 0.536); // 几乎透明
      border: 1px solid rgb(31, 99, 15); // 类似激光轮廓
      box-shadow:
        0 0 5px rgba(197, 189, 115, 0.3),
        0 0 10px rgba(189, 173, 95, 0.2) inset;
      border-radius: 8px;
      overflow-y: auto;
      padding: 0px;

      &::-webkit-scrollbar {
        width: 6px;
      }

      &::-webkit-scrollbar-track {
        background: transparent;
      }

      &::-webkit-scrollbar-thumb {
        background-color: rgb(232, 10, 10);
        border-radius: 3px;
      }

      .info-item {
        padding: 10px;
        width: 100%;
        border-bottom: 1px solid #295907;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 3px;
        padding: 2px 0px;
        border-radius: 6px;
        font-size: 16px;
        animation: fadeIn 0.3s ease-in-out;
      }
    }
  }

  .review {
    height: 500px;
    width: 100%;
    gap: 4px;
    display: flex;
    margin-top: 5px;
    padding: 1px;
    background-color: rgba(250, 235, 215, 0);

    .rleft {
      width: 70%;
      height: 100%;
      border: 1px solid rgb(22, 172, 172);
    }

    .rright {
      width: 28%;
      height: 100%;
      border: 1px solid rgb(22, 172, 172);
      padding: 2px;
      box-sizing: border-box;

      .ibtn {
        aspect-ratio: 2 / 1;
        width: 100%;
        display: flex;
        gap: 3px;
        margin-bottom: 1px;
        align-items: center;
        justify-content: center;

        span {
          height: 100%;
          width: 48%;
        }

        span:hover {
          transform: scale(1.1); // 放大
          transition: transform 0.3s; // 添加过渡动画（时间0.3秒）
        }
      }
    }
  }

  .avreview {
    width: 100%;
    height: 400px;
    display: flex;
    gap: 5px;
    margin-top: 5px;
    padding: 1px;
    background-color: rgba(250, 235, 215, 0);

    .video-review {
      height: 100%;
      width: 60%;
      background:
        radial-gradient(circle at top left, rgba(148, 217, 158, 0.3), transparent 40%),
        radial-gradient(circle at top right, rgba(148, 217, 158, 0.3), transparent 40%),
        radial-gradient(circle at bottom left, rgba(148, 217, 158, 0.3), transparent 40%),
        radial-gradient(circle at bottom right, rgba(148, 217, 158, 0.3), transparent 40%);
      border: 1px solid rgb(22, 172, 172);
      backdrop-filter: blur(8px);
      border-radius: 8px;
      display: flex;
      justify-content: center;
      /* 水平居中 */
      align-items: center;

      /* 垂直居中 */
      #plyr-video {
        width: 90%;
        max-width: 800px;
        height: 280px;
      }

      button {
        position: absolute;
        right: 5px;
        bottom: 5px;
        width: 20%;
        height: 30px;
        background-color: #44d6e6;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;

        &:hover {
          background-color: #28b6c0;
        }
      }
    }

    .audio-review {
      width: 38%;
      height: 100%;
      border: 1px solid rgb(22, 172, 172);
      padding: 5px;
      display: flex;
      align-items: center;
      flex-direction: column;
      /* 👈 加上这行 */
      position: relative;
      background:
        radial-gradient(circle at top left, rgba(148, 217, 158, 0.3), transparent 40%),
        radial-gradient(circle at top right, rgba(148, 217, 158, 0.3), transparent 40%),
        radial-gradient(circle at bottom left, rgba(148, 217, 158, 0.3), transparent 40%),
        radial-gradient(circle at bottom right, rgba(91, 215, 116, 0.3), transparent 50%);

      #waveform {
        width: 100%;
        height: 200px;
        background: linear-gradient(45deg, rgba(125, 130, 98, 0.1), rgba(105, 222, 99, 0.903), rgba(125, 130, 98, 0.1));
        backdrop-filter: blur(8px);
        border-radius: 8px;
      }

      .audio-controls {
        margin-top: 20px;
        height: 50px;
        width: 100%;
        display: flex;
      }

      button {
        flex: 1;
        width: 30%;
        height: 40px;
        background-color: #44d6e6;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;

        &:hover {
          background-color: #28b6c0;
        }
      }

    }
  }
}

.exits {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10000;

  &:hover {
    opacity: 1;
    /* 鼠标悬停时更明显 */
  }
}

.chat_area {
  height: 100%;
  width: 100%;
  flex: 1;
  padding: 20px;
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



      border-bottom-right-radius: 4px;
    }

    &.assistant {
      align-self: flex-start;



      border-bottom-left-radius: 4px;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }

  }

  .real {
    &.user {
      color: rgba(255, 255, 255, 0.955);
      background-color: rgba(255, 194, 72, 0.966);
    }

    &.assistant {
      color: rgba(255, 255, 255, 0.955);
      background-color: rgba(255, 194, 72, 0.966);
    }
  }

  .noreal {
    &.user {
      color: rgb(255, 255, 255);
      background-color: rgba(13, 162, 231, 0.374);
    }

    &.assistant {
      background-color: rgba(13, 162, 231, 0.374);

      color: rgb(104, 255, 3);
    }
  }

  .nono {
    &.user {
      color: rgba(255, 45, 3, 0.955);
      backdrop-filter: blur(30px);
      background-color: rgba(201, 202, 168, 0.374);
    }

    &.assistant {
      background-color: rgba(201, 202, 168, 0.374);
      backdrop-filter: blur(30px);
      color: rgba(189, 6, 244, 0.955);
    }
  }
}

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

::v-deep(.infos .n-empty__description) {
  color: red;
  /* 描述文字颜色 */
}

::v-deep(.rleft .n-empty__description) {
  color: red;
  /* 描述文字颜色 */
}

.ndrawer {
  display: flex;
  justify-content: center;
  /* 整体水平居中 */
  gap: 20px;
  /* 按钮之间的间距 */
  margin: 10px auto; //依次为上右下左
}

.drawer-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 30px;
  width: 120px;
  margin-bottom: 10px;
  background-color: #1ad2dfe6;
  border: 1px solid rgb(28, 224, 234);
  color: rgb(20, 21, 19);
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  transition: background-color 0.3s;
}

.drawer-btn:hover {
  color: rgb(247, 4, 4);
  border-color: rgb(240, 12, 12);
}
</style>