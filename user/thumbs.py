from flask import render_template, redirect, url_for, request, session
from user import app, db


@app.route('/thumbs', methods=['GET'])
# Show thumbnail view
def thumbs():
    if 'username' not in session:
        return "you must be logged in to do that"

    images = db.get_images(session['username'])

    return render_template('thumbs/thumbs.html',
                           images=images,
                           page_header="Your Images")
