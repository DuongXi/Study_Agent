from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from inspect import getmembers
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from datetime import datetime
from fastapi.responses import StreamingResponse
import os
import json
from sqlalchemy.orm import Session
import sys

from src.agent.graph import Graph
import tools.langgraph_toolkit as toolkit
from src.database import SessionLocal, engine
from src.models import *

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]  
)
config = {"configurable": {"thread_id": "1"}}
graph_model = ""
graph = None
auth = False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_tools(auth):
    if auth:
        tools = []
        for name, func in getmembers(toolkit):
            if 'tool_call_schema' in dir(func):
                tools.append(func)
        return tools
    else:
        return [toolkit.doc_retrieve]

async def stream_chat(user_message: Message):
    global graph
    if graph:
        async for chunk in graph.compiled_graph.astream({
            'messages': [{
                "role": "user",
                "content": user_message.message
                }]},
            stream_mode="updates",
            config=config,
            subgraphs=True
        ):
            print(chunk)
            message = list(chunk[1].values())[0]
            if list(message.keys()) == ['messages']:
                if type(message['messages']) == list:
                    response = f"{json.dumps({'role': str(message['messages'][0].type), 'text': str(message['messages'][0].content) if str(message['messages'][0].content) else str(message['messages'][0].additional_kwargs['tool_calls'][0]['function']['arguments']) , 'tool_name': str(message['messages'][0].name) if hasattr(message['messages'][0], 'name') else None})}\n"
                else:
                    response = f"{json.dumps({'role': str(message['messages'].type), 'text': str(message['messages'].content), 'tool_name': str(message['messages'].name) if hasattr(message['messages'], 'name') else None})}\n"   
                yield response
            await asyncio.sleep(0.1)
    else:
        raise HTTPException(status_code=400, detail="Model not found")

# Lấy thông tin chat từ mô hình
@app.post("/api/chat")
async def get_chat(user_message: Message):
    try:
        return StreamingResponse(stream_chat(user_message), media_type="text/event-stream")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lấy thông tin mô hình
@app.post("/api/model")
async def get_model(model: Model):
    global graph_model, graph
    if model.model :
        graph_model=model.model
        graph = Graph(model=graph_model, tools=get_tools(auth))
    else:
        raise HTTPException(status_code=400, detail="Model not found")

# Thực thi câu lệnh SQL
@app.post("/api/query")
async def execute_sql(query: Query):
    return toolkit.connection.get_json_data(query.query)

# Gửi góp ý
@app.post("/api/feedback")
def submit_feedback(feedback: FeedbackInput, db: Session = Depends(get_db)):
    new_feedback = Feedback(email=feedback.email, message=feedback.message)
    db.add(new_feedback)
    db.commit()

# Lưu token
@app.post("/api/token")
def post_token(token: TokenInfo, db: Session = Depends(get_db)):
    global graph_model, graph, auth
    auth = True
    user = db.query(User).filter(User.email == token.user_email).first()
    if not user:
        user = User(email=token.user_email)
        db.add(user)

    # Cập nhật token
    user.access_token = token.access_token
    user.refresh_token = token.refresh_token
    user.expires_at = datetime.fromisoformat(token.expires_at)

    db.commit()
    toolkit.calendar = toolkit.Calendar(token.access_token, token.refresh_token)
    graph = Graph(model=graph_model, tools=get_tools(auth))

# Lấy token
@app.get("/api/token/{user_email}")
def read_token(token: CookieToken, db: Session = Depends(get_db)):
    global graph_model, graph, auth
    auth = True
    user = db.query(User).filter(User.email == token.user_email).first()
    
    toolkit.calendar = toolkit.Calendar(token.access_token, user.refresh_token)
    graph = Graph(model=graph_model, tools=get_tools(auth))

# Đăng xuất
@app.delete("/api/logout")
def logout(request: Request):
    global auth
    auth = False
    try:
        request.session.clear()
    except:
        pass