#!/usr/bin/env python
#
#    Copyright 2017 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import sys

from base import *
from joblib import Parallel, delayed
import logging

logger = logging.getLogger(__package__)
# from fuelweb_test.testrail.settings import TestRailSettings
# from fuelweb_test.testrail.testrail_client import TestRailProject


DELETE_OLD_SECTIONS = False  # User should have proper permissions to do it


SECTIONS_MAP = {
#    "Ironic": ["baremetal."],
#    "Cinder": ["cinder."],
#    "CLI Clients": ["cli_clients."],
#    "Glance": ["glance."],
#    "Heat": ["heat."],
    "Horizon":["test_"],
#    "Keystone": ["keystone."],
#    "Neutron": ["neutron."],
#    "NFV": ["nfv."],
#    "Nova": ["nova."],
#    "Object Storage": ["object_storage."]
}

# Use test IDs for titles of TestRail test cases like
# 'tempest.api.identity.admin.v2.test_rolesRolesTestJSON.test_list_roles[id-
# 75d9593f-50b7-4fcf-bd64-e3fb4a278e23]' instead of test names.
USE_TEST_IDs = True

TEST_CASE_TYPE_ID = 1  # Automated
TEST_CASE_PRIORITY_ID = 4  # P0
QA_TEAM = 4  # MOS

UPLOAD_THREADS_COUNT = 4


LOG = logger


def choose_section_by_test_name(test_name):
    for section, key_words in SECTIONS_MAP.items():
        for key_word in key_words:
            if key_word in test_name:
                return section

    return "Other"


def get_tags_by_test_name(test_name):
    tags = []
    if test_name.find("[") > -1:
        tags = test_name.split("[")[1][:-1].split(",")

    return tags


def create_tr_test_cases(test_cases, milestone_id, type_id=1, priority_id=4,
                         qa_team=4):
    tr_test_cases = []

    for test_case_name in test_cases:
        if "id-" in test_case_name:
            section = choose_section_by_test_name(test_case_name)
            if section not in SECTIONS_MAP:
                SECTIONS_MAP[section] = []

            test_name = test_case_name

            report_label = test_name
	    """
            for tag in get_tags_by_test_name(test_name):
                if tag.startswith("id-"):
                    report_label = tag[3:]
                    break
	    """
            test_case = {
                "milestone_id": milestone_id,
                "section": section,
                "title": (( test_name) if USE_TEST_IDs
                          else test_name),
                "type_id": type_id,
                "priority_id": priority_id,
                "custom_qa_team": qa_team,
                "estimate": "1m",
                "refs": "",
                "custom_test_case_description": test_name,
                "custom_test_case_steps": [{"Run test": "passed"}],
                "custom_report_label": report_label
            }
            tr_test_cases.append(test_case)

    return tr_test_cases


def _add_tr_test_case(tr_client, suite_id, tr_test_case):
    for i in range(7):
        try:
            tr_client.add_case(suite_id, tr_test_case)
        except APIError:
            print "ERROR"
            logging.info("APIError")
        else:
            break



def main():
    call = Base()
    try:
        tests_file_path = sys.argv[1]
    except IndexError:
        raise Exception("Path to a tests file should be provided!")

    if os.path.exists(tests_file_path):
        LOG.info("Reading tests file '%s'..." % tests_file_path)
        with open(tests_file_path) as f:
            test_cases = [test for test in f.read().split("\n") if test]
            LOG.info("Tests file '%s' has been successfully read."
                     % tests_file_path)
    else:
        raise Exception("Tests file '%s' doesn't exist!" % tests_file_path)

    LOG.info("Initializing TestRail client...")
    # tr = TestRailProject(url=TestRailSettings.url,
    #                      user=TestRailSettings.user,
    #                      password=TestRailSettings.password,
    #                      project=TestRailSettings.project)
    LOG.info("TestRail client has been successfully initialized.")

    LOG.info("Getting milestone '%s'..." % config.MILESTONE)
    milestone = call.get_milestone_by_name(config.MILESTONE)
    LOG.info(milestone)
    LOG.info("Getting tests suite '%s'..." % config.SUITE)
    suite = call.get_suite_by_name(config.SUITE)
    if not suite:
        LOG.info("Tests suite '%s' not found. "
                 "Creating tests suite..." % config.SUITE)
        suite = call.add_suite(config.SUITE)
        LOG.info("Tests suite has benn successfully created.")
    LOG.info(suite)

    LOG.info("Creating test cases for TestRail...")
    tr_test_cases = create_tr_test_cases(test_cases, milestone["id"],
                                         type_id=TEST_CASE_TYPE_ID,
                                         priority_id=TEST_CASE_PRIORITY_ID,
                                         qa_team=QA_TEAM)
    LOG.info("Test cases have been successfully created.")

    if DELETE_OLD_SECTIONS:
        LOG.info("Deleting old sections...")
        old_sections = call.get_sections(suite["id"])
        for section in old_sections:
            if section["parent_id"] is None:
                call.delete_section(section["id"])
        LOG.info("Old sections have been successfully deleted.")

    sections_map = {}
    #import ipdb; ipdb.set_trace()
    for section in sorted(SECTIONS_MAP.keys()):
        LOG.info("Creating section '%s'..." % section)
        if (call.get_section_by_name(suite["id"],section)):
            s = call.get_section_by_name(suite["id"],section)
        else:
            s = call.add_section(suite["id"], section)
        LOG.info("Section '%s' has been successfully created." % section)
        sections_map[section] = s["id"]

    LOG.info("Uploading created test cases to TestRail...")

    # Parallel(n_jobs=UPLOAD_THREADS_COUNT)(
    #     delayed(_add_tr_test_case)(call, sections_map[t["section"]], t)
    #     for t in tr_test_cases)
    for t in tr_test_cases:
        _add_tr_test_case(call, sections_map[t["section"]], t)
    LOG.info("Test cases have been successfully uploaded.")


if __name__ == "__main__":
    main()
