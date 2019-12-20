from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
# import sqlite3
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

from data import ArticleForm, RegisterForm, LoginForm

app = Flask(__name__)

# Config 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize mysql
mysql = MySQL(app)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/about')
def about():
  return render_template('about.html')

def get_data(query, isOne=False):
  cur = mysql.connection.cursor()

  cur.execute(query)
  if isOne:
    articles = cur.fetchone()
  else:
    articles = cur.fetchall()

  cur.close()
  return articles

def set_data(query):
  cur = mysql.connection.cursor()
  cur.execute(query)
  mysql.connection.commit()
  cur.close()

@app.route('/articles')
def articles():
  try:
    articles = get_data("SELECT articles.id, articles.title, articles.body, users.name from articles inner join users where articles.author=users.id")
    return render_template('articles.html', articles=articles)
  except Exception:
    return "Please check for the database server"

@app.route('/article/<int:id>')
def article(id):
  article = get_data("SELECT * from ARTICLES WHERE id={}".format(id), True)

  author = get_data("SELECT * from USERS where id={}".format(article['author']), True)
  print(author['name'])
  article['author'] = author['name']
  return render_template('article.html', article=article)

@app.route('/register', methods=['GET', 'POST'])
def register():
  form = RegisterForm(request.form)
  if request.method == 'POST' and form.validate():
    name = form.name.data
    username = form.username.data 
    email = form.email.data 
    password = sha256_crypt.hash(str(form.password.data))

    query = "INSERT into USERS(name, email, username, password) values('{}', '{}', '{}', '{}')".format(name, email, username, password)
    set_data(query)

    flash("U r now registered.", "success")

    return redirect(url_for('login'))

  return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm(request.form)
  if request.method == 'POST' and form.validate():
    username = request.form['username']
    password_candidate = request.form['password']

    user = get_data("SELECT * from USERS where username='{}'".format(username), True)

    password = user['password']

    if sha256_crypt.verify(password_candidate, password):
      session['logged_in'] = True
      session['username'] = username
      return redirect(url_for('dashboard'))
    else:
      error = 'Invalid Credentials'
      return render_template('login.html', form=form, error=error)
    
    flash("U r now registered.", "success")

  return render_template('login.html', form=form)

def is_logged_in(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      flash('Un-authorized: Please login first', 'danger')
      return redirect(url_for('login'))
    
  return wrap

@app.route('/dashboard')
@is_logged_in
def dashboard():
  articles = get_data("SELECT articles.id, articles.title, users.name from articles inner join users where articles.author=users.id")
  print(articles)
  return render_template('dashboard.html', articles = articles)

@app.route('/logout')
@is_logged_in
def logout():
  session.clear()
  flash('You are now logged out.', 'success')
  return redirect(url_for('login'))

@app.route('/create-article', methods=['POST', 'GET'])
@is_logged_in
def create_article():
  form = ArticleForm(request.form)
  if request.method == 'POST':
    title = request.form['title']
    body = request.form['body']

    user = get_data("SELECT * from users where username='{}'".format(session['username']), True)
    userId = user['id']
    set_data("INSERT into articles(title, body, author) values('{}', '{}', '{}')".format(title, body, userId))
      
    flash('Article was saved successfully', 'success')
    return redirect(url_for('dashboard'))
  
  return render_template('create-article.html', form=form, action="/create-article")

@app.route('/edit-article/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def edit_article(id):
  article = get_data("select * from articles where id={}".format(id), True)

  form = ArticleForm(request.form)

  form.title.data = article['title']
  form.body.data = article['body']
  
  if request.method == 'POST' and form.validate():
    title = request.form['title']
    body = request.form['body']
    
    query = "UPDATE articles SET title='{}', body='{}' where id={}".format(title, body, id)
    set_data(query)

    flash('Article was saved successfully', 'success')
    return redirect(url_for('articles'))
  
  return render_template('create-article.html', form=form, action="/edit-article/{}".format(id))

@app.route('/delete-article', methods=['POST'])
@is_logged_in
def delete_article():
  id = request.form['id']

  query = "DELETE from articles where id={}".format(id)
  print(query)
  set_data(query)
  flash("Article was deleted successfully", 'success')
  return redirect(url_for('dashboard'))

if __name__ == '__main__':
  app.secret_key = 'secret1234'
  app.run(debug=1)