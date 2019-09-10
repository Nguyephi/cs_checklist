from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(500), unique=True)
    password = db.Column(db.String(255))
    profile_pic = db.Column(db.String, default=('default.png'))
    is_admin = db.Column(db.Boolean, default=False)
    bio = db.Column(db.String)
    oauth = db.relationship('OAuth', backref='user', cascade='all,delete')
    is_done = db.relationship(
        'isTodosDone', backref='user', cascade='all,delete', lazy=True)

    def __repr__(self):
        return '<User {}self.name'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)


class Todos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(500))
    subTask = db.relationship(
        'SubTodos', backref='todos', cascade="all,delete")
    is_done = db.relationship(
        'isTodosDone', backref='todos', cascade='all,delete')


class SubTodos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subTask = db.Column(db.String)
    todo_id = db.Column(db.Integer, db.ForeignKey('todos.id'), nullable=False)
    is_done = db.relationship(
        'isTodosDone', backref='sub_todos', cascade='all,delete')


class isTodosDone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    todo_id = db.Column(db.Integer, db.ForeignKey('todos.id'))
    sub_todo_id = db.Column(
        db.Integer, db.ForeignKey('sub_todos.id'))
    is_done = db.Column(db.Boolean, default=False)


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.request_loader
def load_user_from_request(request):
    # Login Using our Custom Header
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Token ', '', 1)
        token = Token.query.filter_by(uuid=api_key).first()
        if token:
            return token.user

    return None
