from base import *

if __name__ == "__main__":
    milestone_name = config.MILESTONE
    suite_name = config.SUITE
    call = Base()
    test_plan_name = config.PLAN_NAME

    if not call.is_test_plan_exist:
        description = 'Publish the results of Tempest tests in TestRail'
        entries = []
        milestone = call.get_milestone_by_name(milestone_name)

        test_plan = call.add_plan(test_plan_name,
                                  description=description,
                                  milestone_id=milestone['id'],
                                  entries=[]
                                  )

    test_plan = call.get_plan_by_name(test_plan_name)
    suite = call.get_suite_by_name(suite_name)
    test_run_name = milestone_name + ' ' + suite['name']
    entries = {'name': test_run_name,
               'suite_id': suite['id'],
               'include_all': True}
    run = call.add_plan_entry(test_plan['id'], entries)
    tests = call.get_tests(run['runs'][0]['id'])

    tests_status = call.get_result_by_name()
    results = call.prepare_common_results(tests, tests_status)
    add_results = 'add_results/' + str(run['runs'][0]['id'])
    call.client.send_post(add_results, results)



