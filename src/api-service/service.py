from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routers import llm_chat, llm_chat_routers

# Setup FastAPI app
app = FastAPI(title="API Server", description="API Server", version="v1")

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Crimson Chat API"}

@app.get("/llm")
async def get_index():
    return {"message": "...testing"}

@app.get("/test")
async def get_index():
    return {"message": "also testing"}

# Additional routers here
app.include_router(llm_chat.router, prefix="/test", tags=["LLM Chat Test"])
app.include_router(llm_chat_routers.router, prefix="/llm", tags=["LLM Chat"])