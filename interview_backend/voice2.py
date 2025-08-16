from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess


class smallVideoModel:
    def __init__(self):
        self.model_dir = "iic/SenseVoiceSmall"
        self.model= AutoModel(
            model=self.model_dir,
            trust_remote_code=True,
            remote_code="./model.py",
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            device="cuda:0",
        )
        self.emo_dict = {
            "<|HAPPY|>": "😊",
            "<|SAD|>": "😔",
            "<|ANGRY|>": "😡",
            "<|NEUTRAL|>": "",
            "<|FEARFUL|>": "😰",
            "<|DISGUSTED|>": "🤢",
            "<|SURPRISED|>": "😮",
        }

    def extract_emo(self,filename):
        res = self.model.generate(
            input=filename,
            cache={},
            language="auto",  # "zn", "en", "yue", "ja", "ko", "nospeech"
            use_itn=True,
            batch_size_s=60,
            merge_vad=True,  #
            merge_length_s=15,
        )
        #统计情绪出现的次数
        emo_count={
            "<|HAPPY|>": 0,
            "<|SAD|>": 0,
            "<|ANGRY|>": 0,
            "<|NEUTRAL|>": 0,
            "<|FEARFUL|>": 0,
            "<|DISGUSTED|>": 0,
            "<|SURPRISED|>": 0,
        }
        text1=res[0]["text"]
        text2=rich_transcription_postprocess(text1)
        total_count=0
        for [key, value] in self.emo_dict.items():
            tmp_cnt=text1.count(key)
            total_count+=tmp_cnt
        for [key, value] in self.emo_dict.items():
            if total_count==0:
                print('总表情为0')
                emo_count[key]=0
            else :
                emo_count[key]=text1.count(key)/total_count
        emo_suggest=[]
        if emo_count["<|DISGUSTED|>"]+emo_count["<|SAD|>"]>0.4 :
            emo_suggest=["请打起精神"]
        elif emo_count["<|HAPPY|>"]+emo_count["<|SURPRISED|>"]>0.3 :
            emo_suggest=["你精神状态很好，继续保持"]
        elif emo_count["<|FEARFUL|>"]>0.3 and emo_count["<|NEUTRAL|>"]>0.5:
            emo_suggest=["专注一点，不要紧张，放轻松"]
        elif emo_count["<|NEUTRAL|>"]>0.8:
            emo_suggest=["你很专注"]

        return text2,emo_count,emo_suggest
