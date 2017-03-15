from flask import render_template, redirect, url_for, request
from user import app

from wand.image import Image

import boto3
import os


@app.route('/test/FileUpload/form', methods=['GET'])
# Return file upload form
def upload_form():
    return render_template("fileupload/form.html",
                           page_header = "File Upload")


@app.route('/test/FileUpload', methods=['POST'])
# Upload a new file and store in the systems temp directory
def file_upload():
    userid = request.form.get("userID")
    password = request.form.get("password")

    # check if the post request has the file part
    if 'uploadedfile' not in request.files:
        return "Missing uploaded file"

    new_file = request.files['uploadedfile']

    # if user does not select file, browser also
    # submit a empty part without filename
    if new_file.filename == '':
        return 'Missing file name'

    # following line was in the provided code
    # tempdir = tempfile.gettempdir()

    # file is first saved and transformed locally, then it will be uploaded to S2
    fname = os.path.join('user/static', new_file.filename)
    new_file.save(fname)
    img = Image(filename=fname)

    # rotate the image and save
    i1 = img.clone()
    i1.rotate(180)
    fname_rotated = os.path.join('user/static', 'rotated_' + new_file.filename)
    i1.save(filename=fname_rotated)

    # equalize the image and save
    i2 = img.clone()
    i2.equalize()
    fname_equalized = os.path.join('user/static', 'equalized_' + new_file.filename)
    i2.save(filename=fname_equalized)

    # make a negative of the image and save
    i3 = img.clone()
    i3.negate()
    fname_negative = os.path.join('user/static', 'negative_' + new_file.filename)
    i3.save(filename=fname_negative)

    # save files to S3
    s3 = boto3.client('s3')
    s3.upload_file(fname,
                   'ece1779assignment1source',
                   os.path.basename(fname))
    s3.upload_file(fname_rotated,
                   'ece1779assignment1source',
                   os.path.basename(fname_rotated))
    s3.upload_file(fname_equalized,
                   'ece1779assignment1source',
                   os.path.basename(fname_equalized))
    s3.upload_file(fname_negative,
                   'ece1779assignment1source',
                   os.path.basename(fname_negative))

    # save s3 keys to images database
    #todo

    # delete local copies of image
    #todo

    # temporarily redirect to page showing image, but should redirect to landing page
    #todo redirect to "show my images" page

    return "Success"
