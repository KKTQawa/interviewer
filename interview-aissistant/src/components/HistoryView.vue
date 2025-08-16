<template>
  <div class="main_container">
    <!-- 筛选区域 -->
    <div class="filter">
      <div class="fleft">
        <n-date-picker v-model:value="timestamp" type="date" placeholder="请选择日期" />
        <span>--至今</span>
      </div>
      <div class="fright">
        <n-cascader v-model:value="select_job" :options="jobOptions" placeholder="岗位" style="width: 200px" />
        <n-select v-model:value="select_mode" placeholder="模式" style="width: 120px; margin-left: 12px"
          :options="modeOptions" />
        <n-select v-model:value="select_sort" placeholder="排序方式" style="width: 120px; margin-left: 12px"
          :options="sortOptions" />
      </div>
    </div>

    <!-- 历史记录区域 -->
    <div class="history">
      <div class="history_item" v-for="(item, index) in sortAndFilter" :key="index">
        <div class="left">
          <div class="time">{{ item.time }}</div>
          <div class="score">分数：{{ item.score }}</div>
          <div class="mode">模式：{{ item.mode === 1 ? 'RealTime' : 'noRealTime' }}</div>
          <div class="job">岗位：{{ item.job }}</div>
        </div>
        <div class="right">
          <n-button text @click="showDetail(item)">查看</n-button>
          <a-popconfirm title="确认删除?" ok-text="是的" cancel-text="取消" @confirm="deleteHistory(item)"
            popup-class="custom-popconfirm">
            <template #icon><question-circle-outlined style="color: red" /></template>
            <a style="margin-left: 10px; text-decoration: none; color: inherit; cursor: pointer; "
              @mouseover="e => e.target.style.color = 'red'" @mouseleave="e => e.target.style.color = 'black'"
              href="#">删除</a>
          </a-popconfirm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed,onMounted } from 'vue'
import { useStore } from '../store'
import { NSelect, NDatePicker, NCascader } from 'naive-ui'
import { QuestionCircleOutlined } from '@ant-design/icons-vue'
import axios from "../utils/axios";
const store = useStore()
const props = defineProps({
  history: Array
})
// const history = props.history ? ref(props.history) : ref([
//   { id: 1, time: '2023-05-05 10:10', job: 'web前端开发', mode: 0, score: 91 },
//   { id: 2, time: '2023-05-06 10:10', job: 'web前端开发', mode: 1, score: 82 },
//   { id: 3, time: '2023-06-10 08:20', job: 'web前端开发', mode: 0, score: 73 },
//   { id: 4, time: '2023-07-01 15:00', job: '算法工程师', mode: 1, score: 95 },
//   { id: 5, time: '2023-05-05 10:10', job: 'web前端开发', mode: 0, score: 93 },
//   { id: 6, time: '2023-05-06 10:10', job: 'web全栈开发', mode: 1, score: 86 },
//   { id: 7, time: '2023-06-10 08:20', job: 'web前端开发', mode: 0, score: 77 },
//   { id: 8, time: '2023-07-01 15:00', job: '算法工程师', mode: 1, score: 95 },
//   { id: 9, time: '2023-05-05 10:10', job: 'UI/UX设计师', mode: 0, score: 94 },
//   { id: 10, time: '2023-05-06 10:10', job: '游戏开发', mode: 1, score: 87 },
//   { id: 11, time: '2023-06-10 08:20', job: '游戏开发', mode: 0, score: 70 },
//   { id: 12, time: '2023-07-01 15:00', job: '软件测试工程师', mode: 1, score: 95 },
// ])
const history = props.history ? ref(props.history) : ref([])
onMounted(async()=>{
  await getHistory()
})
const getHistory = async () => { 
  try {
    let uid = localStorage.getItem('id');
    const res = await axios.get('/history/get', {
      params: {
        user_id: uid 
      }
    });
    console.log('获取历史记录:',res.data); 
    history.value=[];
    res.data.history.forEach(item => {
      history.value.push({
        id: item.id,
        time: item.created_time,
        job: item.job,
        mode: item.mode,
        score: item.total_score
      })
    })
  } catch (error) {
    console.error('获取历史记录失败:', error);
  }
}
const select_mode = ref(-1)
const timestamp = ref(null)
const select_sort = ref(0)
const select_job = ref(-1)
const modeOptions = [
  { label: '全部', value: -1 },
  { label: 'noRealTime', value: 0 },
  { label: 'RealTime', value: 1 }
]
const sortOptions = [
  { label: '最近', value: 0 },
  { label: '最早', value: 1 },
  { label: '分数最高', value: 2 },
  { label: '分数最低', value: 3 }
]
const jobOptions = [
  {
    label: '全部',
    value: -1
  },
  {
    label: '开发类',
    value: '开发类',
    children: [
      { label: 'web前端开发', value: 'web前端开发' },
      { label: 'web后端开发', value: 'web后端开发' },
      { label: 'web全栈开发', value: 'web全栈开发' },
      { label: '嵌入式开发', value: '嵌入式开发' },
      { label: 'C++桌面开发', value: 'C++桌面开发' },
      { label: '移动端开发', value: '移动端开发' },
      { label: '游戏开发', value: '游戏开发' }
    ]
  },
  {
    label: '研究类',
    value: '研究类',
    children: [
      { label: '架构师', value: '架构师' }
    ]
  },
  {
    label: '技术类',
    value: '技术类',
    children: [
      { label: '算法工程师', value: '算法工程师' },
      { label: '数据分析与挖掘', value: '数据分析与挖掘' }
    ]
  },
  {
    label: '设计类',
    value: '设计类',
    children: [
      { label: 'UI/UX设计师', value: 'UI/UX设计师' },
      { label: '动画师', value: '动画师' }
    ]
  },
  {
    label: '测试类',
    value: '测试类',
    children: [
      { label: '软件测试工程师', value: '软件测试工程师' }
    ]
  }
]
const sortAndFilter = computed(() => {
  let filtered = [...history.value]

  // 过滤模式
  if (select_mode.value !== -1) {
    filtered = filtered.filter(item => item.mode === select_mode.value)
  }

  // 过滤时间
  if (timestamp.value) {
    const from = new Date(timestamp.value).getTime()
    filtered = filtered.filter(item => new Date(item.time).getTime() >= from)
  }
  //过滤岗位
  if (select_job.value && select_job.value !== -1) {
    //console.log(select_job.value)
    filtered = filtered.filter(item => item.job === select_job.value)
  }
  // 排序
  switch (select_sort.value) {
    case 0: // 最近,Date大的排在前面
      filtered.sort((a, b) => new Date(b.time) - new Date(a.time))
      break
    case 1: // 最早
      filtered.sort((a, b) => new Date(a.time) - new Date(b.time))
      break
    case 2: // 分数最高
      filtered.sort((a, b) => b.score - a.score)
      break
    case 3: // 分数最低
      filtered.sort((a, b) => a.score - b.score)
      break
  }

  return filtered
})
import { weight1Map, weight2Map } from "../utils/score.js";
const emits = defineEmits(['toReport'])
const report_data = ref({})
const showDetail = async (item) => {
  console.log('查看详情', item)
  try {
    const query = await axios.get("/history/query", {
      params: {//get方法，参数放在第二个
        id: item.id
      }
    });
    console.log('查询历史记录成功', query.data);
    let weight1 = weight1Map[query.data.job];
    let weight2 = weight2Map[query.data.job];
    report_data.value = {
      infos: query.data.advice,
      mode: query.data.mode,
      message: query.data.message,
      ...query.data.resource,
      score: query.data.score_detail,
      weight1: weight1,
      weight2: weight2,
    }
    emits('toReport', report_data.value)
  } catch (err) {
    console.log('查询历史记录失败', err);
    emits('toReport')
  }
}
const deleteHistory = (item) => {
  const id = item.id
  const index = history.value.findIndex(h => h.id === id)
  if (index !== -1) {
    history.value.splice(index, 1)
    console.log('删除记录：', item)
  } else {
    console.log('删除失败')
  }
}
</script>

