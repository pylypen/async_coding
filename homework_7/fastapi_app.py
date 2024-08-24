from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class NameWord(BaseModel):
    name: str


@app.get("/", response_model=str)
async def read_root() -> str:
    return "hello world"


@app.post("/")
async def return_name(request: NameWord) -> str:
    return f"Hello {request.name}!"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
