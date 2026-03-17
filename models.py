from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    dishes = db.relationship('Dish', backref='category_rel', lazy=True, cascade="all, delete-orphan")

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    price = db.Column(db.Integer, nullable=False)
    precio_socio = db.Column(db.Integer, nullable=True) # <- CAMPO NUEVO
    is_active = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image_file = db.Column(db.String(120), nullable=True)

# <- TABLA NUEVA PARA WHATSAPP
class Configuracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    whatsapp_numero = db.Column(db.String(20), default="56964257112")
    whatsapp_activo = db.Column(db.Boolean, default=True)
    whatsapp_mensaje = db.Column(db.String(250), default="Hola! Estaba viendo el menú y me gustaría hacer un pedido.") 
    whatsapp_activo = db.Column(db.Boolean, default=True)