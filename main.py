from fastapi import FastAPI, UploadFile, Form, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


from fastapi.staticfiles import StaticFiles
from typing import Annotated
import sqlite3  # sqlite3 모듈을 import

con = sqlite3.connect("db.db", check_same_thread=False)
# db.db라는 DB파일과 연결하고, check_same_thread는 여러 스레드에서 사용할 수 있도록 하는 옵션인데, False로 지정해야 여러 스레드에서 사용 가능.

cur = con.cursor()
# DB와 상호작용하기 위한 커서 객체를 생성. 이 객체를 이용하여 DB에서 쿼리를 실행하고 결과를 가져올 수 있음

app = FastAPI()


# 아이템 추가
@app.post("/items")
async def create_item(
    image: UploadFile,
    title: Annotated[str, Form()],
    price: Annotated[int, Form()],
    description: Annotated[str, Form()],
    place: Annotated[str, Form()],
    insertAt: Annotated[int, Form()],
):
    image_bytes = await image.read()
    # UploadFile객체로 표현된 image를 read하여 ByteString으로 반환.
    # 이후 이 ByteString을 DB에 저장하거나 처리할때 사용

    cur.execute(
        f"""
                INSERT INTO items (title, image, price, description, place, insertAt)
                VALUES ('{title}','{image_bytes.hex()}',{price},'{description}','{place}',{insertAt})
                """
    )
    con.commit()  # 쿼리를 DB에 영구저장하기 위한 commit 함수 호출

    return "200"


# 아이템 불러오기
@app.get("/items")
async def get_items():
    con.row_factory = sqlite3.Row  # 컬럼명도 같이 가져오는 문법
    cur = con.cursor()
    rows = cur.execute(
        f"""
                        SELECT * FROM items
                       """
    ).fetchall()
    return JSONResponse(jsonable_encoder(dict(row) for row in rows))


# @app.post("/items") annotated를 안쓰고
# def create_item(
#     image: UploadFile,
#     title: str,
#     price: int,
#     description: str,
#     place: str,
# ):
#     print(image, title, price, description, place)
#     return "200"


@app.get("/images/{item_id}")
async def get_image(item_id):
    cur = con.cursor()  # DB에 접근하기 위해 커서 객체 생성
    imgae_bytes = cur.execute(
        f"""
                              SELECT image FROM items WHERE id={item_id}
                              """  # 요청한 아이디와 맞는 이미지 값 가져오기
    ).fetchone()[
        0
    ]  # 한번 호출할때 하나의 row만 가져와서 [0]은 첫번째 column의 값 가져오기
    return Response(content=bytes.fromhex(imgae_bytes))


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
