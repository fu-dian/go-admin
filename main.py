from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
import jwt
import bcrypt
import os
import json
import asyncio
from aiohttp import ClientSession
from dotenv import load_dotenv
from openai import OpenAI
import fitz
import docx
import re
import faiss
import numpy as np

# 加载环境变量
load_dotenv()

# 配置数据库连接
# @mysql8
# @localhost:3306/
DATABASE_URL = f"mysql+mysqlconnector://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '123456')}@localhost/{os.getenv('DB_NAME', 'go_user_admin')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 定义用户模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False, default="user")

# 定义文件模型
class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, nullable=True)

# 定义对话历史模型
class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    role = Column(String(20), nullable=False)  # user 或 assistant
    content = Column(Text, nullable=False)
    timestamp = Column(Integer, nullable=False)  # 时间戳
    session_id = Column(String(50), nullable=False)  # 会话ID，用于区分不同的对话

# 尝试删除并重新创建数据库表（仅用于开发环境）
try:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功")
except Exception as e:
    print(f"警告: 数据库连接失败，某些功能可能无法使用: {e}")

# 依赖项：获取数据库会话
def get_db():
    try:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except Exception as e:
        print(f"警告: 数据库连接失败: {e}")
        yield None

# Pydantic 模型
class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    token: Optional[str] = None

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: Optional[str] = None

class DeepRequest(BaseModel):
    message: str

class ImageRecognitionRequest(BaseModel):
    image_url: str
    prompt: str = "这是什么"

class ResponseModel(BaseModel):
    code: int
    msg: str
    data: Optional[Any] = None

# 生成JWT令牌
def generate_token(user: User):
    payload = {
        "id": user.id,
        "username": user.username,
        "role": user.role
    }
    return jwt.encode(payload, os.getenv('JWT_SECRET', 'your-secret-key-123456789012345678901234567890'), algorithm="HS256")

# 验证JWT令牌
def verify_token(token: str):
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET', 'your-secret-key-123456789012345678901234567890'), algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None

# 认证中间件
def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    
    token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
    if not token:
        return None
    
    payload = verify_token(token)
    if not payload:
        return None
    
    user = db.query(User).filter(User.id == payload["id"]).first()
    return user

# 创建默认用户
def create_default_user(db: Session):
    try:
        count = db.query(User).count()
        if count == 0:
            hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt(10))
            default_user = User(
                username="admin",
                password=hashed_password.decode('utf-8'),
                role="user"
            )
            db.add(default_user)
            db.commit()
            print("默认用户创建成功: admin / admin123")
    except Exception as e:
        print(f"创建默认用户失败: {e}")

# 根据用户角色获取系统提示
def get_system_prompt_by_role(role: str):
    role_prompts = {
        "teacher": "你是一位知识渊博的教师，擅长解答各种学术问题，耐心细致地引导学生学习。",
        "doctor": "你是一位专业的医生，能够提供健康咨询和医疗建议，语气温和专业。",
        "engineer": "你是一位经验丰富的工程师，擅长解决技术问题，提供专业的技术建议。",
        "student": "你是一位勤奋好学的学生，对知识充满好奇，积极向他人请教。"
    }
    return role_prompts.get(role, "你是一位友好的AI助手，能够回答各种问题，提供有用的信息和建议。")

# 提取文件内容
def extract_file_content(file: UploadFile) -> str:
    filename = file.filename
    content = ""
    
    if filename.endswith('.pdf'):
        try:
            pdf_document = fitz.open(stream=file.file.read(), filetype="pdf")
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                content += page.get_text()
        except Exception as e:
            print(f"处理PDF文件失败: {e}")
    
    elif filename.endswith('.docx'):
        try:
            doc = docx.Document(file.file)
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
        except Exception as e:
            print(f"处理Word文件失败: {e}")
    
    else:
        try:
            content = file.file.read().decode('utf-8')
        except Exception as e:
            print(f"处理文本文件失败: {e}")
    
    return content

