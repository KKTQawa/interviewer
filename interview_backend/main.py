from dotenv import load_dotenv
import os  # 用于获取环境变量
import sys
import shutil
from pathlib import Path
from passlib.context import CryptContext
import uuid
import json
import base64
# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, Request, status, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel
from datetime import datetime, timedelta,timezone
from typing import Optional, Dict, Any, List

import secrets
from jose import jwt

#from analyzer.main import InterviewAnalyzer
from spark_client import SparkClient
from database import DatabaseManager
from FileManager import FileManager
from config import (
    UPLOAD_DIR, ALLOWED_EXTENSIONS, SECRET_KEY as CONFIG_SECRET_KEY,
    ALGORITHM as CONFIG_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES as CONFIG_TOKEN_EXPIRE,
    SPARK_CONFIG
)
app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# OAuth2 配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # 用于密码哈希和验证
# 配置JWT
print(">>>>>>>>>>>>>>>>>>>>>加载环境变量<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
load_dotenv(".env")
load_dotenv(".env.secret")#叠加加载
SECRET_KEY = os.getenv("SECRET_KEY") or CONFIG_SECRET_KEY
ALGORITHM = os.getenv("ALGORITHM") or CONFIG_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or CONFIG_TOKEN_EXPIRE)
REFRESH_TOKEN_EXPIRE_MINUTES =int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))
OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")

# 创建全局对象实例
print(">>>>>>>>>>>>>>>>>>>>>加载对象实例<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
spark=SparkClient()
file_manager = FileManager(OSS_ACCESS_KEY_ID,OSS_ACCESS_KEY_SECRET,"interviewresource","https://oss-cn-beijing.aliyuncs.com/","cn-beijing",spark)
db_manager = DatabaseManager()

# 传入刷新令牌，获取新的访问令牌access_token和刷新令牌refresh_token
class RefreshTokenRequest(BaseModel):
    refresh_token: str
@app.post("/api/auth/refresh")
async def refresh_token(request: RefreshTokenRequest,meta:Request):
    current_refresh_token = request.refresh_token

    # 从数据库获取令牌记录（包括哈希值和元数据）
    token_record = db_manager.select(
        table="refresh_tokens",
        conditions={
            "is_active":1,
            "ip_address":meta.client.host, #获取客户端IP地址
            "expired_at":{">":datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}
        }
    )

    # 验证刷新令牌是否匹配
    # next(iterator,default=None)获取迭代器的下一个元素
    # 从token_record（这里是一张表）中找到第一个匹配的记录，如果没有找到则返回None
    print('token_record ',token_record)
    token_record = next(
        (record for record in token_record if pwd_context.verify(current_refresh_token, record["token_hash"])),
        None
    )

    if not token_record:
        print("无效的刷新令牌或已过期")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌或已过期"
        )

    user_id = token_record["user_id"]
    # 生成新令牌
    new_access_token = generate_access_token({"sub": str(user_id)})

    # 更新数据库（使用事务确保原子性）
    try:
        db_manager.update(
            table="refresh_tokens",
            data={
                "user_id": user_id,
                "token": current_refresh_token,
                "token_hash": pwd_context.hash(current_refresh_token),
                "is_active": 1,
                "ip_address":meta.client.host, #获取客户端IP地址
                "created_at":token_record["created_at"],
                "expired_at":token_record["expired_at"]
            },
            conditions={"id": token_record["id"]}
        )
        db_manager.commit()
    except Exception as e:
        db_manager.rollback()
        print(f"令牌更新失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌更新失败"
        )

    # FastAPI自动将类型转换为json格式
    return {
        "data": {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 访问令牌的有效期
        }
    }
# 辅助函数：生成安全的随机令牌,封装过期时间
def generate_refresh_token(user_id, length=64):
    # 生成随机部分
    token_id = secrets.token_urlsafe(length)

    #计算时间
    data = datetime.utcnow()
    expired = data + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    # 格式化为 "YYYY-MM-DD HH:MM:SS" 格式
    data = data.strftime("%Y-%m-%d %H:%M:%S")
    expired= expired.strftime("%Y-%m-%d %H:%M:%S")

    # 组合 payload（包含过期时间）
    payload = {
        "sub": user_id,
        "jti": token_id,  # token 唯一标识
        "exp": expired # 过期时间
    }
    
    token = jwt.encode(payload, "SECRET_KEY", algorithm=ALGORITHM )
    
    return {"token":token,"created_at":str(data),"expired_at":expired} 

# 辅助函数：生成访问令牌(JWT),data是一个字典，包含要编码的数据（选择要唯一）
def generate_access_token(data: dict, expires_delta: Optional[timedelta] = None):#None或者timedelta
    to_encode = data.copy()#创建副本，避免直接修改原始数据
    #datatime.utcnow()默认返回YYYY-MM-DD HH:MM:SS.microseconds格式的时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire=expire.strftime("%Y-%m-%d %H:%M:%S")#格式化为 "YYYY-MM-DD HH:MM:SS" 格式
    to_encode.update({"exp": expire})#更新字典的exp键
    #传入三个参数：要封装的数据，加密密钥，加密算法
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 传入用户信息，包含用户名，邮箱（可以为空），密码，在数据库中注册
class RegisterRequest(BaseModel):
    username: str
    email: str =None
    password: str
