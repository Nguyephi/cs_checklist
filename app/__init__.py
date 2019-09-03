import os
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_manager, current_user, logout_user, login_required
from flask_migrate import Migrate
from .cli import create_db
from .config import Config
from .models import db, User, Todos, login_manager
from .oauth import blueprint, github_blueprint
from .forms import SignUpForm, SignInForm, EditProfile, AddTodo

app = Flask(__name__)
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
    signup_form = SignUpForm()
    signin_form = SignInForm()

    if signup_form.validate_on_submit():
        new_user = User(name=signup_form.name.data,
                        email=signup_form.email.data)
        new_user.set_password(signup_form.password.data)
        flash(
            f'Hey {signup_form.name.data.capitalize()}, you have successfully created a new account! Please login to view checklist', 'success')
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))

    if signin_form.validate_on_submit():
        name = signup_form.name.data.strip()
        log_user = User.query.filter_by(name=name).first()

        if log_user is None:
            flash(
                f'This name does not exist, please signup', 'danger')
            return render_template('index.html', signup_form=signup_form, signin_form=signin_form)

        if not log_user.check_password(signin_form.password.data):
            flash(
                f'Invalid password', 'danger')
            return render_template('index.html', signup_form=signup_form, signin_form=signin_form)

        login_user(log_user)
        return render_template('home.html')
    return render_template('index.html', signup_form=signup_form, signin_form=signin_form)


@app.route('/home', methods=['GET'])
@login_required
def home():
    user = User.query.filter_by(id=current_user.id).one()
    admin = User.query.filter_by(is_admin=True, id=current_user.id).first()
    todo_form = AddTodo()
    if todo_form.validate_on_submit():
        new_todo = Todos(title=todo_form.title.data,
                         description=todo_form.description.data)
        flash('New todo has been added!', 'success')
        db.session.add(new_todo)
        db.session.commit()
    return render_template('home.html', admin=admin)

    # return render_template('checklist.html', admin=admin)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return redirect(url_for("index"))


@app.route('/editprofile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfile()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        flash(f'Your account has been updated!', 'success')
        db.session.commit()
    return render_template('editprofile.html', form=form)


if (__name__) == '__main__':
    app.run(debug=True)
