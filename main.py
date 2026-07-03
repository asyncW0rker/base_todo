from fastapi import FastAPI
from app.api.users_router import router as users_router

app = FastAPI()
app.include_router(users_router)
