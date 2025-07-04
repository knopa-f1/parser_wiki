import logging

import uvicorn
from fastapi import FastAPI

from app.api.endpoints import endpoints

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI()

app.include_router(endpoints.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Parser Wiki server"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
