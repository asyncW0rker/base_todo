from fastapi import FastAPI
from app.api.user_router import router as users_router
from app.api.todo_router import router as todos_router
from app.api.auth_router import router as auth_router


app = FastAPI()

app.include_router(users_router)
app.include_router(todos_router)
app.include_router(auth_router)
