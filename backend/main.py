from fastapi import Depends, FastAPI, Query, Body, File, UploadFile
from typing import Optional, Dict, List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from models import MobileNet
import time
app = FastAPI()

origins = [
    "http://localhost:8080",
    "http://localhost:8080/#/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/")
async def read_items(
    q: Optional[str] = Query(
        None,
        alias="item-query",
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
        max_length=50,
        regex="^fixedquery$",
        deprecated=True,
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"filePath": file_path}

@app.get("/params/")
async def read_params(skip: int = 10, content: str = "ok"):
    return {"skip": skip, "content": content}

@app.get("/params2/")
async def read_params2(skip: int = 10, content: Optional[str] = None):
    if content:
        return {"skip": skip, "content": content}
    return {"skip": skip}

@app.get("/needy/")
async def needy_params(skip: int):
    return {"skip": skip}

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.post("/items/")
async def create_item(item: Item):
    return item

@app.post("/body/")
async def test_body(importance: int = Body(...)):
    return {"importance": importance}

@app.post("/dict/")
async def test_dict(dict: Dict[int, float]):
    return dict

async def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons

# Preload the net to memory
model = MobileNet()
@app.post("/images/")
async def receive_file(files: List[UploadFile] = File(...)):
    results = []
    avgTime = 0.0
    allTime = []
    for file in files:
        start = time.time()
        result = model.predict(file.file)
        end = time.time()
        allTime.append(end - start)
        tempL = []
        for arr in result:
            temp = arr[0].split(":")[1]
            tempL.append([temp, arr[1]])
        results.append(tempL)
    for cost in allTime:
        avgTime += cost
    avgTime /= len(allTime)
    print(avgTime)
    return {"predictions": results}