import argparse
import re

import os
import requests
from lxml.html import fromstring

from config import JENKINS_AUTH, STAGING_STAT_RESULTS_URL, JOB_RESULTS_URL, \
    RESOURCES_DIR

TEST_SELECTOR_LINK = 'tr td:first-child a.model-link.inside'

TEST_REG_EXP = '^\|(?P<name>[a-zA-Z0-9_.]+)|<span .*?>' \
               '(?P<result>\d{1,3}:\d{1,3})</span>'
TEST_NAME_REG_EXP = r'^\|(?P<name>[a-zA-Z0-9_.]+)'
TEST_RESULT_EXP = r'<span .*?>(\d{1,3}:\d{1,3})</span>'

WARNING_LEVEL_LOW = 'low'
WARNING_LEVEL_NORMAL = 'warning'
WARNING_LEVEL_CRITICAL = 'danger'

WARNING_LEVELS = (WARNING_LEVEL_LOW,
                  WARNING_LEVEL_NORMAL,
                  WARNING_LEVEL_CRITICAL)

# This is using global variable only as "cache"
staging_aggregation_cache = None


class ResultsChecker(object):

    def __init__(self, job_name, is_testing=False):
        self.failed_tests = []
        self.job_name = job_name
        self.is_testing = is_testing
        self.error = ''
        self.run()

    def get_results_from_jenkins(self):
        """ Get info from jenkins pages
        :return {
                    'result' : (<staging_results>: str, <job_results>: str),
                    'error'  : <text of error>: str
                }
        """

        res = {'results': ('', ''), 'error': ''}
        auth = requests.auth.HTTPBasicAuth(*JENKINS_AUTH)

        try:
            staging_results = self._get_staging_results(auth)
            test_result = requests.get(
                JOB_RESULTS_URL.format(job_name=self.job_name), auth=auth
            ).text
        except (requests.RequestException, AttributeError) as e:
            res['error'] = '[{}] {}'.format(e.__class__.__name__, str(e))
        else:
            res['results'] = staging_results, test_result

        return res

    @staticmethod
    def _get_staging_results(auth):
        global staging_aggregation_cache
        if staging_aggregation_cache:
            return staging_aggregation_cache
        staging_results = requests.get(
            STAGING_STAT_RESULTS_URL, auth=auth
        ).text
        staging_aggregation_cache = staging_results
        return staging_results

    @staticmethod
    def get_results_from_files():
        with open(os.path.join(RESOURCES_DIR, 'test_staging_new_stat.html')) as f:
            staging_results = f.read()

        with open(os.path.join(RESOURCES_DIR, 'test_job_fails.html')) as f:
            test_result = f.read()
        return staging_results, test_result

    def get_results(self):
        if self.is_testing:
            return self.get_results_from_files()

        res = self.get_results_from_jenkins()
        self.error = res['error']
        return res['results']

    def run(self):
        """ Check job results and find match with jenkins tests fail

        :return: list of failed tests... for ex.:
            [{
                'name': '<test_name>',
                'href': '<relative_url>',
                'staging_result': '0:10',
                'warning_level': 'low|warning|danger',
            }, ...]
        """
        staging_result_tests = {}

        staging_results, job_results = self.get_results()

        if self.error:
            # print('Error detected: {}'.format(self.error))
            return

        # hot fix: crop duplicate of HTML tag definition
        if staging_results.count('<html>') > 1:
            dup_length = staging_results.index('</html>') + len('</html>')
            staging_results = staging_results[dup_length:]

        html_doc = fromstring(staging_results)
        for test_tr in html_doc.cssselect('.table tbody tr'):
            try:
                test_name = \
                    test_tr.cssselect('td')[0].cssselect('div > a')[0].text
                test_res = \
                    test_tr.cssselect('td')[2].text
            except IndexError:
                continue

            stat_result = re.findall('([0-9]+)\.*\d*', test_res)
            staging_result_tests[test_name] = {
                'fails': int(stat_result[0]),
                'total': int(stat_result[1])
            }

        html_doc = fromstring(job_results)
        tests_tables = html_doc.cssselect('table.pane')
        # TODO: find a better way to detect success build
        if len(tests_tables) == 1:
            return []  # 'No found failed tests'

        try:
            tests_table = tests_tables[0]
        except IndexError:
            self.error = 'Test table did not fond in Jenkins Job Results'
            return []

        for failed_test_item in tests_table.cssselect(TEST_SELECTOR_LINK):
            test_name = failed_test_item.text
            result_tests = staging_result_tests.get(test_name, {})
            try:
                fails_count = result_tests['fails']
            except KeyError:
                warning_level = WARNING_LEVEL_LOW
            else:
                warning_level = WARNING_LEVEL_CRITICAL \
                    if fails_count == 0 else WARNING_LEVEL_NORMAL

            self.failed_tests.append({
                'name': test_name,
                'href': failed_test_item.get('href'),
                'staging_result': result_tests,
                'warning_level': warning_level,
            })

        return self.failed_tests


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-j', '--job-name', dest='job_name', default=None,
                        required=True)
    parser.add_argument('-t', '--is_testing', action='store_true',
                        dest='is_testing', default=False)
    args = parser.parse_args()

    results_checker = ResultsChecker(job_name=args.job_name,
                                     is_testing=args.is_testing)
    if results_checker.failed_tests is None:
        exit(1)
    for test in results_checker.failed_tests:
        print('| {:<100}| {}'.format(test['name'], test['staging_result']))


