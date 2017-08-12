import os
import unittest
import time
from datetime import timedelta

from flask import url_for, Flask
import flask_testing

from app import db
from app.models import JenkinsJob
from app.views import mod as main_module
from utils.results_check import ResultsChecker, WARNING_LEVELS


class TestResultsChecker(unittest.TestCase):
    def test_run(self):
        results_checker = ResultsChecker(job_name='test_job', is_testing=True)
        self.assertIsInstance(results_checker.failed_tests, list)
        for item in results_checker.failed_tests:
            self.assertIsInstance(item, dict)
            self.assertIn('staging_result', item)
            self.assertIn(item['warning_level'], WARNING_LEVELS)


class AppViewTests(flask_testing.TestCase):
    job_name = 'TestJob'

    def create_app(self):
        test_app = Flask(__name__, template_folder='app/templates')
        test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
        test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(test_app)
        test_app.register_blueprint(main_module)
        return test_app

    def setUp(self):
        db.create_all()
        db.session.add(JenkinsJob(self.job_name))
        db.session.commit()
        os.environ['FLASK_TESTING'] = 'True'

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        del(os.environ['FLASK_TESTING'])

    def get_url(self, endpoint, **url_kwargs):
        kwargs = url_kwargs or {}
        with self.app.app_context():
            url = url_for(endpoint, **kwargs)
        return url

    @property
    def redirect_url(self):
        return '{}#{}'.format(self.index_url, self.job_name)

    @property
    def index_url(self):
        return self.get_url('main.index')

    def test_index(self):
        response = self.client.get(self.index_url)
        self.assert200(response)

    def test_job_create(self):
        url = self.get_url('main.job_create')
        new_job_name = 'TestJob2'
        redirect_url = '{}#{}'.format(self.index_url, new_job_name)
        response = self.client.post(url, data={'name': new_job_name})
        self.assertRedirects(response, location=redirect_url)
        new_job_count = JenkinsJob.query.filter_by(name=new_job_name).count()
        self.assertEqual(new_job_count, 1, 'The job has not been created')

    def test_job_update(self):
        slp_sec = 1
        url = self.get_url('main.job_update', job_name=self.job_name)
        # we are sleeping to detect updated_at changes
        time.sleep(slp_sec)
        response = self.client.get(url)
        self.assertRedirects(response, location=self.redirect_url)
        updated_job = JenkinsJob.query.get(self.job_name)
        self.assertGreater(updated_job.updated_at,
                           updated_job.created_at + timedelta(seconds=slp_sec),
                           'The job has not been updated')
        self.assertIn('success', updated_job.update_message)

    def test_job_remove(self):
        url = self.get_url('main.job_remove', job_name=self.job_name)
        response = self.client.get(url)
        self.assertRedirects(response, location=self.index_url)
        job_counts = JenkinsJob.query.filter_by(name=self.job_name).count()
        self.assertEqual(job_counts, 0, 'The job has not been removed')


if __name__ == '__main__':
    unittest.main()
