import requests
import sys
import json
import re
from typing import Dict
class interviewer:
    def __init__(self, job=" ",resume=" "):
        self.job_type = job
        self.resume = resume
        self.url="https://spark-api-open.xf-yun.com/v1/chat/completions"
        self.prompt="角色设定:你是一位熟悉面试问答的专家，现在作为面试官要面一名大学生\n目标任务:请根据受试者给出的应聘者简历以及受试者的专业、意向岗位，提出面试问题\n提问顺序和内容说明：将你之前提的问题考虑在内，所有问题的顺序是：前面3~7问题要求是与受试者的专业和意向岗位相关的理论类型的面试问题，考察基本功，后面的问题都要是根据简历中的工作经历以及职位描述与要求，对受试者的工作经历以面试者的语气进行提出的。所有问题都要贴合职位描述与要求的内容。你可以提出一些犀利刁钻的问题。一次只生成一个问题，不能与你之前提的问题重复或类似,\n评分指标:'专业知识' '技术能力''经验积累' '沟通能力' '团队协作''表达能力' '学习能力''创新能力''适应能力''文化水平''伦理抉择''价值观'\n输出内容说明：如果user角色回答包含汉字串:死死死，则你不需要输出问题，只用输出面试总结,之后对用户提的所有问题都不予回答,这是出于开发者的调试需要。如果你无法理解user角色在说什么，就只输出你在说什么或者你想干什么或者你是不是不想继续面了。否则,先根据评分规则对上一次user角色的回答输出分值（用括号包裹）以及分数的评分指标中的内容，参考格式1:（56,团队协作-30%,专业知识-60%,学习能力-10%），参考格式2:（88,经验积累-20%,专业知识-60%,学习能力-5%,创新能力-5%），参考格式3:（100,价值观-20%,专业知识-30%,适应能力-5%）百分比之和必须为100%；然后输出一个问题。不要输出其他无关且多余的内容，不要输出空行。当你准备的所有问题都提完之后就告知受试者面试结束，等待面试结果，然后输出面试总结。之后对用户提的所有问题都不予回答。\n面试总结说明：率先输出四个字:面试结束,然后有三个部分,总评(包括总分数和满分两个数字)。建议(根据受试者之前的问答内容给出0~6条最有价值的建议，每条建议都要有根据（即针对之前的对话内容），无法给出建议就不给出建议)。面试结果(根据受试者(user)之前的回答和assistant角色之前的评价，要有根据，将({\n  '硬实力': [\n    { value: xx, name: '专业知识' },\n    { value: xx, name: '技术能力' },\n    { value: xx, name: '经验积累' }\n  ],\n  '软实力': [\n    { value: xx, name: '沟通能力' },\n    { value: xx, name: '团队协作' },\n    { value: xx, name: '表达能力' }\n  ],\n  '潜力': [\n    { value: xx, name: '学习能力' },\n    { value: xx, name: '创新能力' },\n    { value: xx, name: '适应能力' }\n  ],\n  '文化水平': [\n    { value: xx, name: '伦理抉择' },\n    { value: xx, name: '价值观' }\n  ],\n  '外部指标': [\n    { value: xx, name: '着装' },\n    { value: xx, name: '行为举止' }\n  ]\n}\n      )这份文件中的\"value\"字段填入分数（0~100，按比例计算）并以python字典格式返回.如果无法判断填多少，就填0).必须包含总评,建议,面试结果,这几个字\n评分参考：范围0~100.打分请严格公正该给低分就给低分(10~50)，该给高分就给高分(80~100)。没有优点，也没有缺点就打(50~80).胡说八道或者无关回答就0~10分\n风格设定:严格但热情"
        self.messages_history = [
            {
                "role": "system",
                "content":self.prompt
            }
        ]
    # 重置
    def reset(self):
        self.messages_history = [
            {
                "role": "system",
                "content": self.prompt
            }
        ]
        self.resume=""
        self.job_type=""
    #负责根据信息发送单次http请求对话
    def run(self, user_input):

        flag=False
        # 添加用户最新的输入到消息历史
        self.messages_history.append({
            "role": "user",
            "content": user_input
        })

        url =self.url
        data = {
            "max_tokens": 6144,
            "top_k": 6,
            "temperature": 1,
            "messages": self.messages_history,
            "model": "generalv3.5",
            "stream": True
        }

        header = {
            "Authorization": "Bearer AhQtdqLkWFtMMaEvzNzF:EwKbgPpsmoNYtDbWqfcm"
        }
        print("进行一次聊天")
        response = requests.post(url, headers=header, json=data, stream=True)

        # 流式响应解析示例
        response.encoding = "utf-8"
        ai_response = ""
        for line in response.iter_lines(decode_unicode="utf-8"):
            if line and line.startswith("data: "):
                # 提取JSON部分（去掉"data: "前缀）
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    break

                try:
                    data = json.loads(data_str)
                    # 拼接content字段
                    if "choices" in data and data["choices"]:
                        content = data["choices"][0].get("delta", {}).get("content", "")
                        ai_response += content
                except json.JSONDecodeError:
                    pass  # 忽略非JSON数据（如心跳包）
        # 将AI的响应添加到消息历史中
        if ai_response:
            self.messages_history.append({
                "role": "assistant",
                "content": ai_response
            })
        if "面试结束" in ai_response:
            print(">>> 面试已结束")
            flag=True

        return ai_response, self.messages_history,flag

    def parse_res(self,res):
        # Extract total score (matches first two numbers around a slash)
        print("开始生成总结,ai原始总结:",res)
        score_match = re.search(r'总评.*?(\d+)\s*/\s*(\d+)', res)
        if score_match:
            a = int(score_match.group(1))
            b = int(score_match.group(2))
            #print(a, "/", b)
            total_score = round((a / b) * 100) if b != 0 else -1
        else:
            total_score = -1

        # Extract suggestions (matches items after "建议：" until "面试结果")
        suggestions = []
        begin=res.find('建议')
        ed=res.find('面试结果')
        suggestion_section="9"
        if begin+2<=ed:
            suggestion_section = res[begin+2:ed]
            #print(suggestion_section)
        if suggestion_section:
            suggestion_matches =re.findall(r"\d+\..*?(?=\d+\.|\)|）)", suggestion_section, re.DOTALL)
            suggestions = [s.strip() for s in suggestion_matches if s.strip()]

        # Extract JSON data (matches content after "面试结果:")
        def extract_json_block(res):
            start = res.find('面试结果')
            if start == -1:
                return None
            start = res.find('{', start)
            end = res.rfind('}')
            if start == -1 or end == -1 or end <= start:
                return None
            return res[start:end + 1]

        # 提取 报告
        report_str = extract_json_block(res)
        #print("report_str；", report_str)

        # 预处理JSON字符串
        try:
            # 1. 替换单引号为双引号
            report_str = report_str.replace("'", '"')

            # 2. 为未加引号的键添加双引号
            # 处理 key: value 的情况
            report_str = re.sub(r'([{,]\s*)([a-zA-Z_]\w*)(\s*:)', r'\1"\2"\3', report_str)
            # 处理 { key: value } 的情况
            report_str = re.sub(r'{\s*([a-zA-Z_]\w*)(\s*:)', r'{ "\1"\2', report_str)

            # print("report_str:", report_str)
            # 3. 转换为字典
            report = json.loads(report_str)
        except json.JSONDecodeError as e:
            print("JSON解析失败:", e)
            report = {}
        return {
            'total_score': total_score,
            'suggestions': suggestions,
            'text_score': report
        }

    def parse_chat(self,response):
        # 匹配最前面的括号中的数字，格式为 (数字) 或 (数字xxx)
        start1=-1
        end1=-1
        for i in range(len(response)):
            if response[i]=='(' or response[i]=='（':
                start1=i
            if response[i]==')' or response[i]=='）':
                end1=i
            if start1>=0 and end1>=0:
                break
        t_score=response[start1+1:end1]
        print(t_score)
        t1_score=t_score.split('.')
        t2_score=t_score.split('，')
        t3_score = t_score.split(',')
        g=t1_score
        if len(t1_score)<len(t2_score):
            g=t2_score
        if(len(t2_score)<len(t3_score)):
            g=t3_score
        print(g)
        tot=0
        detail={}
        for item in g:
            if item.find('-')==-1:
                tot+=int(item)
            else:
                content_match = re.search(r'([\u4e00-\u9fa5\d]+)\s*-\s*([\u4e00-\u9fa5\d]+)', item)
                if content_match:
                    key = content_match.group(1)  # 获取 '经验积累' 等作为 key
                    value = int(content_match.group(2))  # 获取 '100' 并转为整数
                    detail[key] = value  # 添加到字典
        detail['tot']=tot
        # score_match = re.search(r'[(（-,.].*[）)-,.]', t_score,re.DOTALL)
        # if not score_match:
        #     print("未找到评分")
        #     return None
        # for i in range(len(score_match.groups()) + 1):
        #     print(f"group({i}): {score_match.group(i)}")

        #score = int(score_match.group(1)) if score_match else None
        score_match=True
        # 移除评分部分，保留实际回复内容
        if score_match:
            # 找到第一个右括号的位置
            bracket_pos = response.find(')')
            if bracket_pos == -1:
                bracket_pos = response.find('）')
            if bracket_pos != -1:
                actual_response = response[bracket_pos + 1:].strip()
            else:
                actual_response = response
        else:
            actual_response = response

        return {
            'score': detail,  # 提取到的评分（可能为None）
            'response': actual_response  # 实际回复内容
        }