# ============================
# 用户隔离的向量库变量（key: user_id, value: 向量库）
# ============================
user_vector_dbs = {}  # {user_id: {"index": faiss_index, "file_chunks": []}}
VECTOR_DIM = 128

# ============================
# 初始化指定用户的向量库
# ============================
def init_user_vector_db(user_id: Optional[int] = None):
    """初始化指定用户的向量库，如果user_id为None则使用默认库"""
    global user_vector_dbs
    
    # 使用字符串作为key，避免None的问题
    key = str(user_id) if user_id is not None else "default"
    
    if key not in user_vector_dbs:
        try:
            index = faiss.IndexFlatL2(VECTOR_DIM)
            user_vector_dbs[key] = {
                "index": index,
                "file_chunks": []
            }
            print(f"[OK] 为用户 {key} 初始化向量库成功")
        except Exception as e:
            print(f"[ERROR] 为用户 {key} 初始化向量库失败: {e}")
            return None
    
    return user_vector_dbs[key]

# ============================
# 文本转向量（无encode，纯本地）
# ============================
def text_to_vector(text):
    np.random.seed(hash(text) % 100000)
    return np.random.rand(VECTOR_DIM).astype("float32")

# ============================
# 处理文件（用户隔离版）
# ============================
def process_file(file: UploadFile, user_id: Optional[int] = None, db: Session = None):
    content = extract_file_content(file)
    if not content:
        return False

    # 获取或创建用户的向量库
    user_db = init_user_vector_db(user_id)
    chunks = split_text(content)

    if user_db:
        try:
            index = user_db["index"]
            for chunk in chunks:
                vec = text_to_vector(chunk)
                index.add(np.array([vec]))
                user_db["file_chunks"].append({
                    "content": chunk,
                    "user_id": user_id
                })
            print(f"[OK] 成功添加 {len(chunks)} 条文本到用户 {user_id} 的向量库")
        except Exception as e:
            print(f"添加到向量索引失败: {e}")
    else:
        print("向量数据库未初始化，跳过向量索引")

    # 尝试保存到数据库（可选）
    if db:
        try:
            new_file = File(
                filename=file.filename,
                content=content,
                user_id=user_id
            )
            db.add(new_file)
            db.commit()
            print(f"[OK] 文件保存到数据库成功")
        except Exception as e:
            print(f"[WARN] 保存文件到数据库失败（不影响向量库）: {e}")
    else:
        print(f"[INFO] 数据库不可用，跳过文件持久化")

    # 只要向量库添加成功，就返回True
    return True

