from app import app
from flask.views import View
from flask import request, render_template, redirect


from ipcalc import calc_dispatcher

# @app.route('/test')
# def index():
#     return render_template("index.html.del")


class IPCalc(View):
    init_every_request = False

    def __init__(self, template):
        self.template = template

    def dispatch_request(self):
        raw_request_string = request.args.get('network', '')
        if raw_request_string:
            app.logger.info(f"{raw_request_string=}")
            context = calc_dispatcher(raw_request_string)
        else:
            context = {}

        return render_template(self.template, **context)


class BaseView(View):
    init_every_request = False

    def __init__(self, template):
        self.template = template

    def dispatch_request(self):
        return render_template(self.template)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_template/404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('error_template/500.html'), 500


app.add_url_rule("/", view_func=IPCalc.as_view("ipcalc", "index.html"),)
app.add_url_rule("/faq", view_func=BaseView.as_view("faq", "faq.html"),)
app.add_url_rule("/about", view_func=BaseView.as_view("about", "about.html"),)
app.add_url_rule("/error", view_func=BaseView.as_view("error", "error_template/calc_error.html"),)