<style scoped lang="scss">
.main_container {
  height: 100%;
  min-height:500px;
  width: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
  // background:
  //   radial-gradient(circle at center, rgba(255, 255, 255, 0.3), transparent 70%),
  //   /* 柔和阳光 */
  //   conic-gradient(from 45deg,
  //     #ff9a9e 0deg 90deg,
  //     /* 粉色 */
  //     #fad0c4 90deg 180deg,
  //     /* 淡橘 */
  //     #fbc2eb 180deg 270deg,
  //     /* 淡紫 */
  //     #a6c1ee 270deg 360deg
  //     /* 淡蓝 */
  //   );
     background-image: url('../assets/history.png');
  background-attachment: fixed;
  background-size: 100% 100%;
  background-repeat: no-repeat;
  box-sizing: border-box;
}

.filter {
  margin-bottom: 12px;
  background-color: rgba(255, 255, 255, 0.3);
  border: 2px solid #44d6e6;
  padding: 12px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;

  .fleft {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .fright {
    display: flex;
    align-items: center;
  }
}

.history {
  flex: 1;
  overflow-y: auto;
  background-color: rgba(255, 255, 255, 0);
  border-radius: 8px;
  padding: 0px;
  border: 2px solid #44d6e6;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.1);

  &:hover::-webkit-scrollbar-thumb {
    background-color: rgb(239, 11, 11);
  }

  /* 滚动条样式 */
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-thumb {
    background-color: rgba(218, 180, 9, 0);
    border-radius: 4px;
  }

  &::-webkit-scrollbar-track {
    background-color: transparent;
  }
}

.history_item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin-bottom: 1px;
  background-color: #f9f9f93c;
  border-radius: 8px;
  transition: background-color 0.2s ease;
  border: 1px dashed #9cd4da;

  &:hover {
    background-color: #566b6913;
  }

  .left {
    display: flex;
    flex-direction: row;
    gap: 30px;

    .time {
      font-weight: bold;
      margin-bottom: 4px;
    }

    .score,
    .mode,
    .job {
      font-size: 14px;
      
    }

    .score {
      width: 60px;
      color:#ff0303;
    }

    .mode {
      width: 120px;
      color:#0357ff;
    }

    .job {
      color: #fa0404;
      width: 200px;
    }
  }

  .right {
    .n-button {
      opacity: 0.6;

      &:hover {
        opacity: 1;
      }
    }
  }
}
</style>
