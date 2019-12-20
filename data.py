from wtforms import Form, StringField, TextAreaField, PasswordField, validators

class LoginForm(Form):
  username = StringField('Username', [validators.Length(min=4, max=25)])
  password = PasswordField('Password', [validators.DataRequired()])

class RegisterForm(Form):
  name = StringField('Name', [validators.Length(min=1, max=50)])
  username = StringField('Username', [validators.Length(min=4, max=25)])
  email = StringField('Email', [validators.Length(min=6, max=50)])
  password = PasswordField('Password', [
    validators.DataRequired(),
    validators.EqualTo('confirm', message='Passwords do not match')
  ])
  confirm = PasswordField('Confirm Password')

class ArticleForm(Form):
  title = StringField('Title', [validators.Length(min=5, max=255)])
  body = TextAreaField('Body', [validators.Length(min=4)])