from base import *
import json
import os
import sys

add_result = {
    'assignedto_id': None,
    'comment': None,
    'custom_baseline_stdev': None,
    'custom_baseline_throughput': None,
    'custom_launchpad_bug': None,
    'custom_stdev': None,
    'custom_test_case_steps_results': [{
        'actual': '',
        'content': '',
        'expected': ''
    }],
    'custom_throughput': None,
    'defects': None,
    'elapsed': None,
    'status_id': None,
    'version': None
}

def get_title_exist_tests(exist_tests):
    tests = []
    for test in exist_tests:
        tests.append(test['custom_test_group']+'.'+test['title'])
    return tests

def get_tests_info(data, exist_tests, tests):
    test_cases = data['tests']
    t_test_case = []
    for test_case in test_cases:
        if test_case in exist_tests:
            #print test_cases[test_case]
            status = test_cases[test_case].get('status')
            test_id = _get_tests_id(test_case,tests)
            if status == 'success':
                t_test_case.append({'name': test_case,
                                    'status': status,
                                    'test_id' : test_id})
            elif status == 'fail' :
                t_test_case.append({'name': test_case, 'status': status,
                                    'traceback' : test_cases[test_case].get('traceback'),
                                    'test_id': test_id})
            elif status == 'skip' :
                t_test_case.append({'name': test_case, 'status': status,
                                    'reason': test_cases[test_case].get(
                                        'reason'),
                                    'test_id': test_id})

    return t_test_case

def _get_tests_id(test, tests):
    title = test.split('.')[-1]
    custom_test_group = '.'.join(test.split('.')[:-1])
    result = list(filter(lambda item:
                       item['title'] == title and
                       item['custom_test_group'] == custom_test_group, tests))
    return result[0]['id']

if __name__ == "__main__":
    path = 'report.json'#sys.argv[1]
    test_suite = '35042'#sys.argv[2]
    call = Base()
    tests = call.get_tests(test_suite)

    # print call.get_test_result(28877753)

   # path = 'tempest.api.identity.json'
    JSON_FILE = os.path.join(os.getcwd(), path)
    with open(JSON_FILE) as data_file:
        data = json.load(data_file)

    # import ipdb; ipdb.set_trace()
    exist_tests = get_title_exist_tests(tests)

    test_results = get_tests_info(data, exist_tests, tests)
    for result in test_results:
        # print result
        if call.get_test_result(result['test_id']) == []:
            if result.get('status') == 'fail':
                add_result_my = add_result
                add_result_my['status_id'] = 5
                add_result_my['comment'] = result['traceback']
                send_add_result = 'add_result/' + str(result['test_id'])
                # r = call.client.send_post(send_add_result, add_result)
                # print r
            elif result.get('status') == 'success':
                add_result_my = add_result
                add_result_my['status_id'] = 1
                add_result_my['comment'] = None
                # send_add_result = 'add_result/' + str(result['test_id'])
                # r = call.client.send_post(send_add_result, add_result)
                print r
            elif result.get('status') == 'skip' :
                add_result_my = add_result
                add_result_my['status_id'] = 6
                add_result_my['comment'] = result['reason']
                send_add_result = 'add_result/' + str(result['test_id'])
                # r = call.client.send_post(send_add_result, add_result)
                # print r