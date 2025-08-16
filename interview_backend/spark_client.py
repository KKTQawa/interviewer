
from config import SPARK_CONFIG1
import os

from sparkai.llm.llm import ChatSparkLLM
from sparkai.core.messages import ChatMessage

class SparkClient:
    def __init__(self):
        """初始化星火大模型客户端"""
        self.appid = SPARK_CONFIG1["app_id"]
        self.api_key = SPARK_CONFIG1["api_key"]
        self.api_secret = SPARK_CONFIG1["api_secret"]
        self.spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # Max环境
        self.domain = "generalv3.5"  # Max版本
        self.response_content = ""  # 用于存储响应内容
        # 初始化客户端
        self.spark = ChatSparkLLM(
            spark_api_url=self.spark_url,  # Max 3.5版本URL
            spark_app_id=self.appid,
            spark_api_key=self.api_key,
            spark_api_secret=self.api_secret,
            spark_llm_domain='generalv3.5',  # Max 3.5的domain
            streaming=False  # 是否流式输出
        )
    def chat(self,prompt,max_tokens=10000):
        messages = [ChatMessage(role="user", content=prompt)]
        #print("开始chat：",prompt)
        #response = self.spark.generate([messages])
        response = self.spark.generate(
            [messages],  # 消息列表
            temperature=0.7,  # 控制随机性 (0~1，越高越随机)
            max_tokens=max_tokens,  # 最大生成token数
            top_k=4,  # 从概率最高的k个token中采样
            top_p=0.8,  # 核采样阈值 (0~1)
            streaming=False,  # 是否流式输出
            stop=["。", "\n"],  # 遇到这些字符时停止生成
            repetition_penalty=1.1  # 避免重复的惩罚系数 (>1)
        )
        #print("chat_response:",response)
        return response.generations[0][0].text










