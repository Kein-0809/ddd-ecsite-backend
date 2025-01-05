from ... import db

class UserModel(db.Model):
    """ユーザーモデル"""
    __tablename__ = 'users'

    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)