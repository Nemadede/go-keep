from server import db,ma



notes_label = db.Table('NotesLabel',
                       db.Column('notes_id',db.Integer,db.ForeignKey('notes.id')),
                       db.Column('label_id',db.Integer,db.ForeignKey('label.id')))

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(50))
    email = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(80))
    notes = db.relationship('Notes',backref=db.backref('note',lazy=True))

class Notes(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title= db.Column(db.String(100), unique=False)
    body = db.Column(db.Text, unique=False)
    labels= db.relationship('Label',secondary=notes_label)
    label = db.Column(db.ARRAY(db.Integer),nullable=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False )
    

class Label(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False,unique=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False )
    notes= db.relationship('Notes',secondary=notes_label)
    user = db.relationship('User',backref=db.backref('label',lazy=True))
    
    def __init__(self,name,user_id):
        self.name=name
        self.user_id=user_id
        
class LabelSchema(ma.ModelSchema):
     class Meta:
        fields=('id','name','user_id')

label_schema=LabelSchema()
label_schemas=LabelSchema(many=True)
    