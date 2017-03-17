import os

from flask import render_template, redirect, url_for, request, session
from user import app, db


@app.route('/thumbs', methods=['GET'])
# Show thumbnail view
def thumbs():
    if 'username' not in session:
        return "you must be logged in to do that"

    images, ids = db.get_images(session['username'])

    return render_template('thumbs/thumbs.html',
                           images_ids=zip(images,ids),
                           page_header="Your Images")


@app.route('/thumbs/<id>', methods=['GET'])
def thumbs_view(id):
    if 'username' not in session:
        return "you must be logged in to do that"

    image_urls = get_urls(id)

    return render_template("imagetransform/view.html",
                           f1=image_urls[0],
                           f2=image_urls[1],
                           f3=image_urls[2],
                           f4=image_urls[3],
                           page_header="Image and Transformations")


# Get all of urls of an image and its transformations
def get_urls(id):
    cnx = db.connect_to_database()
    cursor = cnx.cursor()

    user_id = db.get_user_id(session['username'])
    if user_id is None:
        return None

    query = '''
                SELECT key1, key2, key3, key4 FROM images WHERE users_id = %s AND id = %s
                '''

    cursor.execute(query, (user_id, id))
    rows = cursor.fetchall()

    url_start = "https://s3.amazonaws.com/ece1779assignment1source/"

    image_urls = []
    for row in rows:
        for key in row:
            image_urls.append(url_start + key)

    cursor.close()
    cnx.close()

    return image_urls
