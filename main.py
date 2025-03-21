from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from pydantic import BaseModel
from typing import List
from model import get_model
import argparse
import os


# 使用 lifespan 来启动模型加载
async def lifespan_event(app):
    try:
        get_model()  # 在启动时加载模型
    except Exception as e:
        print(f"Error loading model on startup: {str(e)}")
        # 添加全局变量标记模型加载状态
        app.state.model_loaded = False
        return
    app.state.model_loaded = True
    yield  # 等待 FastAPI 生命周期的结束


# 首先定义 app 实例
app = FastAPI(
    title="UIE信息抽取服务",
    description="基于UIE模型的通用信息抽取服务",
    version="1.0.0",
    lifespan=lifespan_event
)

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# 配置静态文件
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "public")), name="static")


# 配置模板
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# 添加根路由
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class ExtractRequest(BaseModel):
    text: str
    schema_list: List[str]

@app.post("/extract")
async def extract_info(request: ExtractRequest):
    """信息抽取接口
    
    Args:
        request: 请求体，包含待抽取文本和抽取模式
            - text: 待抽取的文本内容
            - schema: 信息抽取模式列表，指定需要抽取的实体类型
                Example: ["人名", "时间", "地点"]
        
    Returns:
        dict: 抽取结果，包含识别出的实体及其类型
    """
    if not app.state.model_loaded:
        raise HTTPException(status_code=503, detail="Model is not loaded yet")
    
    try:
        model = get_model()
        result = model.predict(request.text, request.schema_list)
        return result
    except Exception as e:
        # 添加更详细的错误日志
        print(f"Error during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Prediction failed. Please check the input format and try again.")


def parse_args():
    parser = argparse.ArgumentParser(description="Run the FastAPI app with uvicorn.")
    parser.add_argument("--port", type=int, default=9999, help="Port to run the server on.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port)