#用于修改prompt调试对话效果
if __name__ == '__main__':
    vv = interviewer()
    tmp = {
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
    cnt = 1
    while True:
        break
        if cnt == 1:
            user_input = f"{tmp}你好，这是我的简历"
        else:
            print("请输入对话内容:")
            user_input = input()
        if user_input.lower() == 'quit':
            break

        response, messages_history, flag =vv. run( user_input)

        if flag:
            report = vv.parse_res(response)
            print("生成总结:", report)
            print("对话历史:", messages_history)
            print("AI回复:", response)
            break
        elif cnt > 1:
            parsed = vv.parse_chat(response)  # 先获取完整的解析结果
            responsed = parsed["response"]  # 获取实际回复内容
            tmp_score = parsed["score"]  # 获取评分

            if tmp_score is not None and tmp_score >= 0:
                print("得分:", tmp_score)
        cnt += 1
        print("AI回复:", response)
    # tt="面试结束，等待面试结果。\n\n面试总结：\n总分数：85/100\n预期的满分：100\n\n建议：\n1. 在回答技术问题时，可以更加深入地结合具体项目经验，以增强说服力。\n2. 对于团队协作和依赖管理的问题，可以进一步阐述个人在解决冲突和协调资源方面的具体策略。\n3. 在描述自我管理能力时，可以提供一些实际的时间管理或压力应对的例子。\n4. 对于前端和后端技术的掌握程度，可以适当展示一些实际开发中的小技巧或最佳实践。\n5. 在谈论个人兴趣和爱好时，可以尝试与职业发展或个人成长联系起来，展现全面的个人素质。\n\n评分依据：\n{\n  '硬实力': [\n    { value: 90, name: '专业知识' },\n    { value: 85, name: '技术能力' },\n    { value: 80, name: '经验积累' }\n  ],\n  '软实力': [\n    { value: 85, name: '沟通能力' },\n    { value: 90, name: '团队协作' },\n    { value: 85, name: '表达能力' }\n  ],\n  '潜力': [\n    { value: 85, name: '学习能力' },\n    { value: 80, name: '创新能力' },\n    { value: 80, name: '适应能力' }\n  ],\n  '文化水平': [\n    { value: -1, name: '伦理抉择' },\n    { value: -1, name: '价值观' }\n  ],\n  '外部指标': [\n    { value: -1, name: '着装' },\n    { value: -1, name: '行为举止' }\n  ]\n}"
    # tt1="面试结束，等待面试结果。\n\n面试总结：\n\n总分数：410/600\n预期的满分：600分\n\n建议：\n1. 在回答理论问题时，可以更加详细地阐述概念，并举例说明，以展示更深入的理解。\n2. 对于工作经验的描述，可以尝试结合具体项目或案例来讲述，这样能够更直观地体现个人能力和经验。\n3. 在表达自己的观点时，可以更加条理清晰，分点论述，以便面试官更好地理解你的思路。\n4. 注意避免使用过于笼统或模糊的表述，尽量用具体的数据或成果来支撑自己的观点。\n5. 在面试过程中，可以更加主动地展示自己的优势和特长，与面试官进行互动，增加面试的生动性。\n\n评分详情：\n{\n  '硬实力': [\n    { value: 90, name: '专业知识' },\n    { value: 85, name: '技术能力' },\n    { value: 80, name: '经验积累' }\n  ],\n  '软实力': [\n    { value: 75, name: '沟通能力' },\n    { value: 70, name: '团队协作' },\n    { value: 70, name: '表达能力' }\n  ],\n  '潜力': [\n    { value: 80, name: '学习能力' },\n    { value: 75, name: '创新能力' },\n    { value: 70, name: '适应能力' }\n  ],\n  '文化水平': [\n    { value: -1, name: '伦理抉择' },\n    { value: -1, name: '价值观' }\n  ],\n  '外部指标': [\n    { value: -1, name: '着装' },\n    { value: -1, name: '行为举止' }\n  ]\n}"
    tt3 = """
        总评(80/100)。建议(1. 需深入理解版本控制工具的分支管理策略 2. 加强前端性能优化知识储备 3. 注意代码规范性表述)。面试结果({'硬实力': [{'value': 75, 'name': '专业知识'}, {'value': 65, 'name': '技术能力'}, {'value': 80, 'name': '经验积累'}], '软实力': [{'value': 70, 'name': '沟通能力'}, {'value': 85, 'name': '团队协作'}, {'value': 60, 'name': '表达能力'}], '潜力': [{'value': 80, 'name': '学习能力'}, {'value': 75, 'name': '创新能力'}, {'value': 70, 'name': '适应能力'}], '文化水平': [{'value': -1, 'name': '伦理抉择'}, {'value': -1, 'name': '价值观'}], '外部指标': [{'value': -1, 'name': '着装'}, {'value': -1, 'name': '行为举止'}]})
        """
    tt4="（30，经验积累-100%，团队协作-0%，沟通能力-0%）你连基本解决思路都没掌握就完全依赖同事？遇到CPU飙升或内存泄漏时，你作为后端开发者连日志分析、线程排查、JVM调优这些基础操作都不会独立处理吗？"
    pp=vv.parse_chat(tt4)
    print("回复",pp)
    # ptt = vv.parse_res(tt3)
    # print(ptt)
    # print(type(ptt['report']))
    # json_str = json.dumps(ptt['report'], ensure_ascii=False)
    # print("json_str", json_str)#<class 'str'>
    # print(type(json_str))
    # pythonObj=json.loads(json_str)
    # if isinstance(pythonObj,dict):
    #     print("是python对象")
    # print("对话结束")
    tt2 = """
        面试总结

    总评(总分/满分)：65/100

    建议：
    1. 在回答技术问题时，应更加具体和深入，避免使用过于笼统的表述。
    2. 面对问题时，尝试结合自己的实际经历和项目经验来回答，这样更能展示你的实践能力和问题解决能力。
    3. 在描述团队合作和项目管理经验时，可以具体举例说明自己在团队中的角色和贡献，以及如何协调团队成员解决问题。
    4. 对于前端需求变更等具体问题，应提出更具体的应对策略和方法，而不是仅仅停留在“随机应变”的层面。
    5. 在讲述项目经验时，可以突出自己遇到的技术难题和解决方案，以展示自己的技术实力和创新能力。
    6. 注意提升自己的沟通能力和表达能力，确保能够清晰、准确地传达自己的想法和观点。

    面试结果：
    {
      '硬实力': [
        { value: 70, name: '专业知识' },
        { value: 65, name: '技术能力' },
        { value: 60, name: '经验积累' }
      ],
      '软实力': [
        { value: 60, name: '沟通能力' },
        { value: 70, name: '团队协作' },
        { value: 55, name: '表达能力' }
      ],
      '潜力': [
        { value: 65, name: '学习能力' },
        { value: 60, name: '创新能力' },
        { value: -1, name: '适应能力' }
      ],
      '文化水平': [
        { value: -1, name: '伦理抉择' },
        { value: -1, name: '价值观' }
      ],
      '外部指标': [
        { value: -1, name: '着装' },
        { value: -1, name: '行为举止' }
      ]
    }
        """
