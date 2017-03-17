from manager import app

from flask import render_template, redirect, url_for
import boto3

s3_bucket_name = 'ece1779assignment1source'

@app.route('/delete_data', methods=['GET'])
def delete_data():

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(s3_bucket_name)
    bucket.objects.delete()

    return redirect(url_for('index'))