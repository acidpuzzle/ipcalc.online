import logging

from flask.views import View
from flask import request, render_template, jsonify

from ip_calc_app import application
from calculator import calc_dispatcher
from gen_pass import generate_passwords
from sort_sum import get_sorted_nets, sum_nets, get_out_form


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class IPCalc(View):
    init_every_request = False

    def __init__(self, template):
        self.template = template

    def dispatch_request(self):
        context = {"version": application.version}
        raw_request_string = request.args.get('network', '')
        if raw_request_string:
            context = calc_dispatcher(raw_request_string)
            application.logger.debug(f"{raw_request_string=}")
            application.logger.debug(f"{context=}")

        return render_template(self.template, **context)


class GenPass(View):
    init_every_request = False

    def __init__(self, template):
        self.template = template

    def dispatch_request(self):
        context = {}
        if request.args:
            context = generate_passwords(**request.args)

        return render_template(self.template, **context)


class SortSum(View):
    init_every_request = False

    methods = ["GET", "POST"]

    def __init__(self, template):
        self.template = template

    def dispatch_request(self):
        context = {}
        if request.method == 'POST':
            out_form = request.form.get("output_format")
            raw_user_nets = request.form.get("user_nets")
            user_nets = []
            errors = []

            if request.form['action'] == "sort":
                user_nets, errors = get_sorted_nets(raw_user_nets)

            if request.form['action'] == "sum":
                user_nets, errors = sum_nets(raw_user_nets)

            context = {
                "user_nets": raw_user_nets,
                "sorted_nets": get_out_form(user_nets, out_form),
                "errors": errors,
                "output_format": out_form,
            }

        return render_template(self.template, **context)


@application.route('/faq')
def faq():
    return render_template("faq.html")


@application.route('/about')
def about():
    return render_template("about.html")


@application.route('/api/<network>')
def api(network):
    if network:
        context = calc_dispatcher(network)
        return jsonify(context)


@application.errorhandler(404)
def page_not_found(e):
    return render_template('error_template/404.html'), 404


@application.errorhandler(500)
def page_not_found(e):
    return render_template('error_template/500.html'), 500


application.add_url_rule("/", view_func=IPCalc.as_view("ipcalc", "index.html"), )
application.add_url_rule("/gen_pass", view_func=GenPass.as_view("gen_pass", "gen_pass.html"), )
application.add_url_rule("/sort_sum", view_func=SortSum.as_view("sort_sum", "sort_sum.html"), )
