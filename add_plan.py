from base import *
from datetime import datetime
import sys

if __name__ == "__main__":
    milestone_name = sys.argv[1]
    call = Base()
    now = str(datetime.now()).split()[0]
    test_plan_name = '-'.join(['ironic_underlay',now])
    description = 'Publish the results of Tempest tests in TestRail'
    entries = []
    milestone = call.get_milestone_by_name(milestone_name)

    test_plan = call.add_plan(test_plan_name,
                                 description=description,
                                 milestone_id=milestone['id'],
                                 entries=[]
                                 )