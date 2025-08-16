# 面试达人

## 运行

### 后端

1. 确保python版本为3.12.0(最好已添加至系统环境变量)

2. 首次运行双击`build.bat`构建虚拟环境,然后双击`init_run.bat`运行。如有误，则可在cmd界面手动输入bat脚本中的指令查看具体报错信息
   
3. 后续运行可直接双击`run.bat`

### 前端

首次在`interview-aissistant`目录下运行`npm install`安装依赖，然后运行`npm run dev`启动项目，后续就双击`run.bat`

## 技术栈

### 前端
Vue 3

### 后端
⚡ FastAPI – 轻量高性能 Web 框架

🐬 MySQL 数据库：使用 [sqlpub](https://www.sqlpub.com) 管理

### 智能体系统
🌟 讯飞星火大模型
用于智能问答 + 人脸识别

😊 DeepFace
进行表情识别（Emotion Recognition）

🗣️ pyAudioAnalysis
语音特征提取

🎙️ SenseVoiceSmall（modelscope）
语言情感识别（[GitHub 仓库](https://github.com/FunAudioLLM/SenseVoice)）


🔐 其他
所有相关密钥均保存在以下文件中：

.env

.env_secret

* 项目中的图片都由通义万祖生成

