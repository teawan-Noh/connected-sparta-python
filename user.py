from flask import Flask, render_template, jsonify, request, redirect, url_for
import jwt
from pymongo import MongoClient

SECRET_KEY = 'SPARTA'
# AWS 버전
# client = MongoClient('54.180.31.220', 27017, username="test", password="test")
#local 버전
client = MongoClient("mongodb://localhost:27017/")
db = client.cnt_project2

def getUserInfoByToken():

    token_kakao = request.cookies.get('kakao')
    token_receive = request.cookies.get('mytoken')
    user_info = ''

    if token_receive is not None:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            # print(payload["id"])
            user_info = db.users.find_one({"userid": payload["id"]})
            # print('실행', user_info)
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

    if token_kakao is not None:
        set_val = token_kakao.replace('%40', '@')
        user_info = db.users.find_one({"userid": set_val}, {'_id': False})

    if user_info is not None:
        return user_info;

    if user_info is None:
        user_info = 'a';
        return user_info;

def get_status():
    token_kakao = request.cookies.get('kakao')
    token_receive = request.cookies.get('mytoken')

    if token_receive is not None:
        status = 0
    elif token_kakao is not None:
        status = 0
    else:
        status = 123

    return status;