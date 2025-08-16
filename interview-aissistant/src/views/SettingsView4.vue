<template>
    <div class="main_content">
        <Graph :level2Data="test" :weight1="weight1" :weight2="weight2"/>
    </div>
</template>
<script lang="ts" setup>
// Install the assemblyai package by executing the command "npm install assemblyai"

import { AssemblyAI } from "assemblyai";
import axios from "../utils/axios";
import Graph from '../components/Graph.vue'
const test={
  '硬实力': [
    { value: 35, name: '专业知识' },
    { value: 67, name: '技术能力' },
    { value: 43, name: '经验积累' }
  ],
  '软实力': [
    { value: 23, name: '团队协作' },
    { value: 23, name: '表达能力' }
  ],
  '潜力': [
    { value: 22, name: '学习能力' },
    { value: 77, name: '创新能力' },
    { value: 88, name: '适应能力' }
  ],
  '文化水平': [
    { value: 98, name: '伦理抉择' },
    { value: 67, name: '价值观' }
  ],
  '外部指标': [
    {value:25,name:'面试准备程度'},
    {value:25,name:'专业度'},
    { value: 25, name: '精神风貌' },
    { value:25, name: '行为举止' }
  ]
}
const weight1={
  '硬实力':'30%',
  '软实力':'30%',
  '潜力':'5%',
  '文化水平':'5%',
  '外部指标':'30%'
}
const weight2 = {
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
const client = new AssemblyAI({
  apiKey: "d7cc834da51e4a1e99704ed095012acb",
});

// const audioFile = "./local_file.mp3";
const audioFile = 'https://assembly.ai/wildfires.mp3'

const params = {
  audio: audioFile,
  speech_model: "universal",

};

const run = async () => {
  const transcript = await client.transcripts.transcribe(params);

  console.log(transcript);
};
const run1 = async () => {
  try{
    const voice_res = await axios.get('/interview/voice_mark');
     console.log('语言分析完成:', voice_res.data);
  }
  catch(error){
    console.log(error);
  }
 
}
</script>
<style lang="scss" scoped>
.main_content {
    width: 100%;
    height: 100%;
    position:relative;
}
</style>