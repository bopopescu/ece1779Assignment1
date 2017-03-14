from manager import app

from flask import render_template, redirect, url_for


@app.route('/admin')
# main landing page
def admin():
    return render_template("/admin/admin.html",
                           title="ECE 1779 - Assignment 1 - Admin",
                           page_header="Welcome to ECE1771 Assignment 1 Manager")
