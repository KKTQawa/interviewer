
import json

kkk="""
{
  "硬实力": [
    {"value": 70, "name": "专业知识"},
    {"value": 65, "name": "技术能力"},
    {"value": 60, "name": "经验积累"}
  ],
  "软实力": [
    {"value": 50, "name": "团队协作"},
    {"value": 55, "name": "表达能力"}
  ],
  "潜力": [
    {"value": 60, "name": "学习能力"},
    {"value": 40, "name": "创新能力"},
    {"value": 50, "name": "适应能力"}
  ],
  "文化水平": [
    {"value": 0, "name": "伦理抉择"},
    {"value": 0, "name": "价值观"}
  ],
  "外部指标": [
    {"value": 50, "name": "面试准备程度"},
    {"value": 60, "name": "专业度"}
  ]
}
```

建议:["1.联系方式疑似错误(邮箱格式不符合常规)", "2.教育经历中学校名称'asdfas'无法识别", "3.工作经历HTML标签未闭合存在格式风险", "4.研究/奖项内容过于简略缺乏细节", "5.年龄23岁与全栈开发岗位经验可能存在匹配度疑问"]

"""
def parse_i_chat(x):
    try:
        resume_begin = x.find("{")
        resume_end = x.rfind("}")
        #print("评分内容:", x[resume_begin:resume_end + 1])
        score = json.loads(x[resume_begin:resume_end + 1])
        #print("jjj")
        xx=x[resume_end:]
        #print("xx:",xx)
        suggest_begin = xx.rfind("[")
        suggest_end = xx.rfind("]")
        if suggest_begin!=-1 and suggest_end!=-1:
            suggest = json.loads(xx[suggest_begin:suggest_end + 1])
        else:
            suggest=[]

    except Exception as e:
        print("解析失败:", e)
        score = {}
        suggest = []
    return score, suggest
if __name__ == "__main__":
    print(parse_i_chat(kkk))