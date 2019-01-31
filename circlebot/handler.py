"""
Webhook for automatically updating JIRA issues with CircleCI build status.

CircleCI posts a json containing this to our url:
{
    "payload": {
        "vcs_url" : "https://github.com/circleci/mongofinil",
        "build_url" : "https://circleci.com/gh/circleci/mongofinil/22",
        "build_num" : 22,
        "branch" : "master",
        "vcs_revision" : "1d231626ba1d2838e599c5c598d28e2306ad4e48",
        "status" : "failed", // :retried, :canceled, :infrastructure_fail, :timedout, :not_run, :running, :failed, :queued, :scheduled, :not_running, :no_tests, :fixed, :success
        "subject" : "Git commit header",
        "body" : "Git commit body",
        ...
    }
}

We take said payload, then try to match against the env supplied JIRA_KEY_FORMAT regex to find references to a
JIRA issue. When it finds something that looks like it, it attempts to look up that key in JIRA and then puts
the CircleCI badge on the issue. If the issue already has that CircleCI badge for that specific branch, it will
be ignored. An issue can have more than one branch build badge attached to it.

To invoke this functionality when working on a JIRA issue, simply tag your branch at some point in a commit by putting "TES-<id>"
in the commit message somewhere.
"""

import sys
import logging
import os
from collections import defaultdict
import json

from circlebot.jiraclient import JiraClient
from requests import Session
from raven import Client # Offical `raven` module
from raven_python_lambda import RavenLambdaWrapper


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers = []
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"))
logger.addHandler(handler)


CIRCLE_TOKEN = os.environ['CIRCLE_TOKEN']
JIRA_AUTH = (os.environ['JIRA_USER'], os.environ['JIRA_PASSWORD'])
JIRA_CIRCLECI_CUSTOM_FIELD = os.environ['JIRA_CIRCLECI_CUSTOM_FIELD']
JIRA_KEY_FORMAT = os.environ['JIRA_KEY_FORMAT']


def make_response(message):
    body = {
        "message": message
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def badge_markup(url, branch):
    branch = branch.replace("/", "%2F").strip()
    parts = url.split('/')
    base_url = '/'.join(parts[:-1])
    branch_build_url = "{}/tree/{}".format(base_url, branch)
    badge_url = "{}.png?circle_token={}".format(branch_build_url, CIRCLE_TOKEN)
    markup = "[!{badge_url}!|{branch_build_url}]".format(
        badge_url=badge_url, branch_build_url=branch_build_url)
    return badge_url, markup


@RavenLambdaWrapper()
def circle_webhook(event, _):
    body = json.loads(event['body'])
    build_url = body['payload']['build_url']
    commit_text = body['payload']['subject'] + "\n" + body['payload']['body']
    branch = body['payload']['branch']
    print("# Start hook for {}".format(build_url))
    print("# Got commit text: \n{}\n".format(commit_text))

    jira_client = JiraClient(
        JIRA_AUTH, JIRA_CIRCLECI_CUSTOM_FIELD, JIRA_KEY_FORMAT)

    issues = jira_client.jira_issues_from_commit_text(commit_text)

    if len(issues) < 1:
        print("# No issues found in commit")
        return make_response("no issues found")

    badge_url, markup = badge_markup(build_url, branch)

    for issue in issues:
        jira_client.attach_badge_to_jira_issue(issue, badge_url, markup)

    return make_response("updated {} issue{}".format(len(issues), "s" if len(issues) > 1 else ""))
