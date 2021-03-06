import sys
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
# AWS 버전
# client = MongoClient('54.180.31.220', 27017, username="test", password="test")
# client = MongoClient('mongodb://test:test@localhost', 27017)
client = MongoClient("mongodb://localhost:27017/")
db = client.cnt_project2

global filename1

@application.route('/fileupload', methods=['POST'])
def file_upload():
    file = request.files['file']
    box = str(file)

    filenamefront = box.split('.')[0].split('\'')[-1]
    extension = box.split('.')[-1].split('/')[-1].split('\'')[0]

    global filename1
    filename1 = f'{filenamefront}.{extension}'
    # print(str(filename1))
    #로컬 사용시 본인의 계정 연동할 경우 aws access key 주석 처리해야 함.
    s3 = boto3.client('s3'
                      # aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                      # aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
                      )
    s3.put_object(
        ACL="public-read",
        # Bucket=os.environ["BUCKET_NAME"],
        Bucket='project1-sparta',
        Body=file,
        Key=file.filename,
        ContentType=file.content_type
    )
    return jsonify({'result': 'success'})

@application.route('/')
def home():
    user_info = user.getUserInfoByToken()

    status = user.get_status()
    if user_info is not None:
        return render_template('index.html', user_info=user_info, statusbox=status)
    else:
        return render_template('index.html', user_info='a', statusbox=status)

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
    # print(userid_receive, password_receive, role_receive)

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'role': role_receive, 'userid': userid_receive, 'password': pw_hash})
    # print(result)
    if result is not None:
        payload = {
         'id': userid_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        # aws 버전
        # token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        # local 버전
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
    products = list(db.products.find({}))
    user_info = user.getUserInfoByToken()
    status = user.get_status()
    result = user_info['role']
    return render_template('product.html', result=result, user_info=user_info, statusbox=status, products=products)


@application.route('/searchProductByTitle', methods=['GET'])
def searchProductByTitle():

    searchVal = request.args.get("searchVal")

    ({'text': {'$regex': 'IP'}}, {'text': 1, 'created_at': 1})
    # searched_list = list(db.products.find({'title': {'$regex': val}}, {'_id': False}))
    searched_list = list(db.products.find({'title': searchVal}, {'_id': False}))
    print(searched_list, '실')
    return 'a'


@application.route('/go_posting')
def go_posting():
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰 해독 후 username이 토큰의 id값인 녀석을 찾아 user_info라고 한다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userid": payload["id"]})
        result = user_info["role"]
        products = db.products.find({})
        user_info = user.getUserInfoByToken()
        status = user.get_status()
        return render_template('product_write.html', result=result, products=products, user_info=user_info,statusbox=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@application.route('/posting', methods=['POST'])
def posting():
    # print(filename1, '여기')
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰 해독 후 username이 토큰의 id값인 녀석을 찾아 user_info라고 한다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userid": payload["id"]})

        title_receive = request.form["title_give"]
        content_receive = request.form["content_give"]
        date_receive = request.form["date_give"]
        calender_receive = request.form["calender_give"]
        price_receive = request.form["price_give"]
        x_receive = request.form["x_give"]
        y_receive = request.form["y_give"]
        # AWS 버전 file
        # file = filename1
        # Local 버전 file
        file = request.files["file_give"]
        # print(file)
        # print('파일 네임:', file.filename.split('.')[0])
        # 현재 날짜를 불러온다.
        # today = datetime.now()
        # today_receive = today.strftime('%Y-%m-%d-%H-%M-%S')

        # # extention 하고 출력 값이 같은데 왜 이렇게 처리한거지 (강의 코드 따온 부분 : 아래 extension 값 가져오는 부분까지)
        # filename = secure_filename(file.filename)
        # print(filename, '여기')
        # # # 파일 형식을 따오는 코드
        # extension = file.filename.split('.')[-1]
        # # # 따온 파일 이름과 형식을 저장해주는 코드
        # save_to = f'static/profile_pics/{filename}.{extension}'
        save_to = f'static/profile_pics/{file.filename}'
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
            "file": file.filename,
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


# @application.route('/go_editing')
# def go_editing():
#     pid_receive = request.form["pid_give"]
#     token_receive = request.cookies.get('mytoken')
#     try:
#         # 토큰 해독 후 username이 토큰의 id값인 녀석을 찾아 user_info라고 한다.
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.users.find_one({"userid": payload["id"]})
#         result = user_info["role"]
#         product = db.products.find_one({"pid":pid_receive})
#         status = user.get_status()
#         return render_template('product_write.html', result=result, product=product, statusbox=status)
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))

