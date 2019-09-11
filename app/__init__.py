import os
from flask import Flask, render_template, session, request, redirect, url_for, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_manager, current_user, logout_user, login_required
from flask_migrate import Migrate
from .cli import create_db
from .config import Config
from .models import db, User, OAuth, Todos, SubTodos, login_manager, isTodosDone, Token
from .oauth import blueprint, github_blueprint
from .forms import SignUpForm, SignInForm, EditProfile, AddTodo
import uuid
from sqlalchemy.orm.exc import NoResultFound


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
app.config.from_object(Config)
app.register_blueprint(blueprint, url_prefix="/login")
app.cli.add_command(create_db)
db.init_app(app)
login_manager.init_app(app)


migrate = Migrate(app, db, compare_type=True)

app.register_blueprint(github_blueprint, url_prefix='/github_login')

POSTGRES = {
    'user': os.environ['POSTGRES_USER'],
    'pw': os.environ['POSTGRES_PWD'],
    'db': os.environ['POSTGRES_DB'],
    'host': os.environ['POSTGRES_HOST'],
    'port': os.environ['POSTGRES_PORT'],
}

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:\
%(port)s/%(db)s' % POSTGRES

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('sign_in'))


@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    signin_form = SignInForm()
    # no errors from forms. need to fix this.
    if request.method == 'POST':
        if signin_form.validate_on_submit():
            name = signin_form.name.data
            log_user = User.query.filter_by(name=name).first()
            if log_user is None:
                flash(
                    f'Name not registered.', 'danger')
                return redirect(url_for('sign_in'))

            if not log_user.check_password(signin_form.password.data):
                flash(f'Invalid password', 'danger')
                return redirect(url_for('sign_in'))

            login_user(log_user)
            token_query = Token.query.filter_by(user_id=current_user.id)
            try:
                token = token_query.one()
            except NoResultFound:
                token = Token(user_id=current_user.id, uuid=uuid.uuid4().hex)
                db.session.add(token)
                db.session.commit()
            return redirect(f'https://127.0.0.1:5000/home?api_key={token.uuid}')
    return render_template('signInForm.html', signin_form=signin_form)


@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
    signup_form = SignUpForm()
    if request.method == 'POST':
        if signup_form.validate_on_submit():
            new_user = User(name=signup_form.name.data,
                            email=signup_form.email.data)
            new_user.set_password(signup_form.password.data)
            flash(
                f'Hey {signup_form.name.data.capitalize()}, you have successfully created a new account! Please login to view checklist', 'success')
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index'))

    return render_template('signUpForm.html', signup_form=signup_form)


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    templates = ['home.html', 'HomePage/checkList.html',
                 'HomePage/editTodo.html', 'Admin/addTodo.html',
                 'HomePage/currentUserCard.html', 'includes/_navbar.html']
    admin = User.query.filter_by(is_admin=True, id=current_user.id).first()
    provider = OAuth.query.filter_by(user_id=current_user.id).first() or None
    todos = Todos.query.order_by(Todos.id).all()
    # subTodos = SubTodos.query.order_by(SubTodos.id).all()
    todo_form = AddTodo()
    edit_form = AddTodo()
    id = 1
    if request.method == 'POST':
        if todo_form.validate_on_submit():
            new_task = Todos(task=todo_form.task.data)
            if len(request.form.getlist('subTask')) > 0:
                for sub_task in request.form.getlist('subTask'):
                    if len(sub_task) > 0:
                        new_subTask = SubTodos(subTask=sub_task)
                        new_task.subTask.append(new_subTask)
                        db.session.add(new_subTask)
            flash('New todo has been added!', 'success')
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template(templates, admin=admin, todo_form=todo_form, todos=todos, edit_form=edit_form, provider=provider)


@app.route('/add', methods=['POST'])
@login_required
def add():
    return 'ok'


@app.route('/delete/<int:todo_id>', methods=['DELETE'])
@login_required
def delete(todo_id):
    todo = Todos.query.filter_by(id=todo_id).one()
    # is_done = isTodosDone.query.filter_by(todo_id=todo_id).all()
    admin = User.query.filter_by(is_admin=True, id=current_user.id).first()
    if admin:
        if request.method == 'DELETE':
            db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/deletesub/<int:todo_id>', methods=['DELETE'])
@login_required
def delete_sub(todo_id):
    todo = SubTodos.query.filter_by(id=todo_id).first()
    admin = User.query.filter_by(is_admin=True, id=current_user.id).first()
    if admin:
        if request.method == 'DELETE':
            db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/edit/<int:todo_id>', methods=['GET'])
