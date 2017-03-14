from flask import Flask

app = Flask(__name__)

from manager import db
from manager import worker
from manager import loadbalancer
from manager import index
from manager import login_register
from manager import start
from manager import stop
from manager import admin