@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    # 检查用户名是否已存在
    print("注册:",request)
    existing_user = db_manager.select(
        table="users", 
        conditions={"username": request.username}
    )
    print("查询用户信息：",existing_user)
    if existing_user:
        return {"data": None}  # 返回None，不返回error

    # 插入新用户数据
    try:
        tz = timezone(timedelta(hours=8))
        created_at= datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S") # 东8区时间
        print("开始注册用户")
        db_manager.insert("users", {
            "username": request.username,
            "email": request.email,
            "password": request.password, # 注意：实际应用中应先哈希密码
            "created_data":created_at
        })
        db_manager.commit()
        return {"data": "注册成功"}
    except Exception as e:
        print("注册失败:", e)
        db_manager.rollback()
        raise HTTPException(status_code=500, detail="用户注册失败")

# 返回令牌，更新用户状态，刷新令牌
@app.post("/api/auth/login")
async def login(request: RegisterRequest,meta: Request):#request使用pydantic模型将json的body自动转换为字典，meta则直接继承原始json对象，用于获取body之外的内容
    print(">>>>>>>>>>>>>>>>>>>>>登录<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print("请求体：：", request)
    # 1. 验证用户是否存在
    users = db_manager.select(
        table="users",
        conditions={"username": request.username}
    )
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"  # 模糊提示，避免暴露用户存在信息
        )
    
    user = users[0]
    print("登录用户:", user)
    # 2. 生成令牌
    access_token = generate_access_token({"sub": str(user["id"])})
    res=generate_refresh_token(user["id"])
    refresh_token = res["token"]
    print("access_token:", access_token)
    print("refresh_token:", refresh_token)
    # 3. 保存刷新令牌到数据库
    try:
        print("开始保存新令牌")
        print("user_id:", user["id"],"ip_address:",meta.client.host,"created_at:",res["created_at"],"expired_at:",res["expired_at"])
        db_manager.insert(
            table="refresh_tokens",
            data={
                "user_id": user["id"],
                "token": refresh_token,
                "token_hash": pwd_context.hash(refresh_token),
                "is_active": 1,
                "ip_address":meta.client.host, #获取客户端IP地址
                "created_at":res["created_at"],
                "expired_at":res["expired_at"]
            }
        )
        db_manager.commit()
    except Exception as e:
        print("新增令牌失败:", e)
        db_manager.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请重试"
        )
    
    # 4. 返回响应
    res={
        "data": {
            "id": user["id"],
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expired_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60*1000#  毫秒
        }
    }    
    print("返回响应:", res)
    return res
# 传入用户名，返回用户相关信息
@app.get("/api/user/get_info")
async def get_info(username: str):
    #自动转换json为词典
    def safe_get_json(field):
        if field is None:
            return None
        if isinstance(field, dict):  # 如果驱动已自动转换
            return field
        try:
            return json.loads(field)
        except (TypeError, json.JSONDecodeError):
            return None
    print(">>>>>>>>>>开始查询用户信息<<<<<<<<<<<<<<<<<")
    # 查询用户信息
    user = db_manager.select(
        table="users",
        conditions={"username": username}
    )
    if not user:
        print("用户不存在")
        return {"data": None}  # 如果没有找到用户，返回空字典，不返回error

    # 返回用户信息（隐藏敏感信息，如密码）
    print("用户存在")
    print(user)
    #查询用户存储信息
    user_store = db_manager.select(
        table="user_store",
        conditions={"user_id": user[0]["id"]}
    )
    
    try:
        preference =safe_get_json(user_store[0]["user_preference"] if user_store else None)
    except Exception as e:
        print("解析用户偏好失败:", e)
        preference=None
    user_info = {
        "id": user[0]["id"],
        "username": user[0]["username"],
        "email": user[0]["email"],
        "password": user[0]["password"], 
        "created_data": user[0]["created_data"].strftime("%Y-%m-%d") if user[0]["created_data"] else None ,#转换日期格式
        "preference":preference,
    }
    print(user_info)

    res={"data": user_info}
    print("返回用户信息:", res)
    return res
@app.get("/api/user/query_info")
async def query_info(user_id: str):
    try:
        res = db_manager.select(
            table="users",
            conditions={"id": user_id}
        )
        res1 = db_manager.select(
            table="user_store",
            conditions={"user_id": user_id}
        )
        if len(res1)==0:
            res1=[{"user_id":user_id,"user_preference":{}}]
        pre=json.loads(res1[0]["user_preference"])
        return{
        "id": res[0]["id"],
        "username": res[0]["username"],
        "email": res[0]["email"],
        "password": res[0]["password"],
        "preference":pre,
        }
    except Exception as e:
        print("查询用户信息失败:", e)
        raise HTTPException(status_code=500, detail="查询用户信息失败")

class UpdataUserInfoRequest(BaseModel):
    id: int
    username: str=""
    email: str=""
    preferences: Dict[str, Any] = {} #user_store中直接存储json