# 分割文本为块
def split_text(text: str, chunk_size: int = 500) -> List[str]:
    sentences = re.split(r'[。！？.!?]', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + "。"
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence + "。"
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

# ============================
# 检索相关文本（用户隔离版）
# ============================
def retrieve_relevant_text(query: str, user_id: Optional[int] = None, top_k: int = 3) -> List[str]:
    """从指定用户的向量库中检索相关文本"""
    try:
        user_db = init_user_vector_db(user_id)
        if user_db is None:
            print(f"用户 {user_id} 的向量数据库未初始化")
            return []
    except Exception as e:
        print(f"初始化向量数据库失败: {e}")
        return []
    
    try:
        index = user_db["index"]
        file_chunks = user_db["file_chunks"]
        
        # 如果该用户没有上传过文件，返回空列表
        if len(file_chunks) == 0:
            print(f"用户 {user_id} 的向量库为空")
            return []
        
        query_embedding = text_to_vector(query)
        distances, indices = index.search(np.array([query_embedding]), min(top_k, len(file_chunks)))
        
        relevant_texts = []
        for idx in indices[0]:
            if idx < len(file_chunks):
                relevant_texts.append(file_chunks[idx]["content"])
        
        print(f"[OK] 从用户 {user_id} 的向量库中检索到 {len(relevant_texts)} 条相关文本")
        return relevant_texts
    except Exception as e:
        print(f"检索相关文本失败: {e}")
        return []

# 初始化FastAPI应用
app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动时创建默认用户
@app.on_event("startup")
async def startup_event():
    try:
        db = SessionLocal()
        create_default_user(db)
        db.close()
    except Exception as e:
        print(f"启动时创建默认用户失败: {e}")

# 健康检查接口
@app.get("/health")
async def health_check():
    return ResponseModel(code=200, msg="ok", data=None)
@app.get("/api/auth/me")
 # 1. 从数据库查询所有用户
async def get_user_info( db: Session = Depends(get_db)):
    # 1. 从数据库查询所有用户
    user_list = db.query(User).all()

    # 2. 把数据库对象转成普通字典列表
    data = []
    for user in user_list:
        data.append({
            "id": user.id,
            "username": user.username,
            "role": user.role
        })

    # 3. 返回给前端
    return ResponseModel(
        code=200,
        msg="获取用户列表成功",
        data=data  # 这里放真实数据库数据
    )
# 删除用户
@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    # 找到用户
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return ResponseModel(code=404, msg="用户不存在", data=None)

    # 删除
    db.delete(user)
    db.commit()

    return ResponseModel(code=200, msg="删除成功", data=None)
# 注册接口
@app.post("/api/v1/auth/register", response_model=ResponseModel)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        if not db:
            return ResponseModel(code=503, msg="数据库服务不可用", data=None)
        
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            return ResponseModel(code=400, msg="用户名已存在", data=None)
        
        hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt(10))
        
        new_user = User(
            username=user_data.username,
            password=hashed_password.decode('utf-8'),
            role=user_data.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        token = generate_token(new_user)
        
        return ResponseModel(
            code=201,
            msg="注册成功",
            data={
                "id": new_user.id,
                "username": new_user.username,
                "role": new_user.role,
                "token": token
            }
        )
    except Exception as e:
        print(f"注册失败: {e}")
        return ResponseModel(code=500, msg="注册失败", data=None)

# 登录接口
@app.post("/api/v1/auth/login", response_model=ResponseModel)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        if not db:
            return ResponseModel(code=503, msg="数据库服务不可用", data=None)
        
        user = db.query(User).filter(User.username == user_data.username).first()
        if not user:
            return ResponseModel(code=401, msg="用户名或密码错误", data=None)
        
        if not bcrypt.checkpw(user_data.password.encode('utf-8'), user.password.encode('utf-8')):
            return ResponseModel(code=401, msg="用户名或密码错误", data=None)
        
        token = generate_token(user)
        
        return ResponseModel(
            code=200,
            msg="登录成功",
            data={
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "token": token
            }
        )
    except Exception as e:
        print(f"登录失败: {e}")
        return ResponseModel(code=500, msg="登录失败", data=None)

# 获取用户信息接口


# 调用AI API（流式）
async def call_ai_api_stream(message: str, user_role: str = "user", user_id: Optional[int] = None, messages: Optional[List[Dict]] = None, db: Optional[Session] = None, session_id: Optional[str] = None):
    api_key = os.getenv('AGENT_API_KEY')
    if not api_key:
        yield "data: 错误: 未设置AGENT_API_KEY环境变量\n\n"
        yield "data: [DONE]\n\n"
        return
    
    try:
        print(f"开始处理请求: {message} (用户ID: {user_id})")
        
        # 根据用户ID检索相关文本
        relevant_texts = retrieve_relevant_text(message, user_id)
        print(f"检索到的相关文本数量: {len(relevant_texts)}")
        
        system_prompt = get_system_prompt_by_role(user_role)
        
        if relevant_texts:
            context = "\n".join(relevant_texts)
            system_prompt += f"\n\n根据以下相关信息回答问题：\n{context}"
        else:
            print("没有检索到相关文本，使用基本系统提示")
        
        # 构建消息列表
        req_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 如果提供了完整的消息列表，使用它
        if messages:
            req_messages.extend(messages)
        else:
            req_messages.append({"role": "user", "content": message})
        
        req_body = {
            "model": "qwen-plus",
            "messages": req_messages,
            "temperature": 0.7,
            "stream": True,
            "enable_search": True,
            "search_options": {
            "enable_search_intent": True
    }
        }
        
        print("准备发送API请求")
        
        async with ClientSession() as session:
            try:
                async with session.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json=req_body,
                    timeout=30.0
                ) as resp:
                    print(f"API响应状态码: {resp.status}")
                    if not resp.ok:
                        error_msg = f"AI API返回错误状态码: {resp.status}"
                        print(f"错误: {error_msg}")
                        yield f"data: 错误: {error_msg}\n\n"
                        yield "data: [DONE]\n\n"
                        return
                    
                    buffer = ""
                    ai_response = ""  # 累积AI的响应内容
                    async for chunk in resp.content:
                        buffer += chunk.decode('utf-8')
                        lines = buffer.split("\n")
                        buffer = lines.pop()
                        
                        for line in lines:
                            trimmed_line = line.strip()
                            if not trimmed_line:
                                continue
                            
                            if trimmed_line.startswith("event:"):
                                continue
                            
                            if trimmed_line.startswith("data:"):
                                data = trimmed_line[5:]
                                
                                if data == "[DONE]":
                                    # 保存AI的响应到数据库
                                    if db and session_id and ai_response:
                                        try:
                                            new_conversation = Conversation(
                                                user_id=user_id,
                                                role="assistant",
                                                content=ai_response,
                                                timestamp=int(asyncio.get_event_loop().time()),
                                                session_id=session_id
                                            )
                                            db.add(new_conversation)
                                            db.commit()
                                            print("AI响应保存成功")
                                        except Exception as e:
                                            print(f"保存AI响应失败: {e}")
                                
                                try:
                                    stream_resp = json.loads(data)
                                    if (
                                        stream_resp.get("choices") and
                                        len(stream_resp["choices"]) > 0 and
                                        stream_resp["choices"][0].get("delta") and
                                        stream_resp["choices"][0]["delta"].get("content")
                                    ):
                                        content = stream_resp["choices"][0]["delta"]["content"]
                                        ai_response += content  # 累积响应内容
                                        yield f"data: {content}\n\n"
                                except Exception as e:
                                    print(f"解析JSON错误: {e}")
                                    continue
            except asyncio.TimeoutError:
                print("API请求超时")
                yield "data: 错误: API请求超时\n\n"
                yield "data: [DONE]\n\n"
                return
            except Exception as e:
                print(f"发送API请求失败: {e}")
                yield f"data: 错误: 发送API请求失败: {str(e)}\n\n"
                yield "data: [DONE]\n\n"
                return
        
        yield "data: [DONE]\n\n"
    except Exception as e:
        print(f"请求失败: {e}")
        yield f"data: 错误: {str(e)}\n\n"
        yield "data: [DONE]\n\n"

