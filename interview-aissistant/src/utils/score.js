export const jobTypeOptions = [
  { value: 'development', label: '开发岗' },
  { value: 'research', label: '研发岗' },
  { value: 'technical', label: '技术岗' },
  { value: 'design', label: '设计岗' },
  { value: 'testing', label: '测试岗' }
]

export const jobsOptions = {
  development: [
    { value: 'web前端开发', label: 'web前端开发' },
    { value: 'web后端开发', label: 'web后端开发' },
    { value: 'web全栈开发', label: 'web全栈开发' },
    { value: '嵌入式开发', label: '嵌入式开发' },
    { value: 'C++桌面开发', label: 'C++桌面开发' },
    { value: '移动端开发', label: '移动端开发' },
    { value: '游戏开发', label: '游戏开发' }
  ],
  research: [
    { value: '架构师', label: '架构师' }
  ],
  technical: [
    { value: '算法工程师', label: '算法工程师' },
    { value: '数据分析与挖掘', label: '数据分析与挖掘' }
  ],
  design: [
    { value: 'UI/UX设计师', label: 'UI/UX设计师' },
    { value: '动画师', label: '动画师' }
  ],
  testing: [
    { value: '软件测试工程师', label: '软件测试工程师' },
  ]
}
export const weight1Map = {
  'web前端开发': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }, 'web后端开发': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }, 'web全栈开发': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }, '嵌入式开发': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }, 'C++桌面开发': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }, '移动端开发': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }, '游戏开发': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }, '架构师': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }, '算法工程师': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }, '数据分析与挖掘': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }, 'UI/UX设计师': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }, '动画师': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }, '软件测试工程师': {
    '硬实力': '30%',
    '软实力': '30%',
    '潜力': '20%',
    '文化水平': '10%',
    '外部指标': '10%'
  }
}
export const weight2Map = {
  'web前端开发': {
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
  }, 'web后端开发': {
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
  }, 'web全栈开发': {
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
  }, '移动端开发': {
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
  }, '游戏开发': {
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
  }, '嵌入式开发': {
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
  }, 'C++桌面开发': {
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
  }, '架构师': {
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
  }, '算法工程师': {
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
  }, '数据分析与挖掘': {
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
  }, 'UI/UX设计师': {
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
  }, '动画师': {
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
  }, '软件测试工程师': {
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
}
export const interview_init_score = {
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
    { value: 90, name: '伦理抉择' },
    { value: 90, name: '价值观' }
  ],
  '外部指标': [
    { value: 0, name: '面试准备程度' },
    { value: 0, name: '专业度' },
    { value: 90, name: '精神风貌' },
    { value: 90, name: '行为举止' }
  ]
};
