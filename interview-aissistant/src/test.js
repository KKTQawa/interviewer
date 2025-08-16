 
 let score={
  '硬实力': [
    { value: 212, name: '专业知识' },
    { value: 101, name: '技术能力' },
    { value: 54, name: '经验积累' }
  ],
  '软实力': [
    { value: 345, name: '团队协作' },
    { value: 120, name: '表达能力' }
  ],
  '潜力': [
    { value: 351, name: '学习能力' },
    { value: 56, name: '创新能力' },
    { value: 97, name: '适应能力' }
  ],
  '文化水平': [
    { value: 135, name: '伦理抉择' },
    { value: 155, name: '价值观' }
  ],
  '外部指标': [
    {value:551,name:'面试准备程度'},
    {value:70,name:'专业度'},
    { value: 90, name: '精神风貌' },
    { value: 121, name: '行为举止' }
  ]
};
 
 let vweight1={
  '硬实力':'30%',
  '软实力':'30%',
  '潜力':'20%',
  '文化水平':'10%',
  '外部指标':'10%'
}
let vweight2 ={
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
 let total_score=0
function modify_score() {
      //得出最高单向得分
      for (let item in score) {
        let weight = parseFloat(vweight1[item]) / 100;
        let sum = _sub_modify(item, score[item])
        total_score += sum * weight;
      }
    }
   function _sub_modify(name, iarray) {
      let weight_array = vweight2[name]
      let ma = 0;
      let sum = 0;
      iarray.forEach(i => {
        ma = Math.max(ma, i.value);
      })
      let ratio = Math.min(1, 100/ma);
      iarray.forEach(i => {
        i.value *= ratio;
      })
      iarray.forEach(i => {
        let sub_weight = parseFloat(weight_array.find(j => j.name == i.name).weight) / 100
        i.value *= sub_weight
        i.value=Math.round(i.value*100)/100
        sum += i.value;
      })
      console.log('ma',name,ma)
      console.log(name,sum)
      return sum;
    }
modify_score()
console.log('score',score)
console.log('total_score',total_score)