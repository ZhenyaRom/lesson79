from fastapi import FastAPI, APIRouter
from app.routers import task, user


app = FastAPI()


@app.get('/')
async def welcome():
    return {"message": "Welcome to Taskmanager"}

app.include_router(task.router)
app.include_router(user.router)


# python -m uvicorn app.main:app