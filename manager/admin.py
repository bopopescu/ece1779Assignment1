from flask import request

from manager import app

from flask import render_template, redirect, url_for

from manager import monitor_pool


@app.route('/admin', methods=['GET', 'POST'])
# main landing page
def admin():
    if request.method == 'GET':
        return render_template("/admin/admin.html",
                               page_header="Welcome to ECE1771 Assignment 1 Manager",
                               pv=monitor_pool.PolicyVars())
    elif request.method == 'POST':
        try:
            high = int(request.form.get('high'))
            low = int(request.form.get('low'))
            mult = int(request.form.get('mult'))
            div = int(request.form.get('div'))
        except:
            errors = ["All inputs must be numeric"]
            return render_template("/admin/admin.html",
                                   page_header="Welcome to ECE1771 Assignment 1 Manager",
                                   pv=monitor_pool.PolicyVars(),
                                   errors=errors)

        errors = check_errors(high, low, mult, div)
        if errors:
            return render_template("/admin/admin.html",
                                   page_header="Welcome to ECE1771 Assignment 1 Manager",
                                   pv=monitor_pool.PolicyVars(),
                                   errors=errors)

        pv = monitor_pool.PolicyVars()
        pv.high_cpu_threshold = high
        pv.low_cpu_threshold = low
        pv.scaling_multiplier = mult
        pv.scaling_divisor = div

        return render_template("/admin/admin.html",
                               page_header="Welcome to ECE1771 Assignment 1 Manager",
                               pv=monitor_pool.PolicyVars())


def check_errors(high, low, mult, div):
    errors = []

    if high > 100:
        errors.append("High CPU threshold cannot be larger than 100")
    if high <= low:
        errors.append("High CPU threshold must be larger than low CPU threshold")
    if low < 0:
        errors.append("High CPU threshold cannot be less than 0")
    if mult < 2:
        errors.append("Scaling multiplier must be 2 or larger")
    if div < 2:
        errors.append("Scaling divisor must be 2 or larger")

    return errors
