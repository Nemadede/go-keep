from flask import Flask, request, jsonify, make_response
from server.config import Config
import datetime
import jwt
from functools import wraps


## require token decorator for routes that need a user to be logged in

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message':'Token is missing'}), 401
        try:
            data = jwt.decode(token, Config.SECRET_KEY)
        except:
            return jsonify({'message':'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated






