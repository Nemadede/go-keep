from flask import Flask, request, jsonify, make_response, Blueprint
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import  logout_user
from server import db
from server.models import *
from server.utils import *
import datetime
import jwt
from server.config import Config



# user route
users = Blueprint('users',__name__)
#create user
@users.route('/user',methods=['POST'])
def creat_user():
    data=request.get_json()
    email = data['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        name = data['user_name']
        password = generate_password_hash(data['password'],method='sha256')
        new_user = User(user_name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message':'New user Created'})
    return jsonify({'message':'email already taken'})

# get all users
@users.route('/user',methods=['GET'])
@token_required
def get_all_user():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['user_name'] = user.user_name
        user_data['email'] = user.email
        output.append(user_data)
    return jsonify({'users': output})

# get one user
@users.route('/user/<int:user_id>',methods=['GET'])
@token_required
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return make_response('user not found',404)
    user_data = {}
    user_data['id'] = user.id
    user_data['user_name'] = user.user_name
    user_data['email'] = user.email
    return jsonify({'users': user_data})

# Update user
@users.route('/user/<int:user_id>',methods=['PUT'])
@token_required
def update_user(user_id):
    if type(user_id) != int:
        return make_response('bad user id',500)
    user = User.query.filter_by(id=user_id).first()
    if user==None:
        return make_response('user does not exist',404,{'WWW-Authenticate':'Basic realm="need existent user"'})
    data = request.get_json()
    password = generate_password_hash(data['password'],method='sha256')
    user.user_name = data['user_name']
    user.email = data['email']
    user.password = password
    db.session.commit()
    return jsonify({'message':'User updated'})
    
# login 
@users.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify',402,{'WWW-Authenticate':'Basic realm="Login Required"'})
    user = User.query.filter_by(email=auth.username).first()
    if not user:
        return make_response('could not verify',401,{'WWW-Authenticate':'Basic realm="Login required"'})
    if check_password_hash(user.password,auth.password):
        token = jwt.encode({"email":user.email,"exp":datetime.datetime.utcnow()+datetime.timedelta(days=7,minutes=30)},Config.SECRET_KEY)
        return jsonify({'token':token.decode('UTF-8')})
    return jsonify({'message':'wrong credentials'})

@users.route('/logout')
def logout():
    logout_user()
    return jsonify({'message':'logged out'})
