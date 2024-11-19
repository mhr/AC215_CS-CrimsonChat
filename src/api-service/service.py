from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routers import llm_chat

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
@app.get("/login")
async def get_index():
    return {"message": "Welcome to AC215"}

@app.get("/llmm")
async def get_index():
    return {"message": "...testing"}

@app.get("/test")
async def get_index():
    return {"message": "also testing"}

# Additional routers here
app.include_router(llm_chat.router, prefix="/llm")