from app import app

from flask import render_template, redirect, url_for

@app.route('/')
#main landing page
def index():
    return render_template("index.html",
                           title="ECE 1779 - Assignment 1",
                           page_header="Welcome to ECE1771 Assignment 1")
