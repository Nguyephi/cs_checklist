from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, DataRequired, ValidationError, Length, Email, EqualTo
from .models import User


class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[
                       InputRequired(), Length(min=3, max=255)])
    email = StringField('Email', validators=[
                        InputRequired(), Length(min=3, max=500), Email()])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=6, max=255)])
    pass_confirm = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

    # def validate_name(self, field):
    #     if User.query.filter_by(name=field.data).first():
    #         raise ValidationError("This name has been registered!")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email has been used!")


class SignInForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(
        message='Sign in with your registered name.')])
    password = PasswordField('Password', validators=[
                             InputRequired(message='Incorrect password.')])
    submit = SubmitField('Signin')


class EditProfile(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired()])
    submit = SubmitField('Update Profile')

    def validate_email(self, email):
        if email.data == current_user.email:
            if User.query.filter_by(email=email.data).first():
                raise ValidationError("Email has been used!")


class AddTodo(FlaskForm):
    task = StringField('task', validators=[InputRequired()])
    subTask = StringField('subTask')
    submit = SubmitField('Add task')