# # 수정하기 추가 예정
# @application.route('/edit_posting', methods=['POST'])
# def edit_posting():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.users.find_one({"userid": payload["id"]})
#         title_receive = request.form["title_give"]
#         file = filename1
#         content_receive = request.form["content_give"]
#         date_receive = request.form["date_give"]
#         calender_receive = request.form["calender_give"]
#         price_receive = request.form["price_give"]
#         x_receive = request.form["x_give"]
#         y_receive = request.form["y_give"]
#         product_count = db.products.estimated_document_count()
#         if product_count == 0:
#             max_value = 1
#         else:
#             max_value = product_count + 1
#         # username(id), 닉네임, 프로필 사진, 코멘트, 날짜 doc dictionary에 저장
#         doc = {
#             "userid": user_info["userid"],
#             "profile_name": user_info["profile_name"],
#             "profile_pic_real": user_info["profile_pic_real"],
#             "title": title_receive,
#             "file": file,
#             "content": content_receive,
#             "x": x_receive,
#             "y": y_receive,
#             "calender": calender_receive,
#             "price": price_receive,
#             "date": date_receive,
#             "pid": max_value
#         }
#         db.products.update_one(doc)
#         # 성공하면 '포스팅 성공!'을 띄우자!
#         return jsonify({"result": "success", 'msg': '업데이트 성공'})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))

@application.route('/delete_product', methods=['POST'])
def delete_product():
    pid_receive = request.form["pid_give"]
    product = db.products.find_one({"pid": int(pid_receive)}, {"_id": False})['pid']
    db.products.delete_one({"pid":product})
    return jsonify({"result": "success", 'msg': '삭제 성공'})

