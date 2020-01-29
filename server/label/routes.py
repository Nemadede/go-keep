from flask import Flask, request, jsonify, make_response, Blueprint
from server import db
from server.utils import *
from server.models import *
import datetime
import jwt


#begin label routes
labels = Blueprint('labels',__name__)
# create label
@labels.route('/label',methods=['POST'])
@token_required
def create_label():
    data = request.get_json()
    name = data['name']
    if isinstance(name, int):
        name = str(name)
    if ' ' in name:
        return make_response('Label name Should not contain spaces',400)
    elif len(name) > 25:
        return make_response('Label name too long',400)
    user_id = data['user_id']
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return make_response('null user cannot create label',400)
    label = Label.query.filter_by(name=name,user_id=user.id).first()
    if not label:
        new_label = Label(name=name,user_id=user_id)
        db.session.add(new_label)
        db.session.commit()
        return jsonify({'message':'label created'})
    return make_response('label exist',403)

#get all labels
@labels.route('/label', methods=['GET'])
def get_labels():
    labels = Label.query.all()
    count = 0
    for label in labels:
        count = count+1
    result = label_schemas.dump(labels)
    return jsonify({'count':count},{"labels":result})

#get one label
@labels.route('/label/<int:label_id>',methods=['GET'])
def get_label(label_id):
    label = Label.query.filter_by(id=label_id).first()
    if not label:
        return jsonify({'message':'label not found'})
    schema_label = label_schema.dump(label)
    
    return jsonify({'data': schema_label})


    
# Update label
@labels.route('/label/<int:label_id>',methods=['PUT'])
def update_label(label_id):
    label = Label.query.filter_by(id=label_id).first()
    if not label:
        return make_response('label not found',404)
    data = request.get_json()
    label.name = data['name']
    db.session.commit()
    return jsonify({'message':'user updated'})

@labels.route('/label/<int:label_id>', methods=['DELETE'])
def delete_label(label_id):
    label = Label.query.filter_by(id=label_id).first()
    if not label:
        return make_response('label not found',404)
    db.session.delete(label)
    db.session.commit()
    return jsonify({'message':'label deleted'})
# TODO Update label and delete label