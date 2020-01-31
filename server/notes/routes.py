from flask import Flask, request, jsonify, make_response, Blueprint
from server import db
from server.models import *
from server.utils import *
import datetime
import jwt

notes = Blueprint('notes',__name__)
# Notes Routes
@notes.route('/note', methods=['POST'])
@token_required
def create_note():
    data=request.get_json()
    user_id = data['user_id']
    title = data['title']
    body = data['body']
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return make_response('invalid user',404)
    labels_ = data.get('label')
    if labels_:
        for l in labels_:
            label = Label.query.filter_by(id=l).first()
            if not label:
                return jsonify({'message':'invalid label, cannot create note'})
        new_note = Notes(title=title,body=body,user_id=user_id,label=labels_)
        db.session.add(new_note)
        db.session.commit()
        print(new_note)
        for l in labels_:
            label = Label.query.filter_by(id=l).first()
            new_note.labels.append(label)
        # new_note.labels=labels_
        db.session.commit()
        return jsonify({'message':'Note created'})
    new_note = Notes(title=title,body=body,user_id=user_id,label=[])
    db.session.add(new_note)
    db.session.commit()
    return jsonify({'message':'Note created'})
    

# get all notes     
@notes.route('/note', methods=['GET'])
@token_required
def get_all_notes(): # TODO privilage this route to admin only
    notes = Notes.query.all()
    if not notes:
        return jsonify({'message':'Notes are empty'})
    output = []
    for note in notes:
        note_data = {}
        note_data['id'] = note.id
        note_data['title'] = note.title
        note_data['body'] = note.body
        note_data['user_id'] = note.user_id 
        note_data['label'] = note.label
        output.append(note_data)
    return jsonify({'notes':output})


# # get one note
# @notes.route('/note/<int:note_id>',methods=['GET'])
# @token_required
# def get_one_note(note_id): # TODO privilage this route to admin only
#     note = Notes.query.filter_by(id=note_id).first()
#     if not note:
#         return make_response('note not found',404)
#     note_data = {}
#     note_data['id'] = note.id
#     note_data['title'] = note.title
#     note_data['body'] = note.body
#     note_data['user_id'] = note.user_id  
#     note_data['label'] = note.label
#     return jsonify({'note':note_data})



# update note
@notes.route('/note/<int:user_id>/<int:note_id>',methods=['PUT'])
@token_required
def update_note(user_id,note_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message':'User not found'})
    note = Notes.query.filter_by(id=note_id,user_id=user_id).first()
    if not note:
        return make_response('note not found',404)
    data = request.get_json()
    id_check = data.get('user_id')
    if id_check and id_check != user_id:
        return jsonify({'message':'unauthorized update'})
    labels_ = data.get('label')
    if labels_:
        for l in labels_:
            label = Label.query.filter_by(id=l,user_id=user_id).first()
            if not label:
                return jsonify({'message':'cannot update with invalid label'})
        note.title=data['title']
        note.body=data['body']
        note.label=data['label']
        db.session.commit()
        for l in labels_:
            label = Label.query.filter_by(id=l).first()
            note.labels.append(label)
        db.session.commit()
        return jsonify({'message':'Note updated'})    
    note.title = data['title']
    note.body = data['body'] 
    note.label = []
    db.session.commit()
    return jsonify({'message':'Note updated'})
    
#delete note
@notes.route('/note/<int:user_id>/<int:note_id>',methods=['DELETE'])
def del_note(user_id,note_id):
    note = Notes.query.filter_by(id=note_id,user_id=user_id).first()
    if not note:
        return make_response('note not found',400)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message':'note deleted'})




# get all notes for a specific user
@notes.route('/note/<int:user_id>/',methods=['GET'])
@token_required
def get_user_notes(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return make_response('invalid user',400)
    notes = Notes.query.filter_by(user_id=user_id).all()
    if not notes:
        return jsonify({'message':'User has no notes yet'})
    output = []
    for note in notes:
        note_data = {}
        note_data['id'] = note.id
        note_data['title'] = note.title
        note_data['body'] = note.body
        note_data['user_id'] = note.user_id 
        note_data['label'] = note.label
        output.append(note_data)
    return jsonify({'notes':output})

# get a particular note of a particular user
@notes.route('/note/<int:user_id>/<int:note_id>',methods=['GET'])
@token_required
def get_user_note(user_id,note_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return make_response('user not found',404)
    note = Notes.query.filter_by(user_id=user.id,id=note_id).first()
    if not note:
        return make_response('note not found for that user',400)
    note_data = {}
    note_data['id'] = note.id
    note_data['title'] = note.title
    note_data['body'] = note.body
    note_data['user_id'] = note.user_id 
    note_data['label'] = note.label
    return jsonify({'note': note_data})


# get notes by label for a particular user
@notes.route('/<int:user_id>/note/<int:label_id>/',methods=['GET'])
@token_required
def get_label_notes(user_id,label_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message':'user not found'})
    label = Label.query.filter_by(id=label_id,user_id=user_id).first()
    if not label:
        return jsonify({'massage':'label not found, either it doesnt exist or not owned by user'})
    notes = Notes.query.filter(Notes.labels.any(id=label_id))
    schema_note = notes_schemas.dump(notes)
    return jsonify({'notes':schema_note})
    



### end notes routes
######################################################################################################
