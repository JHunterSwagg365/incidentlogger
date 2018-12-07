from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from incidentlogger.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username not available, Please pick a different one.')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account has already been maid with that email. Please pick a different one or Login.')


class LoginForm(FlaskForm):
    email = StringField('Email',
        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class IncidentForm(FlaskForm):
    # category = group_id = SelectField('Category', coerce=int)
    category = SelectField('Category', choices=[('cpp', 'Filler'), ('py', 'choices'), ('text', 'database will fill')])
    description = TextAreaField('Description', validators =[DataRequired(), Length(min =2,max=200)])
    date_created = DateField('Date Created', format = "%m/%d/%Y", validators=[DataRequired()])
    date_resolved = DateField('Date Created', format = "%m/%d/%Y")
    state = StringField('State', validators = [DataRequired(), Length(min = 2, max = 20)])
    point_contact = StringField('Username',
        validators=[DataRequired(), Length(min=2, max=20)])
    tags = StringField('State', validators = [Length(min = 2, max = 20)])
    current_assignee = StringField('Currently Worked on By', validators = [DataRequired(), Length(min = 2, max = 20)])
    case_history = TextAreaField('Description', validators =[DataRequired(), Length(min =2,max=200)])
    submit = SubmitField('Confirm Incident')

#def edit_user(request, id):
#   user = User.query.get(id)
#  form = UserDetails(request.POST, obj=user)
# form.group_id.choices = [(g.id, g.name) for g in Group.query.order_by('name')]