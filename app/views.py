import os
from flask import request, redirect, Blueprint, url_for, flash
from flask import render_template
from sqlalchemy import desc

from config import JENKINS_URL
from app import db, app as my_app
from app.forms import JenkinsJobForm
from app.models import JenkinsJob


mod = Blueprint('main', __name__, url_prefix='/')


flash_messages = []


def store_message(message, category):
    flash_messages.append({'message': message, 'category': category})


def read_messages():
    while flash_messages:
        msg = flash_messages.pop(0)
        flash(msg['message'], msg['category'])


@mod.route('')
def index():
    job_items = JenkinsJob.query.order_by(desc('updated_at')).all()
    context = {
        'job_items': [job_item.to_dict() for job_item in job_items],
        'form': JenkinsJobForm(),
        'JENKINS_URL': JENKINS_URL
    }
    read_messages()
    return render_template('index.html', **context)


@mod.route('jobs/create/', methods=['POST'])
def job_create():
    """ Create item and update him from jenkins-staging results """

    form = JenkinsJobForm(request.form)
    if not request.method == 'POST' or not form.validate():
        store_message('Form data is invalid: {}'.format(form.errors),
                      category='danger')
        return redirect(url_for('main.index'))

    # TODO: use form validation
    job_name = form.name.data
    if JenkinsJob.query.filter_by(name=job_name).count() > 0:
        store_message(
            'JenkinsJob with name {} already exists'.format(job_name),
            category='warning'
        )
        return redirect(url_for('main.index', _anchor=job_name))

    new_job = JenkinsJob(name=form.name.data)
    new_job.update_test_results()
    db.session.add(new_job)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    store_message('JenkinsJob item successfully created', category='success')
    return redirect(url_for('main.index', _anchor=new_job.name))


@mod.route('jobs/<string:job_name>/update/')
def job_update(job_name):
    job_item = JenkinsJob.query.filter_by(name=job_name).first_or_404()
    is_testing = os.environ.get('FLASK_TESTING', False)
    if job_item.update_test_results(is_testing=is_testing):
        store_message(job_item.update_message, category='info')

    db.session.commit()
    return redirect(url_for('main.index', _anchor=job_item.name))


@mod.route('jobs/<string:job_name>/remove/')
def job_remove(job_name):
    job_item = JenkinsJob.query.filter_by(name=job_name).first_or_404()
    db.session.delete(job_item)
    db.session.commit()
    store_message('JenkinsJob item successfully deleted', category='success')
    return redirect(url_for('main.index'))
