from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False) #will hash later

    def __repr__(self):
        return "User('{}','{}')".format(self.username, self.email)


class AuthToken(db.Model):
    __tablename__ = 'authtoken'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    access_token = db.Column(db.String(1000), nullable=False)
    token_type = db.Column(db.String(100), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    refresh_token = db.Column(db.String(1000), nullable=False)
    scope = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return "AuthToken('{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.id,
            self.access_token,
            self.token_type,
            self.expires_at,
            self.refresh_token,
            self.scope
        )