@login_required
def edit(todo_id):
    todo = Todos.query.filter_by(id=todo_id).one()
    send_data = {
        'todo': todo.task
    }
    return jsonify(send_data)


@app.route('/editsub/<int:todo_id>', methods=['GET'])
@login_required
def edit_sub(todo_id):
    todo = SubTodos.query.filter_by(id=todo_id).one()
    send_data = {
        'todo': todo.subTask
    }
    return jsonify(send_data)


@app.route('/update/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def update(todo_id):
    data = request.get_json()
    todo = Todos.query.filter_by(id=todo_id).one()
    if request.method == 'POST':
        todo.task = data['todo']
        db.session.commit()
    send_data = {
        'todo': todo.task
    }
    return jsonify(send_data)


@app.route('/updatesub/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def update_sub(todo_id):
    data = request.get_json()
    todo = SubTodos.query.filter_by(id=todo_id).one()
    if request.method == 'POST':
        todo.subTask = data['todo']
        db.session.commit()
    send_data = {
        'todo': todo.subTask
    }
    return jsonify(send_data)


@app.route("/logout")
@login_required
def logout():
    token = Token.query.filter_by(user_id=current_user.id).one()
    db.session.delete(token)
    db.session.commit()
    logout_user()
    flash("You have logged out")
    return redirect(url_for("index"))


@app.route('/editprofile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    template = ['editprofile.html', 'includes/_navbar.html']
    admin = User.query.filter_by(is_admin=True, id=current_user.id).first()
    provider = OAuth.query.filter_by(user_id=current_user.id).one() or None
    form = EditProfile()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        flash(f'Your account has been updated!', 'success')
        db.session.commit()
    return render_template(template, admin=admin, form=form, provider=provider)


@app.route('/isdone/<int:todo_id>', methods=['POST', 'GET'])
@login_required
def is_done(todo_id):
    todo = Todos.query.filter_by(id=todo_id).one()
    if request.method == 'POST':
        check_todo = isTodosDone.query.filter_by(
            user_id=current_user.id, todo_id=todo_id).first()
        if not check_todo:
            user = User.query.filter_by(id=current_user.id).first()
            isDone = isTodosDone(todo_id=todo.id, is_done=True)
            user.is_done.append(isDone)
            todo.is_done.append(isDone)
            db.session.add(isDone)
        elif check_todo.is_done == True:
            check_todo.is_done = False
        elif check_todo.is_done == False:
            check_todo.is_done = True
        db.session.commit()
        return "hjhjhjhj"
    return redirect(url_for('home'))


@app.route('/issubdone/<int:todo_id>', methods=['POST', 'GET'])
@login_required
def is_sub_done(todo_id):
    todo = SubTodos.query.filter_by(id=todo_id).one()
    print('============', todo)
    if request.method == 'POST':
        check_todo = isTodosDone.query.filter_by(
            user_id=current_user.id, sub_todo_id=todo_id).first()
        if not check_todo:
            user = User.query.filter_by(id=current_user.id).first()
            isDone = isTodosDone(is_done=True)
            user.is_done.append(isDone)
            todo.is_done.append(isDone)
            db.session.add(isDone)
        elif check_todo.is_done == True:
            check_todo.is_done = False
        elif check_todo.is_done == False:
            check_todo.is_done = True
        db.session.commit()
        return "hjhjhjhj"
    return redirect(url_for('home'))


@app.route('/checklistdata', methods=['GET'])
@login_required
def check_list_data():
    checklist = isTodosDone.query.filter_by(user_id=current_user.id).all()
    send_data = {'checklist': [{
        'is_done': i.is_done,
        'todo_id': i.todo_id,
        'sub_todo_id': i.sub_todo_id
    } for i in checklist]}
    return jsonify(send_data)


@app.route('/studentprogress')
@login_required
def student_progress():
    template = ['studentProgress.html', 'includes/_navbar.html']
    admin = User.query.filter_by(is_admin=True, id=current_user.id).first()
    users = User.query.filter_by(is_admin=False).all()
    lst_td = isTodosDone.query.join(User).with_entities(isTodosDone.todo_id, isTodosDone.user_id).filter(
        isTodosDone.is_done == True, User.is_admin == False).all()
    lst_sub_td = isTodosDone.query.join(User).with_entities(isTodosDone.sub_todo_id, isTodosDone.user_id).filter(
        isTodosDone.is_done == True, User.is_admin == False).all()
    todos = Todos.query.all()
    return render_template(template, admin=admin, users=users, todos=todos, lst_td=lst_td, lst_sub_td=lst_sub_td)


if (__name__) == '__main__':
    app.run(debug=True)
