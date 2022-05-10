from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('15.164.98.36', 27017, username="test", password="test")
db = client.cnt_project2

@app.route('/')
def home():
    user_info = getUserInfoByToken()
    # print(user_info)
    return render_template('index.html', user_info=user_info)

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/t_signup')
def t_signup():
    msg = request.args.get("msg")
    return render_template('t_signup.html', msg=msg)

@app.route('/g_signup')
def g_signup():
    msg = request.args.get("msg")
    return render_template('g_signup.html', msg=msg)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    role_receive = request.form['role_give']
    userid_receive = request.form['userid_give']
    password_receive = request.form['password_give']
    # print(userid_receive, password_receive)

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'role': role_receive, 'userid': userid_receive, 'password': pw_hash})
    # print(result)
    if result is not None:
        payload = {
         'id': userid_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/t_sign_up/save', methods=['POST'])
def t_sign_up():
    userid_receive = request.form['userid_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "role": "traveler",
        "userid": userid_receive,
        "password": password_hash,
        "profile_name": userid_receive,
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_placeholder.png",
        "profile_info": ""
    }
    db.users.insert_one(doc)

    return jsonify({'result': 'success'})

@app.route('/g_sign_up/save', methods=['POST'])
def g_sign_up():
    userid_receive = request.form['userid_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "role": "guide",
        "userid": userid_receive,
        "password": password_hash,
        "profile_name": userid_receive,
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_placeholder.png",
        "profile_info": ""
    }
    db.users.insert_one(doc)

    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    userid_receive = request.form['userid_give']
    exists = bool(db.users.find_one({"userid": userid_receive}))
    # print(value_receive, type_receive, exists)
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/posting')
def posting():
    msg = request.args.get("msg")
    return render_template('posting.html', msg=msg)

@app.route('/kakaologin', methods=['POST'])
def kakaologin():
    user_nickname = request.form['nick_name']
    user_email = request.form['email']

    result = db.users.find_one({'role': 'traveler', 'userid': user_email, 'profile_name': user_nickname},{'_id':False})
    if result is None:
        doc = {
            "role": 'traveler',
            "userid": user_email,
            "profile_name": user_nickname,
            "profile_pic": "",
            "profile_pic_real": "profile_pics/profile_placeholder.png",
            "profile_info": ""
        }
        db.users.insert_one(doc)

    return 'a'


@app.route('/test')
def test():
    user_info = getUserInfoByToken()

    return render_template('test.html', user_info=user_info)

# 가이드 내상품 불러오기
@app.route('/test2')
def test2():
    # 가이드 카카오 로그인 구현시 사용
    token_kakao = request.cookies.get('kakao')
    # print(token_kakao) # 화면단에서 토큰 값 세팅시 '@' 가 %40으로 변환되므로 서버단에서 사용시 replace를 사용하여 변환
    if token_kakao is None:
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            myProducts = list(db.products.find({'userid': payload["id"]}, {'_id': False}))
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    else:
        set_val = token_kakao.replace('%40', '@')
        myProducts = list(db.products.find({'userid': set_val}, {'_id': False}))

    print(myProducts)
    return render_template('test2.html', myProducts=myProducts)


# 개인정보 수정
@app.route('/test3')
def test3():
    user_info = getUserInfoByToken()

    return render_template('test3.html', user_info=user_info)

def getUserInfoByToken():
    token_kakao = request.cookies.get('kakao')
    token_receive = request.cookies.get('mytoken')

    if token_receive is not None:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({"userid": payload["id"]})
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

    if token_kakao is not None:
        set_val = token_kakao.replace('%40', '@')
        user_info = db.users.find_one({"userid": set_val}, {'_id': False})

    return user_info;

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)