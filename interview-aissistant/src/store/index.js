// store/auth.js
import { defineStore } from 'pinia';
//测试使用
const init_resume = {
  "姓名": "李⼩画",
  "手机号": "13066668888",
  "邮箱": "cnsupport@canva.com",
  "性别": "⼥",
  "年龄": 22,
  "意向岗位": "web全栈开发",
  "学历信息": "2015年 - 2019年 华东师范⼤学",
  "专业": "软件⼯程",
  "实习经历": [
    {
      "公司": "可⽡科技公司",
      "职位": "java后端",
      "时间": "2015年9⽉ -2016年11⽉",
      "职责": "负责服务器维护"
    },
    {
      "公司": "可⽡信息公司",
      "职位": "前端开发",
      "时间": "2013年6⽉ - 2015年8⽉",
      "技能": "掌握了前端管理⽹⻚的基本⼯作流程"
    }
  ],
  "学术成就": [
    "第⼗届中国计算机设计⼤赛全国⼆等奖",
    "第五届中国软件杯A组全国⼀等奖",
    "“问⼼”笔记智能体、淘宝商城微信⼩程序、学术论⽂“魔镜”等七个⼤型项⽬"
  ],
  "技能": [
    "熟悉全栈开发流程，具备基础的专业知识",
    "良好的团队协作能⼒",
    "强⼤的⾃主学习能⼒",
    "扩充专业知识",
    "喜欢打篮球、看电影、打游戏"
  ],
  "自我评价": [
    "经验丰富：有丰富的知识体体系做基础，能够按部就班完成任务、查找代码bug",
    "团队合作：善于与他⼈合作，能够在团队中积极贡献并共同实现⽬标",
    "⾃我管理：具备良好的时间管理和⾃我组织能⼒，能够有效管理⼯作任务和⼯作压⼒"
  ]
}
const init_score = {
  '硬实力': [
    { value: 0, name: '专业知识' },
    { value: 0, name: '技术能力' },
    { value: 0, name: '经验积累' }
  ],
  '软实力': [
    { value: 0, name: '团队协作' },
    { value: 0, name: '表达能力' }
  ],
  '潜力': [
    { value: 0, name: '学习能力' },
    { value: 0, name: '创新能力' },
    { value: 0, name: '适应能力' }
  ],
  '文化水平': [
    { value: 0, name: '伦理抉择' },
    { value: 0, name: '价值观' }
  ],
  '外部指标': [
    { value: 0, name: '面试准备程度' },
    { value: 0, name: '专业度' },
    { value: 0, name: '精神风貌' },
    { value: 0, name: '行为举止' }
  ]
};
const init_weight1 = {
  '硬实力': 0.3,
  '软实力': 0.2,
  '潜力': 0.2,
  '文化水平': 0.1,
  '外部指标': 0.2
}
const init_weight2 = {
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
    { name: '面试准备程度', weight: '50%' },
    { name: '专业度', weight: '15%' },
    { name: '精神风貌', weight: '30%' },
    { name: '行为举止', weight: '5%' }
  ]
}
export const useStore = defineStore('auth', {
  state: () => ({
    isLoggedIn: false, // 表示用户是否处于登录状态
    userInfo: {
      username: '', // 用户名
      email: '', // 用户邮箱
      avatarSrc: '',// 用户头像的URL
      bio: '', // 用户简介''
    },
    //一次面试记录,仅保存部分内容
    interview: {
      score: init_score,
      total_score: 0,
      //resumefile: init_resume,//可能为文件对象，也可能是精炼内容
      resumefile: null,//可能为文件对象，也可能是精炼内容
      resume_type: 0,//0是文字json，1是文件
      // resume: init_resume,//通过各种文件形式整理得到的精炼文本
      // file_name:'my_resume.txt',
       resume:null ,//通过各种文件形式整理得到的精炼文本
      file_name:'my_resume.txt',
      resume_advice: [],
      advice: [],
      videoFile: null,//录像流
      urls: {},
      weight1: init_weight1,
      weight2: init_weight2,
      job:''
    }
  }),
  actions: {
    login() {
      this.isLoggedIn = true; // 设置为已登录
    },
    logout() {
      this.isLoggedIn = false; // 设置为未登录
    },
    getUser() {
      return this.userInfo;
    },
    setUser(userInfo) {
      this.userInfo.username = userInfo.username;
      this.userInfo.email = userInfo.email;
      this.userInfo.avatarSrc = userInfo.preference?.avatarSrc ?? '';
      this.userInfo.bio = userInfo.preference?.bio ?? '';
    },
    init_interview() {
      this.interview = {
        score: init_score,
        total_score: 0,
        resumefile: init_resume,//可能为文件对象，也可能是精炼内容
        resume_type: 0,
        resume: init_resume,//通过各种文件形式整理得到的精炼文本
        file_name:'my_resume.txt',
        resume_advice: [],
        advice: [],
        videoFile: null,//录像流
        urls: {},
        weight1: init_weight1,
        weight2: init_weight2,
        job:''
      }
    },
    init_score() {
      this.interview.score = init_score;
      this.interview.total_score = 0;
    },
    modify_score(tot=80) {
      if(tot>100)tot=100;
      this.interview.total_score = 0;
      //得出最高单向得分
      for (let item in this.interview.score) {
        let weight = parseFloat(this.interview.weight1[item]) / 100;
        let sum = this._sub_modify(item, this.interview.score[item],tot)
        this.interview.total_score += sum * weight;
      }
      this.interview.total_score = Math.round(this.interview.total_score * 100) / 100//保留两位小数
    },
    _sub_modify(name, iarray,tot) {
      let weight_array = this.interview.weight2[name]
      let ma = 0;
      let sum = 0;
      iarray.forEach(i => {
        ma = Math.max(ma, i.value);
      })
      let ratio = Math.min(1, tot / ma);
      iarray.forEach(i => {
        i.value *= ratio;
      })
      iarray.forEach(i => {
        ma = Math.max(ma, i.value);
        let sub_weight = parseFloat(weight_array.find(j => j.name == i.name).weight) / 100
        let kk=i.value
        kk *= sub_weight
        i.value = Math.round(i.value * 100) / 100
        sum += kk;
      })
      return sum;
    },
    // 私有方法 - 根据文件名判断文件类型
    _getFileType(filename) {
      const extension = filename.split('.').pop().toLowerCase();
      const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
      const audioTypes = ['mp3', 'wav', 'ogg'];
      const videoTypes = ['mp4', 'webm', 'mov'];

      if (imageTypes.includes(extension)) return 'images';
      if (audioTypes.includes(extension)) return 'audios';
      if (videoTypes.includes(extension)) return 'videos';
      return 'documents';
    }
  },
});
