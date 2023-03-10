from flask.views import View
from flask import request, render_template, jsonify

from app import application
from calculator import calc_dispatcher


class IPCalc(View):
    init_every_request = False

    def __init__(self, template):
        self.template = template

    def dispatch_request(self):
        raw_request_string = request.args.get('network', '')
        if raw_request_string:
            context = calc_dispatcher(raw_request_string)
            application.logger.debug(f"{raw_request_string=}")
            application.logger.debug(f"{context=}")
        else:
            context = {}

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
