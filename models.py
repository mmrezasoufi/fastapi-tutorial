import datetime
import sqlalchemy as sql
import sqlalchemy.orm as orm
import passlib.hash as hash
import database as db


class UserModel(db.Base):
    __tablename__ = "users"
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    email = sql.Column(sql.String, unique=True, index=True)
    name = sql.Column(sql.String)
    phone = sql.Column(sql.String)
    password_hash = sql.Column(sql.String)
    created_at = sql.Column(sql.DateTime, default=datetime.datetime.utcnow())
    posts = orm.relationship("PostModel", back_populates="user")

    def password_verification(self, password: str):
        return hash.bcrypt.verify(password, self.password_hash)


class PostModel(db.Base):
    __tablename__ = "posts"
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey("users.id"))
    post_title = sql.Column(sql.String, index=True)
    post_description = sql.Column(sql.String, index=True)
    image = sql.Column(sql.String)
    created_at = sql.Column(sql.DateTime, default=datetime.datetime.utcnow())
    user = orm.relationship("UserModel", back_populates="posts")
