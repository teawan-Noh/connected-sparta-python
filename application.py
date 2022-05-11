from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from bson.json_util import dumps
from datetime import datetime, timedelta
import user
import boto3
import json
from flask_cors import CORS
import os


application = Flask(__name__)
cors = CORS(application, resources={r"/*": {"origins": "*"}})
application.config["TEMPLATES_AUTO_RELOAD"] = True
application.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('54.180.31.220', 27017, username="test", password="test")
db = client.cnt_project2

@application.route('/fileupload', methods=['POST'])
def file_upload():
    file = request.files['file']
    s3 = boto3.client('s3',
                      aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
                      )
    s3.put_object(
        ACL="public-read",
        Bucket=os.environ["BUCKET_NAME"],
        Body=file,
        Key=file.filename,
        ContentType=file.content_type
    )
    return jsonify({'result': 'success'})

@application.route('/')
def home():
    status = user.get_status()
    return render_template('index.html', statusbox=status)

@application.route('/login')
def login():
    msg = request.args.get("msg")
    # user_info = getUserInfoByToken()
    return render_template('login.html', msg=msg)

@application.route('/t_signup')
def t_signup():
    msg = request.args.get("msg")
    return render_template('t_signup.html', msg=msg)

@application.route('/g_signup')
def g_signup():
    msg = request.args.get("msg")
    return render_template('g_signup.html', msg=msg)

@application.route('/sign_in', methods=['POST'])
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


@application.route('/t_sign_up/save', methods=['POST'])
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

@application.route('/g_sign_up/save', methods=['POST'])
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


@application.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    userid_receive = request.form['userid_give']
    exists = bool(db.users.find_one({"userid": userid_receive}))
    # print(value_receive, type_receive, exists)
    return jsonify({'result': 'success', 'exists': exists})

########################################################################################################################