# AI聊天接口
@app.post("/api/v1/agent/chat")
async def chat(request: ChatRequest, req: Request, db: Session = Depends(get_db)):
    try:
        user_message = ""
        for msg in request.messages:
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            return ResponseModel(code=400, msg="请提供用户消息", data=None)
        
        user_role = "user"
        user_id = None
        auth_header = req.headers.get("Authorization")
        if auth_header and db:
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
            if token:
                try:
                    payload = verify_token(token)
                    if payload:
                        user = db.query(User).filter(User.id == payload["id"]).first()
                        if user:
                            user_role = user.role
                            user_id = user.id
                except Exception as e:
                    print(f"警告: 获取用户信息失败: {e}")
        
        # 生成或使用会话ID
        session_id = request.session_id
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
        
        # 加载历史对话
        history_messages = []
        if db:
            try:
                # 获取最近的10条对话记录
                conversations = db.query(Conversation).filter(
                    Conversation.session_id == session_id
                ).order_by(Conversation.timestamp).limit(10).all()
                
                for conv in conversations:
                    history_messages.append({
                        "role": conv.role,
                        "content": conv.content
                    })
            except Exception as e:
                print(f"加载历史对话失败: {e}")
        
        # 保存用户消息到数据库
        if db:
            try:
                new_conversation = Conversation(
                    user_id=user_id,
                    role="user",
                    content=user_message,
                    timestamp=int(asyncio.get_event_loop().time()),
                    session_id=session_id
                )
                db.add(new_conversation)
                db.commit()
            except Exception as e:
                print(f"保存对话失败: {e}")
        
        async def event_stream():
            try:
                # 构建完整的消息列表（历史对话 + 当前消息）
                full_messages = history_messages.copy()
                full_messages.append({"role": "user", "content": user_message})
                
                # 调用AI API，传递完整的消息列表、db会话和session_id
                async for chunk in call_ai_api_stream(user_message, user_role, user_id, full_messages, db, session_id):
                    yield chunk
            except Exception as e:
                print(f"API调用错误: {e}")
                yield f"data: 错误: {str(e)}\n\n"
                yield "data: [DONE]\n\n"
        
        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        print(f"错误: {e}")
        return ResponseModel(code=500, msg="AI API调用失败", data=None)

