from flask import render_template, url_for, redirect, request, Blueprint
from app.main.forms import ContactForm
from flask_mail import Message
from app import app, log, mail, ACCESS
from app.utils import requires_access_level

main = Blueprint('main', __name__)


@main.route("/", methods=['GET'])
def index():
    return redirect(url_for('main.about'))


@main.route("/about", methods=['GET', 'POST'])
def about():
    return render_template("about.html")


@main.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate() is False:
            flash('All fields are required', 'danger')
            return render_template('contact.html', form=form)
        else:
            msg = Message(form.subject.data, sender="lwtpoodles150@gmail.com", recipients=[
                'lwtpoodles150@gmail.com'])
            msg.body = """
                       From: %s %s <%s>
                       %s
                       """ % (form.firstname.data, form.lastname.data, form.email.data, form.message.data)
            log.info("Sending message from {first} {last} to lwtpoodles150@gmail.com".format(
                first=form.firstname.data, last=form.lastname.data))
            mail.send(msg)
            return 'Form sent.'
    elif request.method == 'GET':
        return render_template("contact.html", form=form)