@app.post("/api/user/update")
async def update_userinfo(request: UpdataUserInfoRequest):
    #更新users表
    try:
        db_manager.update(
            table="users",
            data={
                "username": request.username,
                "email": request.email,
            },
            conditions={"id": request.id}
        )
        db_manager.commit()
    except Exception as e:
        print("更新user表失败:",e)
        db_manager.rollback()
    tmp_user = db_manager.select(
        table="user_store",
        conditions={"user_id": request.id}
    )
    print(request.preferences)
    #如果是首次更新
    if not tmp_user:
        try:
            db_manager.insert(
                table="user_store",
                data={
                    "user_id": request.id,
                    "user_preference": json.dumps(request.preferences)  # 显式转换为JSON字符串
                }
            )
            db_manager.commit()
        except Exception as e:
            print("插入user_store表失败:",e)
            db_manager.rollback()
    else:
        #更新user_store表
        try:
            db_manager.update(
                table="user_store",
                data={
                    "user_preference": json.dumps(request.preferences)  # 显式转换为JSON字符串
                },
                conditions={"user_id": request.id}
            )
            db_manager.commit()
        except Exception as e:
            print("更新user_store表失败:",e)
            db_manager.rollback()
    return {"message": "更新成功","data": ""}

@app.post("/api/upload/file")
async def upload(
    user_id: int = Form(...),
    file: UploadFile = File(...)
):
    try:
        # 检查文件名是否存在
        bucket = file_manager.connect()
        if file_manager.is_exists2(bucket, user_id, file.filename):
            raise HTTPException(status_code=400, detail="文件已存在")
        file_url=file_manager.upload_file(file.file,file.filename,user_id)
        return{
            "url": file_url
        }
    except Exception as e:
        print("上传文件失败:",e)
        raise HTTPException(status_code=500, detail=str(e))
