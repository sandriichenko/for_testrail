from base import *




if __name__ == "__main__":
    call = Base()
    test_plan_id = call.get_plan_by_name(config.PLAN_NAME)['id']
    test_runs = call.get_test_runs(test_plan_id, config.SUITE)
    for run in test_runs:
        print run['name']