from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    password1 = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', '비밀번호가 일치하지 않습니다.')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Content', validators=[DataRequired()])

class CommentForm(FlaskForm):
    text = TextAreaField('Comment', validators=[DataRequired()])
    parent_id = HiddenField("parent comment ID")