# 简历允许的文件类型
RESUME_ALLOWED_EXTENSIONS = {'txt', 'doc', 'docx', 'pdf', 'jpg', 'jpeg', 'png'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in RESUME_ALLOWED_EXTENSIONS

mark={
    "硬实力": [
        {"value": 0, "name": "专业知识"},
        {"value": 0, "name": "技术能力"},
        {"value": 0, "name": "经验积累"}
    ],
    "软实力": [
        {"value": 0, "name": "团队协作"},
        {"value": 0, "name": "表达能力"}
    ],
    "潜力": [
        {"value": 0, "name": "学习能力"},
        {"value": 0, "name": "创新能力"},
        {"value": 0, "name": "适应能力"}
    ],
    "文化水平": [
        {"value": 0, "name": "伦理抉择"},
        {"value": 0, "name": "价值观"}
    ],
    "外部指标": [
        {"value": 0, "name": "面试准备程度"},
        {"value": 0, "name": "专业度"}
    ]
}
def parse_i_chat(x):
    try:
        resume_begin = x.find("{")
        resume_end = x.rfind("}")
        #print("评分内容:", x[resume_begin:resume_end + 1])
        score = json.loads(x[resume_begin:resume_end + 1])
        xx=x[resume_end:]
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
class mark_resumeModel(BaseModel):
    resume: Dict[str, Any]
    file_name:str
    user_id:int
@app.post("/api/interview/resume")
async def mark_resume(request:mark_resumeModel):
    fileName=request.file_name+".txt"
    #检查文件名是否存在
    bucket = file_manager.connect()
    if file_manager.is_exists2(bucket,request.user_id,fileName):
        raise HTTPException(status_code=400, detail="文件已存在")

    print("收到简历信息",request.resume)
    print(type(request.resume))
    # #生成临时txt文件
    # with open("output.txt", "w", encoding="utf-8") as f:
    #     json.dump(request.resume, f, ensure_ascii=False, indent=4)
    # print("已生成临时文件output.txt")

    organized_content=request.resume
    # 给简历打分
    r_prompt = f"""{organized_content}。。。
    这是一份简历信息。第一、你需要分析简历并进行合理推理，对{mark}中每一项指标给出加成分数，0~100分，最后将填了分数的mark返回(如包含单引号请替换为双引号），第一部分请不要输出别的内容！当你确定性或依据不足时，你可以选择不评分,例如：你无法从简历中推测出这个人的创新能力如何或者有什么亮点，就先打0分。或者，你从简历中推测出这个人表述很有逻辑，于是给表达能力和面试准备程度各加10分。
    第二、你需要寻找简历中的矛盾、错误之处(忽略格式相关的错误)或者不足之处，然后按条给出建议。参考格式(python列表，使用双引号而非单引号):建议:["1.时间线冲突","2.无法搜索到华东师范大学",...]
    """
    res1 = spark.chat(r_prompt)
    print("获取简历评分回复:", res1)
    resume_score, suggest = parse_i_chat(res1)
    print("简历评分:", resume_score)
    print("简历建议:", suggest)
    # #上传txt文件
    # with open("output.txt", 'rb') as f:
    #     file_manager.upload_file(f, fileName, request.user_id)
    # print("上传简历文件成功")
    # os.remove("output.txt")
    return {
        "code": 200,
        "data": {
            "interview_id": 1,
            "resume": organized_content,
            "resume_score": resume_score,
            "resume_suggestion": suggest
        }
    }

@app.post("/api/upload/resume")
async def upload_resume(
    file: UploadFile = File(...),
    job: str = Form(...),
    user_id: int = Form(...)
):
    try:
        # 验证文件类型
        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        #先检查是否存在同名文件
        bucket=file_manager.connect()
        if file_manager.is_exists2(bucket,user_id,file.filename):
            raise HTTPException(status_code=400, detail="文件已存在")

        #这是参数形式，接收。前端以fromData形式进行传输
        print("开始分析简历","目标岗位:",job,"用户Id:",user_id)
        # 提取简历内容
        content =await file_manager.extract_resume_content(file)

        content=content+job
        #print("提取文件内容:",content)
        organized_content =await file_manager.organize_content(content, job)
        print("成功提取简历内容:",organized_content)
        #给简历打分
        r_prompt=f"""{organized_content}。。。
这是一份简历信息。第一、你需要分析简历并进行合理推理，对{mark}中每一项指标给出加成分数，0~100分，最后将填了分数的mark返回，第一部分请不要输出别的内容！当你确定性或依据不足时，你可以选择不评分,例如：你无法从简历中推测出这个人的创新能力如何或者有什么亮点，就先打0分。或者，你从简历中推测出这个人表述很有逻辑，于是给表达能力和面试准备程度各加10分。
第二、你需要寻找简历中的矛盾、错误之处(忽略格式相关的错误)或者不足之处，然后按条给出建议。参考格式(python列表，使用双引号而非单引号):建议:["1.时间线冲突","2.无法搜索到华东师范大学",...]
"""
        res1=spark.chat(r_prompt)
        print("获取简历评分回复:",res1)
        resume_score,suggest=parse_i_chat(res1)
        print("简历评分:", resume_score)
        print("简历建议:", suggest)

        return {
            "code": 200,
            "data": {
                "resume" :organized_content,
                "resume_score": resume_score,
                "resume_suggestion":suggest
            }
        }
    except HTTPException:
        # 直接重新抛出，保留原始状态码和详情
        raise
    except Exception as e:
        # 仅处理非HTTPException的异常
        print(f"上传简历失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")
#检查是否为有效的标准wav文件
import wave
from pydub import AudioSegment
async def convert_to_wav(input_path: str, output_dir="") -> str:
    if not output_dir:
        output_dir=os.path.dirname(input_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # 加载音频文件（自动识别格式）
        audio = AudioSegment.from_file(input_path)

        # 输出路径
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        out_path = os.path.join(output_dir, f"{base_name}.wav")

        # 导出为标准 WAV (PCM)
        audio.export(out_path, format="wav")
        print(f"转换成功: {input_path} -> {out_path}")
        return out_path

    except Exception as e:
        print(f"转换失败: {input_path}，错误信息: {e}")
        return ""

def is_valid_wav(file_path):
    try:
        with wave.open(file_path, 'rb') as wf:
            wf.getparams()  # 尝试读取参数
        return True
    except (wave.Error, EOFError):
        return False
voice_mark="""{
    "硬实力": [
        {"value": 0, "name": "专业知识"},
        {"value": 0, "name": "经验积累"}
    ],
    "软实力": [
        {"value": 0, "name": "表达能力"}
    ],
    "潜力": [
        {"value": 0, "name": "学习能力"},
        {"value": 0, "name": "创新能力"},
        {"value": 0, "name": "适应能力"}
    ],
    "外部指标": [
        {"value": 0, "name": "面试准备程度"},
        {"value": 0, "name": "专业度"},
        { "value": 0, "name": "精神风貌"}
    ]
}
    """
from voice1 import videoFeature
from voice2 import smallVideoModel
selfmodel=videoFeature()
emo_model = smallVideoModel()
@app.get("/api/interview/voice_mark")
async def handle_interview_finish():
    ###创建完整wav文件
    upload_audio_dir = "uploads/audios"
    tmp_dir = "tmp"
    output_file_path = os.path.join(upload_audio_dir, "recording.wav")

    # 确保上传目录存在
    os.makedirs(upload_audio_dir, exist_ok=True)
    # 判断 tmp 目录是否存在
    if not os.path.exists(tmp_dir):
        print("tmp 目录不存在，无需合并")
        return
    if os.path.exists("audio/recording.wav"):
        os.remove("audio/recording.wav")
        print("已移除原有文件:","audio/recording.wav")
    # 获取 tmp 中合法的 .wav 文件（按文件名排序）
    wav_files = sorted([
        f for f in os.listdir(tmp_dir)
        if is_valid_wav(os.path.join(tmp_dir, f))
    ])
    if not wav_files:
        print("tmp 中没有合法的 .wav 文件")
        shutil.rmtree(tmp_dir)
        print("清除了 tmp 目录")
        return

    # 打开第一个文件，作为基础参数来源
    first_path = os.path.join(tmp_dir, wav_files[0])
    with wave.open(first_path, 'rb') as wf:
        params = wf.getparams()
        frames = [wf.readframes(wf.getnframes())]
    # 遍历后续文件并追加数据（确保参数一致）
    for filename in wav_files[1:]:
        file_path = os.path.join(tmp_dir, filename)
        with wave.open(file_path, 'rb') as wf:
            if wf.getparams()[:3] != params[:3]:  # 检查通道数、采样宽度、采样率
                print(f"跳过不兼容的文件: {filename}")
                continue
            frames.append(wf.readframes(wf.getnframes()))
    # 写入合并后的 WAV 文件
    with wave.open(output_file_path, 'wb') as out_wav:
        out_wav.setparams(params)
        for data in frames:
            out_wav.writeframes(data)

    print(f"合并完成，共合并 {len(frames)} 个文件，输出到: {output_file_path}")
    # 清除 tmp 目录
    shutil.rmtree(tmp_dir)
    print("清除了 tmp 目录")
    ###进行语言基本特征提取
    output_file_path="uploads/audios/recording.wav"
    feature=selfmodel.extract_features(output_file_path)
    print("语言特征:",feature)
    voice_tip=[]
    if feature["energy_mean"]<0.05:
        print("音量过小")
        voice_tip.append("音量过小")
    elif feature["energy_mean"]>0.2:
        print("音量过高")
        voice_tip.append("音量过高")
    else:
        print("音量正常")
        voice_tip.append("音量过高")
    if feature["energy_variation"]<0.08:
        print("说话较为平淡，请带有情感")
        voice_tip.append("说话较为平淡，请带有情感")
    elif feature["energy_variation"]>0.11:
        print("你说话太快了")
        voice_tip.append("你说话太快了")
    else:
        print("说话很有吸引力")
        voice_tip.append("说话很有吸引力")
    ###进行表情识别和获取文字
    text,emo_cnt,emo_suggest=emo_model.extract_emo(output_file_path)
    print("识别的表情:",emo_cnt)
    print("识别的文字:",text)
    ###进行系统化语音评分
    prompt1=f"""{text}目标:这是一段面试记录。你重点要从中提取与表达相关的内容，然后给对应的指标加分，并给出建议。评分指标:{voice_mark},0~100分，并且打分要有依据，依据不足就先打0分。输出内容:先输出打分后的分数文件,是严格的双引号json格式，然后针对表达方面给出一点建议。输出参考格式1:
    分数:xxx.建议:["1.xxx”,"2.xxx","3.xxx"]输出参考格式2: 分数:xxx.建议:["1.xxx","2.xxx"]
"""
    voice2_res=spark.chat(prompt1)
    print("获取语音结果:",voice2_res)
    voice_score,voice_suggest=parse_i_chat(voice2_res)
    print("语音评分:",voice_score)
    print("语音建议:",voice_suggest)
    return{
        "voice1_res":feature,
        "voice_tip":voice_tip,
        "emo_cnt":emo_cnt,
        "emo_suggest":emo_suggest,
        "voice2_res":voice2_res,
        "voice_score":voice_score,
        "voice_suggest":voice_suggest,
    }

#使用http请求步进每一次对话
from interview import interviewer
vv=interviewer()
class step_interviewModel(BaseModel):
    user_input:Any
    is_begin:bool
@app.post("/api/interview/step")
async def step_interview(request: step_interviewModel):
    #print("开始步进面试")
    user_input=request.user_input
    print("用户输入:",user_input)
    try:
        if request.is_begin:
            vv.reset()
            #检查类型是否正确
            if not isinstance(user_input, dict):
                user_input=json.loads(user_input)
            vv.resume=user_input#此时是简历
            chat=f"{vv.resume}你好，这是我的简历"
        else:
            if isinstance(user_input, str):
                chat=user_input
            else:
                raise TypeError("类型错误")

        response, messages_history, is_end = vv.run(chat)
        if is_end:
            report = vv.parse_res(response)
            print("生成总结:", report)
            #print("对话历史:", messages_history)
            #print("AI回复:", response)

            #这里的report['report']已经是一个dict类型了
            # try:
            #     json_str = json.dumps(report['report'], ensure_ascii=False)
            # except Exception as e:
            #     print("解析失败:", e)
            #     raise TypeError("类型错误:",str(e))
            # print("json_str", json_str)
            print("对话结束")
            return{
            "code": 200,
            "data": {
                "request": response,
                "messages_history": messages_history,
                "is_end": is_end,
                **report  # 正确解包report字典
                }
            }
        else:
            print("AI回复:", response)
            parsed = vv.parse_chat(response)  # 先获取完整的解析结果
            response = parsed["response"]  # 获取实际回复内容
            tmp_score = parsed["score"]  # 获取评分
            if tmp_score is not None :
                print("得分:", tmp_score)
            return {
            "code": 200,
            "data": {
                "request": response,
                "messages_history": messages_history,
                "is_end": is_end,
                "is_begin":request.is_begin,
                "tmp_score": tmp_score
            }
        }

    except Exception as e:
        print("错误:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/audio")
async def upload_audio(file: UploadFile = File(...)):
    # 获取原始文件名（例如 record.wav）
    filename = file.filename
    _, f_extension = os.path.splitext(filename)  # 获取扩展名，如 ".wav"
    save_dir="tmp"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # 自动生成不重复的文件名
    cnt = 0
    while True:
        f_name = f"recording{cnt}{f_extension}"
        f_path = os.path.join(save_dir, f_name)
        if os.path.exists(f_path):
            cnt += 1
        else:
            break

    print("新文件将保存到", f_path)

    # 保存文件内容到目标路径
    with open(f_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if not is_valid_wav(f_path):
        print("wav文件格式错误")
        raise HTTPException(status_code=400, detail="wav文件格式错误")
        #await convert_to_wav(f_path)

    return {"message": "上传成功", "code": 200}

def save_base64_to_file(base64_data: str, save_dir: str) -> str:
    #print("开始存储",base64_data)
    # 去除 data:image/png;base64, 前缀
    if base64_data.startswith("data:image"):
        base64_data = base64_data.split(",")[1]

    img_bytes = base64.b64decode(base64_data)
    filename = f"{uuid.uuid4().hex}.png"
    file_path = os.path.join(save_dir, filename)

    with open(file_path, "wb") as f:
        f.write(img_bytes)
    return file_path
from vedio1 import imgChat,video1_run
from vedio2 import video2_run
imgChat=imgChat()
class upload_imgModel(BaseModel):
    img:Any
    flag:int#1为关键帧 2为间隔帧
@app.post("/api/upload/img")
async def upload_img(request: upload_imgModel):
    Img_UploadDIR="uploads/img"
    img_path = save_base64_to_file(request.img, Img_UploadDIR)
    print(f"生成临时图片:",request.flag,{img_path})
    img_score={"外部指标":[{ "value": 0,"name": '精神风貌' },{"value":0,"name":'面试准备程度'},{ "value": 0, "name": '行为举止' }],"软实力":[{"value":0,"name":"表达能力"}]}
    if request.flag==1:
        #print("关键帧:",request.img)
        prompt = """这是一张图片，
        第一题：请输出与你的判断最相近的那一项。A.图片中没有出现人物的手臂 B.图片中人物的手靠近头部上方，可能在挠头 C.图片中出现了人物的手，但是离头部比较远，停放在底部桌面附近 D.图片中出现了人物的手,但是悬停在半空中，似乎在比划什么 E.图片中的人物的手贴近脸部，可能脸部某个位置有点痒 F.图片中人物手托下巴或者贴近鼻子，也许这是其正在思考的习惯性动作 
        第二题：请输出与你判断最相近的一项。
        A.图片中人物闭上了眼镜 B.图片中人物很懒散，神情恍惚 C图片中人物很专注 D.图片中人物很高兴、兴奋 E.图片中人物看向了别处
            """
        #text = [{"role": "user", "content": str(base64.b64encode(imagedata), 'utf-8'), "content_type": "image"}]
        #baseData=str(base64.b64encode(open(img_path,'rb').read()))
        with open(img_path, 'rb') as f:
            baseData = base64.b64encode(f.read()).decode('utf-8')
        question = [{"role": "user", "content": baseData,"content_type": "image"},{"role": "user", "content": prompt}]
        video1_run(question,imgChat)
        print("ai回复:",imgChat.ans)
        res=[]
        for i in imgChat.ans:
            if i.isalpha() and i.isupper():
                res.append(i)
        ans1=res[0]
        suggest=[]
        if ans1 in "BEF":
            img_score["外部指标"][0]["value"]-=8
            img_score["外部指标"][1]["value"]-=5
            img_score["外部指标"][2]["value"]-=10
            if len(suggest)<3:
                suggest.append("请注意举止")
        if ans1 in "D":
            img_score["外部指标"][0]["value"]+=5
            img_score["外部指标"][1]["value"]+=3
            img_score["软实力"][0]["value"]+=5
        ans2=res[1]
        if ans2 in "AB":
            img_score["外部指标"][2]["value"] -= 10
            if len(suggest)<3:
                suggest.append("请打起精神")
        if ans2 in "E":
            img_score["外部指标"][1]["value"] -= 5
            img_score["外部指标"][2]["value"] -= 8
            if len(suggest)<3:
                suggest.append("请专注")
        if ans2 in "CD":
            img_score["外部指标"][0]["value"]+=5
            img_score["外部指标"][1]["value"]+=8
            if len(suggest)<3:
                if ans2=="C":
                    suggest.append("请专注")
                if ans2=="D":
                    suggest.append("你给面试官留下的印象很好·")
        print("img_score:",img_score)
        imgChat.ans=""
        return {
            "info":suggest,
            "img_score":img_score
        }
    elif request.flag==2:
        advice=[]
        try:
            advice=video2_run(img_path)
        except RuntimeError as e:
            advice.append(str(e))
            print(str(e))
        except Exception as e:
            print("错误:", e)
            raise HTTPException(status_code=500, detail=str(e))
        print("img_score",img_score)
        return{
            "info":advice,
            "img_score":img_score
        }
class HistoryModel(BaseModel):
    user_id: int
    mode: int
    resource: Dict[str, Any]  # 更明确：JSON 对象
    total_score: float
    score_detail: Dict[str, Any]  # 也是 JSON 对象
    message: List[Any]
    advice: List[str]
    job:str
# 捕获 422 校验错误
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("🔥 422 参数校验失败！")
    print("请求路径:", request.url.path)
    print("错误详情:", exc.errors())
    #print("请求体:", await request.body())  # 原始 body（bytes）

    # 你也可以选择返回标准错误响应
    return await request_validation_exception_handler(request, exc)
@app.post("/api/history/save")
async def save_history(request:HistoryModel):
    tz = timezone(timedelta(hours=8))
    created_time=datetime.now(tz)#东8区时间
    print(created_time)
    try:
        #手动将python对象转为json字符串
        db_manager.insert("history", {
            "user_id": request.user_id,
            "mode": request.mode,
            "job":request.job,
            "resource": json.dumps(request.resource),
            "total_score": request.total_score,
            "score_detail": json.dumps(request.score_detail),
            "message": json.dumps(request.message),
            "advice": json.dumps(request.advice),
            "created_time": created_time
        })
        return {
            "code": 200,
            "message": "保存成功"
        }
    except Exception as e:
        print("保存历史失败:",str(e))
        raise HTTPException(status_code=500,detail="保存历史失败:"+str(e))
@app.post("/api/history/delete")
async def delete_history(id:int):
    try:
        db_manager.delete("history",{"id":id})
        return{
            "code":200,
            "message":"删除成功"
        }
    except Exception as e:
        print("删除历史失败:", str(e))
        raise HTTPException(status_code=500, detail="删除历史失败:" + str(e))

@app.get("/api/history/query")
async def query_history(id:int):
    try:
        res = db_manager.select("history", conditions={"id": id})
        if res:
            row = res[0]
            print("查询成功：",row)
        else:
            return {}
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "mode": row["mode"],
            "job":row["job"],
            "resource": json.loads(row["resource"]),
            "total_score": row["total_score"],
            "score_detail": json.loads(row["score_detail"]),
            "message": json.loads(row["message"]),
            "advice": json.loads(row["advice"]),
            "created_time": row["created_time"].strftime("%Y-%m-%d %H:%M")
        }
    except Exception as e:
        print("查询历史失败:", str(e))
        raise HTTPException(status_code=500, detail="查询历史失败:" + str(e))
@app.get("/api/history/get")
async def get_history(user_id:int):
    try:
        res = db_manager.select("history", conditions={"user_id": user_id})
        print("查询到",len(res),"条历史记录")
        return{
            "history":res
        }
    except Exception as e:
        print("查询历史失败:", str(e))
        return{
            "history":[]
        }
@app.post("/api/interview/upload")
async def interview_upload(
    resume: UploadFile = File(...),
    video: Optional[UploadFile] = File(None),
    user_id: int = Form(...),
    mode: int = Form(...),
):
    text_url=""
    video_url=""
    audio_url=""
    try:
        text_url=file_manager.upload_file(resume.file,resume.filename,user_id)
        print("成功上传简历:",text_url)

        #bucket=file_manager.connect()
        #避免文件名重复
        unique_audio_name = f"{uuid.uuid4().hex}.wav"
        with open("uploads/audios/recording.wav", "rb") as f:
            audio_url=file_manager.upload_file(f,unique_audio_name,user_id)
        print("成功上传音频文件:",audio_url)
        # cnt=0
        # while file_manager.is_exists2(bucket,user_id,f"recording{cnt}.wav"):
        #     cnt+=1
        # print(f"将上传音频文件recording{cnt}.wav")
        # with open("uploads/audios/recording.wav") as f:
        #     audio_url=file_manager.upload_file(f,f"recording{cnt}.wav",user_id)
        if os.path.exists("audio/recording.wav"):
            os.remove("audio/recording.wav")
            print("已经成功移除文件:","audio/recording.wav")
        if mode==1:
            video_url=file_manager.upload_file(video.file,video.filename,user_id)
            print("已成功上传视频文件文件:",video_url)

    except Exception as e:
        print("上传错误:",str(e))
    return{
        "textUrl":text_url,
        "videoUrl":video_url,
        "audioUrl":audio_url
    }
@app.post("/api/interview/init")
async def interview_init():
    # 删除 tmp 目录
    if os.path.exists("tmp"):
        shutil.rmtree("tmp")

    # 清空并重新创建 uploads/img 目录
    img_path = os.path.join("uploads", "img")
    if os.path.exists(img_path):
        shutil.rmtree(img_path)
    os.makedirs(img_path, exist_ok=True)

    # 清空并重新创建 uploads/audios 目录
    audio_path = os.path.join("uploads", "audios")
    if os.path.exists(audio_path):
        shutil.rmtree(audio_path)
    os.makedirs(audio_path, exist_ok=True)
    #初始化interview
    vv.reset()
    return{
        "code":200,
        "message":"初始化成功"
    }
































# 社区相关的模型
class PostCreate(BaseModel):
    title: str
    content: str
    post_type: str
    tags: Optional[str] = None

class CommentCreate(BaseModel):
    post_id: int
    content: str

class ResourceLinkCreate(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    category: str
    tags: Optional[str] = None
async def get_current_user(request: Request) -> int:
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="未提供身份凭证")

    # 示例：从 token 中解析 user_id
    try:
        payload = jwt.decode(token, "your-secret", algorithms=["HS256"])
        return payload["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="身份验证失败")
# 社区相关的API路由
@app.post("/api/community/posts")
async def create_post(post: PostCreate, user_id: int = Depends(get_current_user)):
    """创建帖子"""
    try:
        query = """
            INSERT INTO community_posts 
            (user_id, title, content, post_type, tags)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (user_id, post.title, post.content, post.post_type, post.tags)
        
        db_manager.cursor.execute(query, values)
        db_manager.conn.commit()
        post_id = db_manager.cursor.lastrowid
        
        return {
            "code": 200,
            "data": {
                "post_id": post_id
            }
        }
    except Exception as e:
        print(f"创建帖子失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/community/posts")
async def get_posts(
    post_type: Optional[str] = None,
    tags: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
):
    """获取帖子列表"""
    try:
        conditions = []
        values = []
        
        if post_type:
            conditions.append("post_type = %s")
            values.append(post_type)
        
        if tags:
            conditions.append("FIND_IN_SET(%s, tags)")
            values.append(tags)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 获取总数
        count_query = f"SELECT COUNT(*) as total FROM community_posts WHERE {where_clause}"
        db_manager.cursor.execute(count_query, tuple(values))
        total = db_manager.cursor.fetchone()["total"]
        
        # 获取帖子列表
        query = f"""
            SELECT p.*, u.username
            FROM community_posts p
            JOIN users u ON p.user_id = u.id
            WHERE {where_clause}
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """
        values.extend([page_size, (page - 1) * page_size])
        
        db_manager.cursor.execute(query, tuple(values))
        posts = db_manager.cursor.fetchall()
        
        return {
            "code": 200,
            "data": {
                "total": total,
                "posts": posts,
                "page": page,
                "page_size": page_size
            }
        }
    except Exception as e:
        print(f"获取帖子列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/community/posts/{post_id}")
async def get_post_detail(post_id: int):
    """获取帖子详情"""
    try:
        # 更新浏览量
        db_manager.cursor.execute(
            "UPDATE community_posts SET views = views + 1 WHERE id = %s",
            (post_id,)
        )
        
        # 获取帖子信息
        query = """
            SELECT p.*, u.username
            FROM community_posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = %s
        """
        db_manager.cursor.execute(query, (post_id,))
        post = db_manager.cursor.fetchone()
        
        if not post:
            raise HTTPException(status_code=404, detail="帖子不存在")
        
        # 获取评论
        comment_query = """
            SELECT c.*, u.username
            FROM post_comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at DESC
        """
        db_manager.cursor.execute(comment_query, (post_id,))
        comments = db_manager.cursor.fetchall()
        
        db_manager.conn.commit()
        
        return {
            "code": 200,
            "data": {
                "post": post,
                "comments": comments
            }
        }
    except Exception as e:
        print(f"获取帖子详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/community/comments")
async def create_comment(comment: CommentCreate, user_id: int = Depends(get_current_user)):
    """创建评论"""
    try:
        query = """
            INSERT INTO post_comments 
            (post_id, user_id, content)
            VALUES (%s, %s, %s)
        """
        values = (comment.post_id, user_id, comment.content)
        
        db_manager.cursor.execute(query, values)
        db_manager.conn.commit()
        
        return {
            "code": 200,
            "data": {
                "comment_id": db_manager.cursor.lastrowid
            }
        }
    except Exception as e:
        print(f"创建评论失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/community/resources")
async def create_resource_link(resource: ResourceLinkCreate):
    """创建资源链接"""
    try:
        query = """
            INSERT INTO resource_links 
            (title, url, description, category, tags)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            resource.title,
            resource.url,
            resource.description,
            resource.category,
            resource.tags
        )
        
        db_manager.cursor.execute(query, values)
        db_manager.conn.commit()
        
        return {
            "code": 200,
            "data": {
                "resource_id": db_manager.cursor.lastrowid
            }
        }
    except Exception as e:
        print(f"创建资源链接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/community/resources")
async def get_resource_links(
    category: Optional[str] = None,
    tags: Optional[str] = None
):
    """获取资源链接列表"""
    try:
        conditions = []
        values = []
        
        if category:
            conditions.append("category = %s")
            values.append(category)
        
        if tags:
            conditions.append("FIND_IN_SET(%s, tags)")
            values.append(tags)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
            SELECT *
            FROM resource_links
            WHERE {where_clause}
            ORDER BY clicks DESC, created_at DESC
        """
        
        db_manager.cursor.execute(query, tuple(values))
        resources = db_manager.cursor.fetchall()
        
        return {
            "code": 200,
            "data": {
                "resources": resources
            }
        }
    except Exception as e:
        print(f"获取资源链接列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/community/resources/{resource_id}/click")
async def record_resource_click(resource_id: int):
    """记录资源点击"""
    try:
        query = "UPDATE resource_links SET clicks = clicks + 1 WHERE id = %s"
        db_manager.cursor.execute(query, (resource_id,))
        db_manager.conn.commit()
        
        return {
            "code": 200,
            "data": None
        }
    except Exception as e:
        print(f"记录资源点击失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/community/posts/{post_id}/like")
async def like_post(post_id: int, user_id: int = Depends(get_current_user)):
    """点赞帖子"""
    try:
        query = "UPDATE community_posts SET likes = likes + 1 WHERE id = %s"
        db_manager.cursor.execute(query, (post_id,))
        db_manager.conn.commit()
        
        return {
            "code": 200,
            "data": None
        }
    except Exception as e:
        print(f"点赞帖子失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/community/comments/{comment_id}/like")
async def like_comment(comment_id: int, user_id: int = Depends(get_current_user)):
    """点赞评论"""
    try:
        query = "UPDATE post_comments SET likes = likes + 1 WHERE id = %s"
        db_manager.cursor.execute(query, (comment_id,))
        db_manager.conn.commit()
        
        return {
            "code": 200,
            "data": None
        }
    except Exception as e:
        print(f"点赞评论失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    tttt="""{
  "硬实力": [
    {"value": 80, "name": "专业知识"},
    {"value": 75, "name": "技术能力"},
    {"value": 60, "name": "经验积累"}
  ],
  "软实力": [
    {"value": 70, "name": "团队协作"},
    {"value": 60, "name": "表达能力"}
  ],
  "潜力": [
    {"value": 65, "name": "学习能力"},
    {"value": 50, "name": "创新能力"},
    {"value": 60, "name": "适应能力"}
  ],
  "文化水平": [
    {"value": 0, "name": "伦理抉择"},
    {"value": 0, "name": "价值观"}
  ],
  "外部指标": [
    {"value": 70, "name": "面试准备程度"},
    {"value": 80, "name": "专业度"}
  ]
}
    """
    a,b=parse_i_chat(tttt)
    print(a,b)

