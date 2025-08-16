import oss2
from oss2 import Bucket, Auth
from typing import Optional
import urllib.parse#用于url编码
import os
from fastapi import HTTPException
import uuid
import shutil
from pathlib import Path
from urllib.parse import quote
from fastapi import UploadFile
import PyPDF2
from docx import Document
import pytesseract
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime


class FileManager:
    def __init__(self, access_key_id: str, access_key_secret: str, bucket_name: str, endpoint: str,region:str,spark_client):

        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.spark_client = spark_client
        self.bucket_name = bucket_name
        self.endpoint = endpoint.rstrip('/')  # 去除末尾斜杠
        self.region=region
        self.bucket: Optional[Bucket] = None
        self.UPLOAD_DIR = Path("uploads")
        self.ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'mp4', 'webm', 'mp3', 'wav'}
        # 确保上传目录存在
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        (self.UPLOAD_DIR / "img").mkdir(exist_ok=True)
        (self.UPLOAD_DIR / "audios").mkdir(exist_ok=True)

    def connect(self) -> Bucket:
        bucket=None
        try:
            if not self.bucket:
                auth = Auth(self.access_key_id, self.access_key_secret)
                bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name,region=self.region)
        except Exception as e:
            print(f"连接OSS失败: {e}")

        return bucket
    def get_dir(self,file_name):
        file_extension=file_name.split('.')[-1]
        if not file_extension:
            raise ValueError("文件名错误！")
        dir=''
        if file_extension in ['txt','pdf', 'doc', 'docx']:
            dir='document'
        elif file_extension in ['mp4', 'webm','gif']:
            dir='video'
        elif file_extension in ['mp3', 'wav']:
            dir='audio'
        elif file_extension in ['png','jpg', 'jpeg']:
            dir='image'
        return dir
    def is_exists(self,bucket, object_key: str) -> bool:
        encoded_path = quote(object_key, safe='/')
        try:
            bucket.head_object(encoded_path)
            return True
        except oss2.exceptions.NoSuchKey:
            return False
        except oss2.exceptions.NotFound:
            return False
        except Exception as e:
            print(f"Error checking file existence: {e}")
            return False
    def is_exists2(self,bucket,user_id: int, file_name: str)->bool:
        dir = self.get_dir(file_name)
        file_path = f"{dir}/{user_id}_{file_name}"
        return self.is_exists(bucket,file_path)
    def upload_file(self, file, file_name: str, user_id: int) -> str:
        dir = self.get_dir(file_name)
        file_path = f"{dir}/{user_id}_{file_name}"
        bucket = self.connect()

        print("上传文件:", file_path)
        # 示例'https://interviewresource.oss-cn-beijing.aliyuncs.com/video/demo2-video.mp4'

        # 上传本地文件
        result = bucket.put_object(file_path, file)

        if result.status == 200:
            # 对路径进行 URL 编码，保留 /
            encoded_path = quote(file_path, safe='/')
            return f"https://{self.bucket_name}.oss-cn-beijing.aliyuncs.com/{encoded_path}"
        raise Exception(f"上传文件失败: {result.status}")

    def delete_file(self, user_id,file_name) -> bool:
        dir = self.get_dir(file_name)
        file_path=f"{dir}/{user_id}_{file_name}"
        bucket = self.connect()
        encoded_path = quote(file_path, safe='/')
        result = bucket.delete_object(encoded_path)
        return result.status == 204
    
    async def extract_resume_content(self, file: UploadFile):
        """从不同格式的简历文件中提取文本内容（支持UploadFile对象）"""
        try:
            # 获取文件扩展名（确保正确处理带点的后缀）
            filename = file.filename
            ext = filename[filename.rfind('.'):].lower() if '.' in filename else ''
            from io import BytesIO
            if ext == '.txt':
                # 文本文件直接读取
                content = (await file.read()).decode('utf-8')
                await file.seek(0)  # 重置指针以便后续操作
                return content

            elif ext == '.pdf':
                # PDF文件处理（使用PyPDF2）
                content = []
                pdf_data = await file.read()

                # 使用BytesIO模拟文件对象
                with BytesIO(pdf_data) as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:  # 避免None
                            content.append(text)

                await file.seek(0)
                return '\n'.join(content)

            elif ext in ['.doc', '.docx']:
                # Word文档处理（使用python-docx）
                docx_data = await file.read()
                doc = Document(BytesIO(docx_data))
                await file.seek(0)
                return '\n'.join([para.text for para in doc.paragraphs if para.text])

            elif ext in ['.png', '.jpg', '.jpeg']:
                # 图片OCR处理（需安装pytesseract和Pillow）
                from PIL import Image
                image_data = await file.read()
                image = Image.open(BytesIO(image_data))
                await file.seek(0)
                return pytesseract.image_to_string(image, lang='chi_sim+eng')

            else:
                raise ValueError(f"不支持的文件类型: {ext}")

        except Exception as e:
            print(f"提取简历内容失败: {str(e)}")
            raise ValueError(f"文件处理错误: {str(e)}")

        # 整理成格式化的内部信息
    async def organize_content(self, resume_content, job):
        try:
            prompt = f"""
    从以下文本中提取关键文字信息:{resume_content}。整理为json格式的响应数据。json需包含以下字段:
    "姓名""手机号""邮箱""性别""年龄""意向岗位""学历信息""专业""实习经历""学术成就""技能""自我评价",其中“技能"是指兴趣爱好/特长,"学术成就"是指
    科研成果/竞赛获奖/做过或者参与的项目,如果无法找到"学历信息""性别""年龄""姓名""意向岗位""专业""技能"这几个字段，就只返回空的json数据。
            """
            prompt1 = prompt  # 推测这里需要自动转换
            response = self.spark_client.chat(prompt1, 512)  # 如果max_tokens过小可能返回空结果
            if not response:  # 检查空数据
                raise HTTPException(
                    status_code=400,
                    detail="无法从简历中提取有效信息"
                )
            return response
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=422,
                detail="简历内容格式解析失败"
            )
        except Exception as e:
            print(f"简历处理发生错误: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"简历处理发生错误: {str(e)}"
            )

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS






















    async def generate_report(self, report_data: dict, output_path: str) -> str:
        """生成面试报告PDF文件"""
        try:
            # 注册中文字体
            pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
            
            # 创建PDF文件
            c = canvas.Canvas(output_path, pagesize=letter)
            c.setFont('SimSun', 16)
            
            # 标题
            c.drawString(100, 750, "面试评估报告")
            c.setFont('SimSun', 12)
            
            # 基本信息
            c.drawString(100, 700, f"面试ID: {report_data['interview_id']}")
            c.drawString(100, 680, f"总分: {report_data['total_score']:.1f}")
            c.drawString(100, 660, f"评级: {report_data['rating']}")
            c.drawString(100, 640, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 问题和答案评估
            y = 600
            for i, question in enumerate(report_data['questions'], 1):
                if y < 100:  # 如果页面空间不足，添加新页面
                    c.showPage()
                    c.setFont('SimSun', 12)
                    y = 750
                
                c.drawString(100, y, f"问题 {i}: {question['question']}")
                y -= 20
                c.drawString(120, y, f"答案: {question.get('answer_text', '未作答')}")
                y -= 20
                c.drawString(120, y, f"得分: {question.get('score', 0):.1f}")
                y -= 30
            
            # 简历分析
            if y < 200:  # 如果页面空间不足，添加新页面
                c.showPage()
                c.setFont('SimSun', 12)
                y = 750
            
            c.drawString(100, y, "简历分析:")
            y -= 20
            resume_content = report_data['resume_analysis']['content']
            # 简单的文本换行处理
            words = resume_content.split()
            line = ""
            for word in words:
                if len(line + word) < 50:  # 假设每行50个字符
                    line += word + " "
                else:
                    c.drawString(120, y, line)
                    y -= 20
                    line = word + " "
            if line:
                c.drawString(120, y, line)
            
            # 保存PDF
            c.save()
            return output_path
            
        except Exception as e:
            print(f"生成报告失败: {str(e)}")
            raise