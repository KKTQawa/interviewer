<template>
  <div class="main-content">
    <input type="file" @change="handleFileChange"  />
    <button @click="upload">上传</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from "../utils/axios";
import{NButton} from "naive-ui";
import {message} from 'ant-design-vue'
const score_detail= {
  '硬实力': [
    { value: 88, name: '专业知识' },
    { value: 67, name: '技术能力' },
    { value: 87, name: '经验积累' }
  ],
  '软实力': [
    { value: 54, name: '团队协作' },
    { value: 98, name: '表达能力' }
  ],
  '潜力': [
    { value: 35, name: '学习能力' },
    { value: 56, name: '创新能力' },
    { value: 97, name: '适应能力' }
  ],
  '文化水平': [
    { value: 35, name: '伦理抉择' },
    { value: 55, name: '价值观' }
  ],
  '外部指标': [
    {value:55,name:'面试准备程度'},
    {value:70,name:'专业度'},
    { value: 50, name: '精神风貌' },
    { value: 48, name: '行为举止' }
  ]
};
let weight1={
  '硬实力':'30%',
  '软实力':'30%',
  '潜力':'20%',
  '文化水平':'10%',
  '外部指标':'10%'
}
let weight2 ={
  '硬实力': [
    { name: '专业知识', weight: '35%' },
    { name: '技术能力', weight: '35%' },
    { name: '经验积累', weight: '30%' }
  ],
  '软实力': [
    { name: '表达能力', weight: '40%' },
    { name: '团队协作', weight: '60%' },
  ],
  '潜力': [
    { name: '学习能力', weight: '40%' },
    { name: '创新能力', weight: '35%' },
    { name: '适应能力', weight: '25%' }
  ],
  '文化水平': [
    { name: '伦理抉择', weight: '70%' },
    { name: '价值观', weight: '30%' }
  ],
  '外部指标': [
        {name:'面试准备程度',weight:'50%'},
    {name:'专业度',weight:'15%'},
    { name: '精神风貌',weight: '30%' },
    { name: '行为举止',weight: '5%' }
  ]
}
let totalScore = 0
let level1Data = ['硬实力', '软实力', '潜力', '文化水平', '外部指标'].map(category => {
  const item = score_detail[category] || [];
  let sum = 0;
  item.forEach(subItem => {
    //console.log('subItem:', subItem)
    let tt = weight2[category].find(item => item.name === subItem.name)
    //console.log('tt:',tt)
    const weight = parseFloat(tt.weight) / 100
    sum += subItem.value * weight
  })
  return {
    name: category,
    weight: weight1[category],
    value: sum
  };
});
level1Data.forEach(item => {
  totalScore += item.value * parseFloat(weight1[item.name]) / 100;
})
let rounded = Math.round(totalScore * 100) / 100; // 3.14 (数字)
totalScore = rounded;
console.log('加权分数:', totalScore)

const messages =ref(
  [{ type: 'user', content: '开始' },
  { type: 'assistant', content: '好的' },
  { type: 'user', content: '加我诶附件哦我IE合格佛' },
  { type: 'assistant', content: '都发了我就发个哦让我i和光' },
  { type: 'user', content: '阿胶哦覅我和哦i' },
  { type: 'assistant', content: '打飞机另外IE放假哦i未付合计哦UI和叫哦发' },
  { type: 'user', content: '开始' },
  { type: 'assistant', content: '好的' },
  { type: 'user', content: '加我诶附件哦我IE合格佛' },
  { type: 'assistant', content: '都发了我就发个哦让我i和光' },
  { type: 'user', content: '阿胶哦覅我和哦i' },
  { type: 'assistant', content: '打飞机另外IE放假哦i未付合计哦UI和叫哦发' }
  ]);
const infos =ref([
  '1.建议说话声大一点',
  '2.面试请专注',
  '3.建议加强专业知识的积累',
  '4.建议多做项目',
  '5.建议多和人打交道',
  '6.请注意举止'
])

const history={
  user_id:localStorage.getItem("id"),
    mode:1,
    resource:{
      videoUrl:'https://interviewresource.oss-cn-beijing.aliyuncs.com/video/demo2-video.mp4',
      audioUrl:'https://interviewresource.oss-cn-beijing.aliyuncs.com/audio/tmp1.wav',
      textUrl:'https://interviewresource.oss-cn-beijing.aliyuncs.com/document/%E3%80%8A%E7%BC%96%E7%A8%8B%E7%BB%BC%E5%90%88%E5%AE%9E%E8%B7%B5%E3%80%8B%E5%B0%8F%E7%BB%84%E9%A1%B9%E7%9B%AE%E6%8A%A5%E5%91%8A%E4%B9%A6-%E6%99%BA%E8%83%BD%E9%80%89%E8%AF%BE%E7%B3%BB%E7%BB%9F-10245102512-10245102403.docx'
    },
    total_score:totalScore,
    score_detail:score_detail,
    message:messages.value,
    advice:infos.value
}
const query_history=async()=>{
  try{
    const res=await axios.get("/history/query",{params:{//get方法，参数放在第二个
      id:3
    }});
    console.log(res.data);
  }catch(err){
    console.log(err);
  }
}
const delete_history=async()=>{
  try{
    const res=await axios.post("/history/delete",{},{params:{//post方法，参数放在第三个，body放在第二个
      id:4
    }});
    console.log('删除成功',res.data);
  }catch(err){
    console.log('删除失败',err);
  }
}
const save_history=async()=>{
  console.log('history:',history)
  try{
    const res=await axios.post("/history/save",history);
    console.log('保存成功',res.data);
  }catch(err){
    console.log('保存失败',err);
  }
}
const file=ref(null);
const uid=localStorage.getItem("id");
const handleFileChange = (event) => {
  const selectedFile = event.target.files[0]
  file.value = selectedFile
}
const upload = async () => {
  const formData = new FormData();
  formData.append("file", file.value);
  formData.append("user_id", uid);
  try {
    const res = await axios.post("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
     message.success('上传成功！')
    console.log('上传成功', res.data);
  } catch (err) {
    console.log('上传失败', err);
  }
}
</script>

<style scoped lang="scss">
.main-content {
  height: 100%;
  width: 100%;
}

</style>
