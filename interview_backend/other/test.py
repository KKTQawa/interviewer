import json
import re
import os
import sys
from typing import Any,List,Dict
from pathlib import Path
from dotenv import load_dotenv
import shutil #更强大的路径处理
import base64
import uuid
from datetime import datetime, timezone,timedelta
from fastapi import FastAPI, HTTPException, Request, status, UploadFile, File,Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import request_validation_exception_handler

current=str(Path(__file__).parent)
print(current)
sys.path.append(str(Path(__file__).parent))

from database import DatabaseManager
from FileManager import FileManager
from spark_client import SparkClient

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from config import (
    UPLOAD_DIR, ALLOWED_EXTENSIONS, SECRET_KEY as CONFIG_SECRET_KEY,
    ALGORITHM as CONFIG_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES as CONFIG_TOKEN_EXPIRE,
    SPARK_CONFIG
)
load_dotenv(".env")
load_dotenv(".env.secret")#叠加加载

SECRET_KEY = os.getenv("SECRET_KEY") or CONFIG_SECRET_KEY
ALGORITHM = os.getenv("ALGORITHM") or CONFIG_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or CONFIG_TOKEN_EXPIRE)
REFRESH_TOKEN_EXPIRE_MINUTES =int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))
OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")
spark=SparkClient()
file_manager = FileManager(OSS_ACCESS_KEY_ID,OSS_ACCESS_KEY_SECRET,"interviewresource","https://oss-cn-beijing.aliyuncs.com/","cn-beijing",spark)
db_manager = DatabaseManager()
from pydantic import BaseModel, Field

class HistoryModel(BaseModel):
    user_id: int
    mode: int
    resource: Dict[str, Any]  # 更明确：JSON 对象
    total_score: float
    score_detail: Dict[str, Any]  # 也是 JSON 对象
    message: List[Any]
    advice: List[str]
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

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: int = Form(...)
):
    try:
        if not file_manager.allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        file_manager.upload_file(file.file,file.filename,user_id)
    except Exception as e:
        print("上传文件失败:", str(e))
        raise HTTPException(status_code=500, detail="上传文件失败:" + str(e))

if __name__ == "__main__":

    bucket = file_manager.connect()
    file_name="demo2-picture1.jpg"
    print(file_manager.delete_file(9,file_name))
    # with open(f"tmp/{file_name}", "rb") as f:
    #     result = bucket.put_object(f"image/{file_name}", f)
    # if result.status == 200:
    #     print("yes")
    # else:
    #     print({result.status})