# 文件上传接口
@app.post("/api/v1/files/upload", response_model=ResponseModel)
async def upload_file(file: UploadFile, request: Request, db: Session = Depends(get_db)):
    try:
        if not db:
            return ResponseModel(code=503, msg="数据库服务不可用", data=None)
        
        # 获取当前用户ID
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
            if token:
                try:
                    payload = verify_token(token)
                    if payload:
                        user_id = payload.get("id")
                except Exception as e:
                    print(f"警告: 获取用户ID失败: {e}")
        
        success = process_file(file, user_id, db)
        if not success:
            return ResponseModel(code=400, msg="文件处理失败", data=None)
        
        return ResponseModel(
            code=200,
            msg="文件上传成功",
            data={"filename": file.filename, "user_id": user_id}
        )
    except Exception as e:
        print(f"文件上传失败: {e}")
        return ResponseModel(code=500, msg="文件上传失败", data=None)

# 深度思考接口
@app.post("/api/v1/agent/deep", response_model=ResponseModel)
async def deep(request: DeepRequest):
    try:
        content = ""
        async for chunk in call_ai_api_stream(f"请对以下问题进行深度思考：{request.message}", "user"):
            if chunk.startswith("data: ") and not chunk.startswith("data: [DONE]"):
                content += chunk[6:]
        
        if content:
            return ResponseModel(
                code=200,
                msg="深度思考成功",
                data={"content": content}
            )
        else:
            return ResponseModel(
                code=200,
                msg="深度思考成功",
                data={"content": "我无法回答这个问题"}
            )
    except Exception as e:
        print(f"错误: {e}")
        return ResponseModel(
            code=200,
            msg="深度思考成功",
            data={"content": "我无法回答这个问题"}
        )

# 图片识别接口
@app.post("/api/v1/agent/image-recognition", response_model=ResponseModel)
async def image_recognition(request: ImageRecognitionRequest):
    try:
        # 初始化OpenAI客户端
        client = OpenAI(
            api_key=os.getenv("AGENT_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 调用图片识别API
        completion = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": request.image_url}},
                    {"type": "text", "text": request.prompt}
                ]
            }]
        )
        
        # 提取响应内容
        content = completion.choices[0].message.content
        
        return ResponseModel(
            code=200,
            msg="图片识别成功",
            data={"content": content}
        )
    except Exception as e:
        print(f"图片识别失败: {e}")
        return ResponseModel(
            code=500,
            msg="图片识别失败",
            data={"error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 8080)))