# 포스팅 불러오기
@application.route("/product/get_index", methods=['GET'])
def get_products_index():
    products = list(db.products.find({}).sort("date", -1).limit(3))
    return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "products":dumps(products)})

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
        bucket_info = db.buckets.find_one({"pid": int(pid)}, {"_id": False})
        comments = list(db.comments.find({"cid": int(pid)}, {"_id": False}))
        return render_template('product_info.html', result=result, user_info=user_info, product_info=product_info, comments=comments, statusbox=status, bucket_info=bucket_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@application.route('/on_bucket', methods=['POST'])
def on_bucket():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userid": payload["id"]})
        action_receive = request.form["action_give"]
        pid_receive = request.form["pid_give"]
        doc = {
            "pid": pid_receive,
            "action": action_receive,
            "userid": user_info["userid"]
        }
        db.buckets.insert_one(doc)
        return jsonify({"result": "success", 'msg': '등록 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@application.route('/off_bucket', methods=['POST'])
def off_bucket():
    pid_receive = request.form["pid_give"]
    db.buckets.delete_one({"pid":int(pid_receive)})
    return jsonify({"result": "success", 'msg': '삭제 성공'})

@application.route('/mybucket')
def myBuckets():
    # 가이드 카카오 로그인 구현시 사용
    token_kakao = request.cookies.get('kakao')
    # print(token_kakao) # 화면단에서 토큰 값 세팅시 '@' 가 %40으로 변환되므로 서버단에서 사용시 replace를 사용하여 변환
    if token_kakao is None:
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({"userid": payload["id"]})
            bucketlist = []
            buckets = list(db.buckets.find({'userid':payload['id']}, {'_id': False}))
            for bucket in buckets:
                bucketid = bucket['pid']
                bucket2 = db.products.find_one({'pid':bucketid}, {'_id': False})
                bucketlist.append(bucket2)
            print(bucketlist)
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    else:
        set_val = token_kakao.replace('%40', '@')
        user_info = db.users.find_one({"userid": set_val})
        bucketlist = []
        buckets = list(db.buckets.find({'userid': set_val}, {'_id': False}))
        for bucket in buckets:
            bucketid = bucket['pid']
            bucket2 = db.products.find_one({'pid': bucketid}, {'_id': False})
            bucketlist.append(bucket2)
        print(bucketlist)
    user_info = user.getUserInfoByToken()
    status = user.get_status()
    return render_template('myBuckets.html', myBuckets=bucketlist, user_info=user_info, statusbox=status)

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
        comment_count = db.comments.estimated_document_count({"cid":cid_receive})
        if comment_count == 0:
            comment_value = 1
        else:
            comment_value = comment_count + 1
        doc = {
            "cid":cid_receive,
            "userid":user_info["userid"],
            "profile_pic_real": user_info["profile_pic_real"],
            "content": content_receive,
            "pcid":comment_value
            # "grade": grade_receive
        }
        db.comments.insert_one(doc)
        # 성공하면 '포스팅 성공!'을 띄우자!
        return jsonify({"result": "success", 'msg': '댓글 달기 성공.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# # 댓글 수정하기
# @application.route('/product/edit_comments', methods=['POST'])
# def edit_comments():
#     user_info = user.getUserInfoByToken()
#     cid_receive = request.form['cid_give']
#     pcid_receive = request.form['pcid_give']
#     comment_receive = request.form['comment_give']
#     doc = {
#         "cid": cid_receive,
#         "userid":user_info["userid"],
#         "profile_pic_real": user_info["profile_pic_real"],
#         "content": comment_receive,
#         "pcid": pcid_receive
#     }
#     db.comments.update_one(doc)


@application.route('/delete_comment', methods=['POST'])
def delete_comment():
    pcid_receive = request.form["pcid_give"]
    comment_cid = db.comments.find_one({"pcid": int(pcid_receive)}, {"_id": False})['pcid']
    db.comments.delete_one({"pcid":comment_cid})
    return jsonify({"result": "success", 'msg': '삭제 성공'})


# 댓글 불러오기
@application.route('/product/get_comments', methods=['GET'])
def get_comments():
    cid_receive = request.args.get("cid_give")
    # data form box / get args
    # comments = list(db.comments.find({"comment":comment_receive}, {"_id": False}))
    # return jsonify({'result': 'success', 'comments': comments})
    comments = list(db.comments.find({"cid":cid_receive}, {'_id': False}).sort("date",-1))
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
            user_info = db.users.find_one({"userid": payload["id"]})
            myProducts = list(db.products.find({'userid': payload["id"]}, {'_id': False}))
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    else:
        set_val = token_kakao.replace('%40', '@')
        myProducts = list(db.products.find({'userid': set_val}, {'_id': False}))
        user_info = db.users.find_one({"userid": set_val})
    print(myProducts)
    status = user.get_status()
    return render_template('myProducts.html', myProducts=myProducts, statusbox=status, user_info=user_info)

@application.route('/mybookmark')
def myBookmark():
    # 가이드 카카오 로그인 구현시 사용
    token_kakao = request.cookies.get('kakao')
    # print(token_kakao) # 화면단에서 토큰 값 세팅시 '@' 가 %40으로 변환되므로 서버단에서 사용시 replace를 사용하여 변환
    if token_kakao is None:
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({"userid": payload["id"]})
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    else:
        set_val = token_kakao.replace('%40', '@')
        user_info = db.users.find_one({"userid": set_val})
    user_info = user.getUserInfoByToken()
    status = user.get_status()
    return render_template('myBookmark.html', user_info=user_info, statusbox=status)

# 내 댓글 불러오기
@application.route('/myComment')
def myComment():
    # 가이드 카카오 로그인 구현시 사용
    token_kakao = request.cookies.get('kakao')
    # print(token_kakao) # 화면단에서 토큰 값 세팅시 '@' 가 %40으로 변환되므로 서버단에서 사용시 replace를 사용하여 변환
    if token_kakao is None:
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({"userid": payload["id"]})
            myComments = list(db.comments.find({'userid': payload["id"]}, {'_id': False}))
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    else:
        set_val = token_kakao.replace('%40', '@')
        user_info = db.users.find_one({"userid": set_val})
        myComments = list(db.comments.find({'userid': set_val}, {'_id': False}))

    print(myComments)
    status = user.get_status()
    return render_template('myComments.html', myComments=myComments, statusbox=status, user_info=user_info)

# 내 커뮤니티 불러오기
@application.route('/myCommunity')
def myCommunity():
    # 가이드 카카오 로그인 구현시 사용
    token_kakao = request.cookies.get('kakao')
    # print(token_kakao) # 화면단에서 토큰 값 세팅시 '@' 가 %40으로 변환되므로 서버단에서 사용시 replace를 사용하여 변환
    if token_kakao is None:
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({"userid": payload["id"]})
            myCommunity = list(db.community.find({'userid': payload["id"]}, {'_id': False}))
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    else:
        set_val = token_kakao.replace('%40', '@')
        user_info = db.users.find_one({"userid": set_val})
        myCommunity = list(db.community.find({'userid': set_val}, {'_id': False}))

    print(myCommunity)
    status = user.get_status()
    return render_template('myCommunity.html', myCommunity=myCommunity, statusbox=status, user_info=user_info)

# 개인정보 페이지 호출
@application.route('/myInfo')
def myInfo():
    user_info = user.getUserInfoByToken()
    status = user.get_status()
    return render_template('myInfo.html', user_info=user_info, statusbox=status)

# 개인정보 수정
@application.route('/userInfoUpdate', methods=['POST'])
def userInfoUpdate():
    # email = request.form['email1']
    profile_name = request.form['nickname']
    userid = request.args.get('user')
    print(userid)

    db.users.update_one({'userid': userid}, {'$set': {'profile_name': profile_name}})
    user_info = user.getUserInfoByToken()
    status = user.get_status()
    return render_template('myInfo.html', user_info=user_info, statusbox=status)


if __name__ == '__main__':
    application.run('0.0.0.0', port=5000, debug=True)

########################################################################################################################

# from flaskext.mysql import MySQL
# import redis
# import logging
# from logstash_async.handler import AsynchronousLogstashHandler
# import json
# import botocore

# # cors
# cors = CORS(application, resources={r"/*": {"origins": "*"}})
#
# # mysql
# mysql = MySQL()
# application.config['MYSQL_DATABASE_USER'] = os.environ["MYSQL_DATABASE_USER"]
# application.config['MYSQL_DATABASE_PASSWORD'] = os.environ["MYSQL_DATABASE_PASSWORD"]
# application.config['MYSQL_DATABASE_DB'] = os.environ["MYSQL_DATABASE_DB"]
# application.config['MYSQL_DATABASE_HOST'] = os.environ["MYSQL_DATABASE_HOST"]
# mysql.init_app(application)
#
# # redis
# db = redis.Redis(os.environ["REDIS_HOST"], decode_responses=True)
#
# #logstash
# python_logger = logging.getLogger('python-logstash-logger')
# python_logger.setLevel(logging.INFO)
# python_logger.addHandler(AsynchronousLogstashHandler(os.environ["LOGSTASH_HOST"], 5044, database_path=''))

# @application.route('/download', methods=['GET'])
# def download_img():
#     bucket_name = 'project1-sparta'
#     object_path = ''
#     file_path = '/static'
#
#     s3 = boto3.client('s3')
#     s3.download_file(bucket_name, object_path, file_path)
#
#     s3 = boto3.resource('s3')
#     BUCKET_NAME = 'project1-sparta'
#     KEY = filename1
#     try:
#         s3.Bucket(BUCKET_NAME).download_file(KEY, 'my_local_image.jpg')
#     except botocore.exceptions.ClientError as e:
#         if e.response['Error']['Code'] == "404":
#             print("The object does not exist.")
#         else:
#             raise

# @application.route('/files', methods=['GET'])
# def files():
#     conn = mysql.connect()
#     cursor = conn.cursor()
#     cursor.execute("SELECT file_name from file")
#     data = cursor.fetchall()
#     conn.close()
#     return jsonify({'result': 'success', 'files':data})

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

# # 즐겨찾기 추가 예정
# @application.route('/update_favorite', methods=['POST'])
# def update_favorite():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.users.find_one({"userid": payload["id"]})
#         type_receive = request.form["type_give"]
#         pid_receive = request.form["pid_give"]
#         action_receive = request.form["action_give"]
#         doc = {
#             "pid": pid_receive,
#             "userid": user_info["userid"],
#             "type": type_receive
#         }
#         if action_receive == "on_favorite":
#             db.favorites.insert_one(doc)
#         else:
#             db.favorites.delete_one(doc)
#         return jsonify({"result": "success", 'msg': 'updated'})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))

# # 댓글 삭제 추가 예정
# @application.route('/delete_comment', methods=['POST'])
# def delete_comment():
#     cid_receive = request.form["cid_give"]
#     list(db.articles.find({}).sort("date", -1).limit(4)
#     comment = list(db.comments.find({"cid":cid_receive}, {'_id': False})).sort({date})
#     db.products.delete_one({"pid":product})
#     return jsonify({"result": "success", 'msg': '삭제 성공'})

# @application.route('/payment')
# def payment():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.users.find_one({"username": payload["id"]})
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
