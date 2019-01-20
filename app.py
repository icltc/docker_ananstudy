from flask import Flask,render_template, flash, redirect, url_for, request
from redis import Redis, RedisError
import os
import socket
from datetime import datetime

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import DateTimeField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SearchForm(FlaskForm):
  fromdatetime = DateTimeField('From:', default=datetime.now())
  todatetime = DateTimeField('To:', default=datetime.now())
  search = SubmitField('Search')

@app.route("/", methods=['GET', 'POST'])
def login():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    form = LoginForm()
    if form.validate_on_submit():
      return redirect(url_for('index', 
                              user=form.username.data, 
                              todatetime="2000",
                              fromdatetime="now"))

    return render_template('login.html', title='Login', form=form)

@app.route("/test")
def test():
  return "Hello word"

@app.route("/index", methods=['GET', 'POST'])
def index():
  posts = [
      {
          'author': {'username': 'John'},
          'body': 'Beautiful day in Portland!'
      },
      {
          'author': {'username': 'Susan'},
          'body': 'The Avengers movie was so cool!'
      }
  ]
  user = request.args['user']
  sf = SearchForm()
  if sf.is_submitted():
    print sf.fromdatetime.data
    return redirect(url_for('index', 
      user=user, 
      fromdatetime=sf.fromdatetime.data,
      todatetime=sf.todatetime.data))
  return render_template('index.html', 
                         title='Home', 
                         user=request.args['user'], 
                         fromdatetime=request.args['fromdatetime'],
                         todatetime=request.args['todatetime'],
                         posts=posts, 
                         form=sf)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
