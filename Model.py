from flask import Flask
from marshmallow import Schema, fields, pre_load, validate, post_load
from marshmallow.exceptions import ValidationError
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy


ma = Marshmallow()
db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__= True
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Category(BaseModel):
    __tablename__ = 'categories'
    name = db.Column(db.String(150), unique=True, nullable=False)

    # def __init__(self, name):
    #     self.name = name
    
class Comment(BaseModel):
    __tablename__ = 'comments'
    comment = db.Column(db.String(250), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    category = db.relationship('Category', backref=db.backref('comments', lazy='dynamic' ))

    # def __init__(self, comment, category_id):
    #     self.comment = comment
    #     self.category_id = category_id


    


class CategorySchema(ma.Schema):
    id = fields.Integer()
    name = fields.String(required=True)

    @post_load
    def validate_name(self, data):
        name = data['name']
        category = Category.query.filter(Category.name==name.lower()).first()
        if category:
            raise ValidationError({'message':'category already exists'})


class CommentSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    category_id = fields.Integer(required=True, dump_to='categoryId')
    comment = fields.String(required=True, validate=validate.Length(1))
    creation_date = fields.DateTime()