if __name__ == "__main__":
    model = smallVideoModel()
    res,emo, suggest = model.extract_emo("talk.wav")
    print(res)
    print(emo)
    example="""<|zh|><|NEUTRAL|><|Speech|><|withitn|>而软件生命周期是指从规划到废弃的全过程。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>呃，主要包括需求分期、设计、实现测试和部署维护这几个阶段。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>呃，如果想要优化呃一段时间发杂度较高的代码的话。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>呃，一般我都是先分期呃，影响时间带。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>时间复杂度的关键问题所在。然后呃就尝试使用更高效的算法或者数据结构。，比如说哈希用哈希表去替代线性搜索呃，以此来重复减少重复计算或者采用并情化处理。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>比如多线程或者分布式计算当中，这些场景，我就采用并形化处理。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>啊，单列模式就是确保一个类，它只有一个实例，一般用于数据库连接日志系统这些呃需要全局访问点的场景。 <|en|><|EMO_UNKNOWN|><|Speech|><|withitn|>I. <|zh|><|NEUTRAL|><|Speech|><|withitn|>也就是执行get pull，如果提示冲突，就使用get data查看冲突日志文件，然后去手动编辑这些文件，解决冲突。最后保留保留需要的代码，最后再执行get add。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>然后fi和get commit完成合并。首先就是要跟队友商量好，然后。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>明确分工，一个人开发一个模块规范代码的风格，然后实时也要沟通反馈，免得别人就是写了，然后你也不用。 <|en|><|EMO_UNKNOWN|><|Speech|><|withitn|>The. <|zh|><|NEUTRAL|><|Speech|><|withitn|>呃，其实就是通过两次的实习，我发现我自己的话既享受前端可以及时可见的成就感，也非常喜欢后端的逻辑设计。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>全站开发可以让我更完整的理解系统架构。在魔镜这个项目当中的话呃。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>由于它是一个基于计算机视觉的穿衣搭配推荐系统。呃，我主要是负责搭建图像分类模块，然后负责撰且算法实现的论文章节。 <|en|><|EMO_UNKNOWN|><|Speech|><|withitn|>The. <|zh|><|NEUTRAL|><|Speech|><|withitn|>最近三个月的话，我正在学习next JS和next JS框架，实践权站项目，同时系统学习docker系融件化部署。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>呃我们团队的话在。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>那次比赛主要是开发了基于支识图谱的智能客服系统。我主导了python后端问答引擎的优化，使得响应速度非常提升的很很多。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>最后那个项目也是拿来奖。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>嗯，如果遇到需求频繁变更的话，我一般会先通过原型设计确认核心要求，采用模块化开发。比如使用reck组件库来快速响应前前端的变更。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>呃，篮球这些兴趣爱好的话，主要是培养了我和团队的协作意识和抗压能力这。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>嗯，我觉得这项技能在敏在快速开发项目需要快速得出对快速产出结果的。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>过程中非常重要。，我之所以选择软件工程专业的话，主要是因为我对解决复杂问题和技术创新充满了兴趣。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>呃，因为软件工程它结合了逻辑思维与创造力。呃，我未来的话也希望深耕后端开发领域吧，成为架构师。 <|zh|><|NEUTRAL|><|Speech|><|withitn|>嗯，同时持续学习云原生活AI技术，提升大规模系统的设计能力。那好的，我我我知道了，谢谢。
而软件生命周期是指从规划到废弃的全过程。呃，主要包括需求分期、设计、实现测试和部署维护这几个阶段。呃，如果想要优化呃一段时间发杂度较高的代码的话。呃，一般我都是先分期呃，影响时间带。时间复杂度的关键问题所在。然后呃就尝试使用更高效的算法或者数据结构。，比如说哈希用哈希表去替代线性搜索呃，以此来重复减少重复计算或者采用并情化处理。比如多线程或者分布式计算当中，这些场景，我就采用并形化处理。啊，单列模式就是确保一个类，它只有一个实例，一般用于数据库连接日志系统这些呃需要全局访问点的场景。I.也就是执行get pull，如果提示冲突，就使用get data查看冲突日志文件，然后去手动编辑这些文件，解决冲突。最后保留保留需要的代码，最后再执行get add。然后fi和get commit完成合并。首先就是要跟队友商量好，然后。明确分工，一个人开发一个模块规范代码的风格，然后实时也要沟通反馈，免得别人就是写了，然后你也不用。 呃，其实就是通过两次的实习，我发现我自己的话既享受前端可以及时可见的成就感，也非常喜欢后端的逻辑设计。全站开发可以让我更完整的理解系统架构。在魔镜这个项目当中的话呃。由于它是一个基于计算机视觉的穿衣搭配推荐系统。呃，我主要是负责搭建图像分类模块，然后负责撰且算法实现的论文章节。 最近三个月的话，我正在学习next JS和next JS框架，实践权站项目，同时系统学习docker系融件化部署。呃我们团队的话在。那次比赛主要是开发了基于支识图谱的智能客服系统。我主导了python后端问答引擎的优化，使得响应速度非常提升的很很多。最后那个项目也是拿来奖。嗯，如果遇到需求频繁变更的话，我一般会先通过原型设计确认核心要求，采用模块化开发。比如使用reck组件库来快速响应前前端的变更。呃，篮球这些兴趣爱好的话，主要是培养了我和团队的协作意识和抗压能力这。嗯，我觉得这项技能在敏在快速开发项目需要快速得出对快速产出结果的。过程中非常重要。，我之所以选择软件工程专业的话，主要是因为我对解决复杂问题和技术创新充满了兴趣。呃，因为软件工程它结合了逻辑思维与创造力。呃，我未来的话也希望深耕后端开发领域吧，成为架构师。嗯，同时持续学习云原生活AI技术，提升大规模系统的设计能力。那好的，我我我知道了，谢谢。
    """