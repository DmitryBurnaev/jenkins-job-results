from datetime import datetime

from flask import json

from app import db
from utils import human_datetime
from utils.results_check import ResultsChecker


class JenkinsJob(db.Model):
    __tablename__ = 'jenkins_job'

    name = db.Column(db.String(256), primary_key=True)
    created_at = db.Column(db.DateTime(), default=datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.now())
    update_message = db.Column(db.Text(), nullable=True)
    failed_tests = db.Column(db.Text(), nullable=True)

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {
            'name': self.name,
            'created_at': human_datetime(self.created_at),
            'updated_at': human_datetime(self.updated_at),
            'update_message': self.update_message or '',
            'failed_tests':
                json.loads(self.failed_tests) if self.failed_tests else {}
        }

    def update_test_results(self, is_testing=False):
        now_time = datetime.now()
        results_checker = ResultsChecker(job_name=self.name,
                                         is_testing=is_testing)

        if results_checker.error:
            self.update_message = 'Update fail ({}): {}'.format(
                human_datetime(now_time),
                results_checker.error
            )
            return False

        self.update_message = \
            'Update success ({})'.format(human_datetime(now_time))
        self.failed_tests = json.dumps(results_checker.failed_tests)
        self.updated_at = now_time

        return True

    def __repr__(self):
        return '<JenkinsJobBuild %r>' % self.name


if __name__ == '__main__':
    need_create_db = input('Create db? y/n: ')
    if need_create_db == 'y':
        db.create_all()
        print('Created')
