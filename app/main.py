import uvicorn
from fastapi import FastAPI

from db.base import engine,Base

from api.token.endpoints_tokens import router as token_router

app = FastAPI()

app.include_router(token_router)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    

if __name__=="__main__":
    uvicorn.run("main:app",port=8000,host="127.0.0.1")