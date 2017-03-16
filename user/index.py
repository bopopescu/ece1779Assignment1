from user import app

from flask import render_template, redirect, url_for


@app.route('/')
# main landing page
def index():
    return render_template("index.html",
                           page_header="Welcome to ECE1779 Assignment 1")
