from testrail import *

class Base():

    def __init__(self):
        self.client = APIClient('https://mirantis.testrail.com')
        self.client.user = ''
        self.client.password = ''
        self.project = self._get_project('Mirantis Cloud Platform')

    def _get_project(self, project_name):
        projects_uri = 'get_projects'
        projects = self.client.send_get(uri=projects_uri)
        for project in projects:
            if project['name'] == project_name:
                return project
        return None

    def send_post_add_result (self, id, bug, status_id, add_result):
        add_result['status_id'] = status_id
        add_result['custom_launchpad_bug'] = bug
        send_add_result = 'add_result/' + str(id)
        return self.client.send_post(send_add_result, add_result)

    def get_plans(self, project_id):#!
        return self.client.send_get('get_plans/{0}'.format(project_id))

    def get_plan(self, plan_id):#!
        return self.client.send_get('get_plan/{0}'.format(plan_id))

    def get_tests(self, plan_id):#!
        return self.client.send_get('get_tests/{0}'.format(plan_id))

    def get_tempest_runs(self, plan_id):
        all_run = self.get_plan(plan_id)#!get_plans
        tempest_runs = []
        for run in all_run['entries']:
            if 'Tempest' in run['name']:
                tempest_runs.append(run)
        return tempest_runs

    def get_id_of_tempest_runs(self, tempest_runs):
        tempest_runs_ids = {}#[]
        for i in tempest_runs:
            for item in i['runs']:
                tempest_runs_ids.update({item['id']:item['name']})
        return tempest_runs_ids

    def get_id_of_failed_tests(self, tempest_run_id):#!
        all_tests = self.get_tests(tempest_run_id)
        test_ids = []
        for test in all_tests:
            if test['status_id'] == 5:
                test_ids.append(test['id'])
        return test_ids

    def get_test_result(self, test_id):
        return self.client.send_get('get_results/{0}'.format(test_id))

    def get_test_results_for_run(self, run_id):
        return self.client.send_get('get_results_for_run/{0}'.format(run_id))

    def get_results_for_case(self, run_id, case_id):
        return self.client.send_get('get_results_for_case/{0}/{1}'.
                                    format(run_id, case_id))

    def get_test(self, test_id):
        return self.client.send_get('get_test/{0}'.format(test_id))

    def get_runs(self, run_id):
        return self.client.send_get('get_runs/{0}'.format(run_id))

    def get_run(self, run_id):
        return self.client.send_get('get_run/{0}'.format(run_id))

    def get_milestones(self):
        milestones_uri = 'get_milestones/{project_id}'.format(
            project_id=self.project['id'])
        return self.client.send_get(uri=milestones_uri)

    def get_milestone(self, milestone_id):
        milestone_uri = 'get_milestone/{milestone_id}'.format(
            milestone_id=milestone_id)
        return self.client.send_get(uri=milestone_uri)

    def get_milestone_by_name(self, name):
        for milestone in self.get_milestones():
            if milestone['name'] == name:
                return self.get_milestone(milestone_id=milestone['id'])

    def add_plan(self, name, description, milestone_id, entries):
        add_plan_uri = 'add_plan/{project_id}'.format(
            project_id=self.project['id'])
        new_plan = {
            'name': name,
            'description': description,
            'milestone_id': milestone_id,
            'entries': entries  # entries=[]
        }
        return self.client.send_post(add_plan_uri, new_plan)

    def get_last_tempest_run(self, get_plans):
        for plans in get_plans:
            # print dict
            if (plans.get(u'passed_count') > 1000 or plans.get(
                    u'blocked_count') > 1000 )and '9.1' in plans.get(u'name'):
                return plans.get(u'id')

    def add_result(self,test_id , result_to_add):
        return self.client.send_post('add_result/{0}'.format(test_id['id']),
                                     result_to_add)

    def get_plan_with_tempest(self):#!
        get_plans = self.get_plans(3)
        for plans in get_plans:
            if plans.get(u'passed_count') > 1000:
                get_plan = self.get_plan(str(plans.get(u'id')))

