from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm  import sessionmaker
import os



app=Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('DB-SECRET-KEY-MU-STASH')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db=SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'

engine=create_engine('sqlite:///site.db')
session=sessionmaker()
session.configure(bind=engine)
my_session=session()

from flaskStash import routes