from flask_login import UserMixin
from extensions import db   # 👈 IMPORTANT FIX

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    city = db.Column(db.String(100))
    price = db.Column(db.Integer)
    image = db.Column(db.String(300))


class Purchase(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    house_id = db.Column(db.Integer, db.ForeignKey('house.id'))

    buyer_name = db.Column(db.String(100))

    phone = db.Column(db.String(20))

    status = db.Column(db.String(20), default='Pending')