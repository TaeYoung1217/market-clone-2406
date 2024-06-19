from fastapi import FastAPI, UploadFile, Form, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
import hashlib

from fastapi.staticfiles import StaticFiles
from typing import Annotated
import sqlite3  # sqlite3 모듈을 import

con = sqlite3.connect("db.db", check_same_thread=False)
# db.db라는 DB파일과 연결하고, check_same_thread는 여러 스레드에서 사용할 수 있도록 하는 옵션인데, False로 지정해야 여러 스레드에서 사용 가능.

cur = con.cursor()
# DB와 상호작용하기 위한 커서 객체를 생성. 이 객체를 이용하여 DB에서 쿼리를 실행하고 결과를 가져올 수 있음

cur.execute(
    f"""
        CREATE TABLE IF NOT EXISTS items(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        image BLOB,
        price INTEGER NOT NULL,
        description TEXT ,
        place TEXT NOT NULL,
        insertAt INTEGER NOT NULL
        )
    """
)

app = FastAPI()

SECRET = "비밀키"
manager = LoginManager(SECRET, "/login")


# 회원가입
@app.post("/signup")
def signup(
    id: Annotated[str, Form()],
    password: Annotated[str, Form()],
    name: Annotated[str, Form()],
    email: Annotated[str, Form()],
):
    hashPassword = hashlib.sha256(password.encode()).hexdigest() #hashlib를 이용한 해시 암호화 후 16진수로 변환
    
    try:
        cur.execute(
            f"""
                    INSERT INTO users(`id`,`name`,`email`,`password`)
                    VALUES('{id}','{name}','{email}','{hashPassword}')
                    """
        )
        con.commit()
        return "200"
    except sqlite3.IntegrityError as e:
        return "duplicated id"


@manager.user_loader()
def query_user(data):  # 입력한 id가 DB에 존재하는지 확인
    WHERE_STATEMENTS = f'id="{data}"'  # SQL 쿼리에 WHERE 절 뒤에 조건문을 문자열로 만듦
    if type(data) == dict:  # 함수호출할때 인자가 dict 타입이라면
        WHERE_STATEMENTS = f'id="{data['id']}"'  # data 안에 있는 id를 쿼리문에 삽입

    con.row_factory = sqlite3.Row  # 컬럼명도 같이 가져오는 문법
    cur = con.cursor()
    user = cur.execute(
        f"""
                       SELECT * FROM users WHERE {WHERE_STATEMENTS}
                       """
    ).fetchone()  # id에 해당하는 row한개 전체를 가져옴
    return user


@app.post("/login")
def login(id: Annotated[str, Form()], password: Annotated[str, Form()]):
    user = query_user(id)
    hashPassword = hashlib.sha256(password.encode()).hexdigest()  
    #입력한 password를 hashlib를 이용하여 암호화 한 다음 DB에서 조회
    
    if not user:  # 해당하는 유저가 없을때
        raise InvalidCredentialsException  # error 메세지 출력
    elif (
        
        hashPassword != user["password"]
    ):  # 비밀번호가 틀릴때 user row에서 password column에 해당하는 값을 가져와서 비교
        # query_user 함수에서 row_factory 사용했기때문에 가능
        raise InvalidCredentialsException  # error 메세지 출력

    access_token = manager.create_access_token(
        data={"sub": {"id": user["id"], "name": user["name"], "email": user["email"]}}
    )  # access_token 발급하여 프론트엔드로 return

    return access_token


# 아이템 추가
@app.post("/items")
async def create_item(
    image: UploadFile,
    title: Annotated[str, Form()],
    price: Annotated[int, Form()],
    description: Annotated[str, Form()],
    place: Annotated[str, Form()],
    insertAt: Annotated[int, Form()],user=Depends(manager)
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
async def get_items(
    user=Depends(manager),
):  # user가 인증된 상태에서만 get 요청 가능하도록
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


# 이미지만 가져오기
@app.get("/images/{item_id}")
async def get_image(item_id):
    cur = con.cursor()  # DB에 접근하기 위해 커서 객체 생성
    image_bytes = cur.execute(
        f"""
                              SELECT image FROM items WHERE id={item_id}
                              """  # 요청한 아이디와 맞는 이미지 값 가져오기
    ).fetchone()[
        0
    ]  # 한번 호출할때 하나의 row만 가져와서 [0]은 첫번째 column의 값 가져오기

    return Response(content=bytes.fromhex(image_bytes), media_type="image/*")


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
