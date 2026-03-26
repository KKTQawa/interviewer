# Interview Backend

面试达人 - 智能AI模拟面试平台后端

## 技术栈

- FastAPI
- MySQL
- 讯飞星火大模型
- DeepFace (人脸识别/表情识别)
- pyAudioAnalysis (语音特征提取)
- SenseVoice (语言情感识别)
- OpenCV

## 项目结构

```
interview_backend/
├── main.py                # FastAPI 入口
├── config.py              # 配置
├── database.py            # 数据库连接
├── interview.py           # 面试核心逻辑
├── spark_client.py        # 星火大模型调用
├── voice1.py / voice2.py  # 音频处理
├── vedio1.py / vedio2.py  # 视频分析
├── FileManager.py        # 文件管理
├── requirements*.txt      # Python 依赖
├── uploads/               # 上传文件存储
├── tmp/                   # 临时音频文件
└── other/                 # 实验性代码
```

## 运行

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn main:app --reload
```

## 环境变量

在 `.env` 文件中配置以下内容：

- 数据库连接信息
- 讯飞星火 API 密钥
- 其他服务配置

## API 端点

主要通过 `main.py` 提供 RESTful API 接口供前端调用。