@application.route('/product')
def product():
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰 해독 후 username이 토큰의 id값인 녀석을 찾아 user_info라고 한다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userid": payload["id"]})
        result = user_info["role"]
        msg = request.args.get("msg")
        status = user.get_status()
        return render_template('product.html', result=result, msg=msg, statusbox=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@application.route('/go_posting')
def go_posting():
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰 해독 후 username이 토큰의 id값인 녀석을 찾아 user_info라고 한다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userid": payload["id"]})
        result = user_info["role"]
        products = db.products.find({})
        status = user.get_status()
        return render_template('product_write.html', result=result, products=products, statusbox=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@application.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰 해독 후 username이 토큰의 id값인 녀석을 찾아 user_info라고 한다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userid": payload["id"]})
        # 코멘트에 적힌 글과 현재 날짜를 불러온다.
        today = datetime.now()
        title_receive = request.form["title_give"]
        file = request.files["file_give"]
        content_receive = request.form["content_give"]
        date_receive = request.form["date_give"]
        calender_receive = request.form["calender_give"]
        price_receive = request.form["price_give"]
        x_receive = request.form["x_give"]
        y_receive = request.form["y_give"]
        today_receive = today.strftime('%Y-%m-%d-%H-%M-%S')
        filename = f'file-{today_receive}'
        # 파일 형식을 따오는 코드
        extension = file.filename.split('.')[-1]
        # 따온 파일 이름과 형식을 저장해주는 코드
        save_to = f'static/{filename}.{extension}'
        file.save(save_to)
        product_count = db.products.estimated_document_count()
        if product_count == 0:
            max_value = 1
        else:
            max_value = product_count + 1
        # username(id), 닉네임, 프로필 사진, 코멘트, 날짜 doc dictionary에 저장
        doc = {
            "userid": user_info["userid"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "title": title_receive,
            "file": f'{filename}.{extension}',
            "content": content_receive,
            "x":x_receive,
            "y":y_receive,
            "calender":calender_receive,
            "price":price_receive,
            "date": date_receive,
            "pid":max_value
        }
        db.products.insert_one(doc)
        # 성공하면 '포스팅 성공!'을 띄우자!
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@application.route('/edit_posting', methods=['POST'])
def edit_posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userid": payload["id"]})
        today = datetime.now()
        title_receive = request.form["title_give"]
        file = request.files["file_give"]
        content_receive = request.form["content_give"]
        date_receive = request.form["date_give"]
        calender_receive = request.form["calender_give"]
        price_receive = request.form["price_give"]
        today_receive = today.strftime('%Y-%m-%d-%H-%M-%S')
        filename = f'file-{today_receive}'
        extension = file.filename.split('.')[-1]
        save_to = f'static/{filename}.{extension}'
        file.save(save_to)
        doc = {
            "userid": user_info["userid"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "title": title_receive,
            "file": f'{filename}.{extension}',
            "content": content_receive,
            "calender":calender_receive,
            "price":price_receive,
            "date": date_receive
        }
        db.products.update_one(doc)
        # 성공하면 '포스팅 성공!'을 띄우자!
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 포스팅 불러오기
@application.route("/product/get", methods=['GET'])
def get_products():
    products = list(db.products.find({}).sort("date", -1))
    return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "products":dumps(products)})

# 상품 상세 페이지로 이동
@application.route('/product/<pid>')
def product_detail(pid):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userid": payload["id"]}, {"_id": False})
        # print(user_info)
        result = user_info["role"]
        product_info = db.products.find_one({"pid": int(pid)}, {"_id": False})
        status = user.get_status()
        return render_template('product_info.html', result=result, user_info=user_info, product_info=product_info, statusbox=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 댓글 작성하기
@application.route('/product/add_comments', methods=['POST'])
def add_comments():
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰 해독 후 username이 토큰의 id값인 녀석을 찾아 user_info라고 한다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userid": payload["id"]})
        cid_receive = request.form["cid_give"]
        # grade_receive = request.form['grade_give']
        content_receive = request.form['content_give']
        doc = {
            "cid":cid_receive,
            "userid":user_info["userid"],
            "profile_pic_real": user_info["profile_pic_real"],
            "content": content_receive
            # "grade": grade_receive
        }
        db.comments.insert_one(doc)
        # 성공하면 '포스팅 성공!'을 띄우자!
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



# # 댓글 수정하기
# @application.route('/product/edit_comments', methods=['POST'])
# def edit_comments():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         # 토큰 해독 후 username이 토큰의 id값인 녀석을 찾아 user_info라고 한다.
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.users.find_one({"userid": payload["id"]})
#         grade_receive = request.form['grade_give']
#         content_receive = request.form['content_give']
#         doc = {
#             "userid":user_info["userid"],
#             "profile_pic_real": user_info["profile_pic_real"],
#             "content": content_receive,
#             "grade": grade_receive
#         }
#         db.comments.update_one(doc)
#         # 성공하면 '포스팅 성공!'을 띄우자!
#         return jsonify({'result': 'success', 'msg': 'comment edited'})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))

# 댓글 불러오기
@application.route('/product/get_comments', methods=['GET'])
def get_comments():
    cid_receive = request.args.get("cid_give")
    # data form box / get args
    # comments = list(db.comments.find({"comment":comment_receive}, {"_id": False}))
    # return jsonify({'result': 'success', 'comments': comments})
    comments = list(db.comments.find({"cid":cid_receive}, {'_id': False}))
    # count_grade = db.comments.count_documents({})
    # add_grade = 0
    # for comment in comments:
    #     grades = comment['grade']
    #     add_grade += grades
    # mean = add_grade / count_grade
    return jsonify({'result': 'success', 'comments': comments})

@application.route('/kakaologin', methods=['POST'])
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


@application.route('/mypage')
def mypage():
    user_info = user.getUserInfoByToken()
    status = user.get_status()
    return render_template('myPage.html', user_info=user_info, statusbox=status)

# 가이드 내상품 불러오기
@application.route('/myProduct')
def myProduct():
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
    status = user.get_status()
    return render_template('myProducts.html', myProducts=myProducts, statusbox=status)


# 개인정보 페이지 호출
@application.route('/myInfo')
def myInfo():
    user_info = user.getUserInfoByToken()
    status = user.get_status()
    return render_template('myInfo.html', user_info=user_info, statusbox=status)

# 개인정보 수정
@application.route('/userInfoUpdate', methods=['POST'])
def userInfoUpdate():
    email = request.form['email1']
    profile_name = request.form['nickname']
    userid = request.args.get('user')
    print(userid)

    db.users.update_one({'userid': userid}, {'$set': {'profile_name': profile_name}})
    user_info = user.getUserInfoByToken()
    status = user.get_status()
    return render_template('myInfo.html', user_info=user_info, statusbox=status)



# if __name__ == '__main__':
#     application.debug = True
#     application.run()
if __name__ == '__main__':
    application.run('0.0.0.0', port=5000, debug=True)

########################################################################################################################

# @application.route('/payment')
# def payment():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.users.find_one({"username": payload["id"]})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))

# # 포스팅 게시 (토큰 필요)
# @application.route('/posting', methods=['POST'])
# def posting():
#     token_receive = request.cookies.get('mytoken')                               # 가이드 토큰
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])    # 가이드 토큰
#         user_info = db.users.find_one({"username": payload["id"]})               # 가이드 토큰
#         today = datetime.now()
#         name_receive = request.form["name_give"]
#         title_receive = request.form["title_give"]
#         file = request.files["file_give"]
#         comment_receive = request.form["comment_give"]
#         date_receive = request.form["date_give"]
#         grade_receive = request.form["grade_give"]
#         today_receive = today.strftime('%Y-%m-%d-%H-%M-%S')
#         filename = f'file-{today_receive}'
#         # 파일 형식을 따오는 코드
#         extension = file.filename.split('.')[-1]
#         # 따온 파일 이름과 형식을 저장해주는 코드
#         save_to = f'static/post_pics/{filename}.{extension}'
#         file.save(save_to)
#         # username(id), 닉네임, 프로필 사진, 코멘트, 날짜 doc dictionary에 저장
#         doc = {
#             "username": user_info["username"],
#             "profile_name": user_info["profile_name"],
#             "profile_pic_real": user_info["profile_pic_real"],
#             "name": name_receive,
#             "title": title_receive,
#             'file': f'{filename}.{extension}',
#             "comment": comment_receive,
#             "grade": grade_receive,
#             "date": date_receive
#         }
#         db.products.insert_one(doc)
#         # 성공하면 '포스팅 성공!'을 띄우자!
#         return jsonify({"result": "success", 'msg': '포스팅 성공'})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))

# # 후기 불러오기
# @application.route("/product/get_articles", methods=['GET'])
# def get_articles():
#     articles = list(db.articles.find({}).sort("date", -1).limit(4))
#     for article in articles:
#         article["_id"] = str(article["_id"])
#         article["grade"] = db.grades.find_one({"article_id": article["_id"], "type": "grade"})
#         # article["count_heart"] = db.grade.count_documents({"article_id": article["_id"], "type": "grade"})
#     return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "articles":articles})

# # 커뮤니티로 이동
# @application.route('/move_community')
# def move_community():
#     return render_template('community.html')

########################################################################################################################