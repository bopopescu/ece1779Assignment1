from flask import render_template, redirect, url_for, request, session
from user import app, db


@app.route('/thumbs/', methods=['GET'])
# Show thumbnail view
def image_form():
    if 'username' not in session:
        return "you must be logged in to do that"
    return render_template("thumbs/index.html", images=db.get_images(session['username']))
