from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, DateTimeLocalField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    deadline = StringField('Deadline', validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        (0, 'Normal'), 
        (1, 'Important'), 
        (2, 'Urgent'), 
        (3, 'Critical')
    ], coerce=int, default=0)
    submit = SubmitField('Add Task')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password (leave blank to keep current)')
    confirm_password = PasswordField('Confirm New Password', 
                                    validators=[EqualTo('password')])
    submit = SubmitField('Update Profile')
