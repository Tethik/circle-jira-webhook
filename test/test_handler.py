import pytest
import os
import jira

import circlebot.jiraclient
from circlebot.handler import badge_markup, circle_webhook

def test_badge_markup():
  url = "https://circleci.com/gh/circleci/mongofinil/22"
  branch = "master"
  print(badge_markup(url, branch))

class MockFields:
  customfield_10050 = ""

class MockIssue(object):
  fields = MockFields()
  key = "TES-58"

  def update(self, *stuff, **morestuff):
    return True

class MockEmptyJira(object):
  def __init__(self, *args, **xargs):
    pass

  def issue(self, text):
    return None

class FakeContext(object):
  def get_remaining_time_in_millis(self):
    return 300000


class MockJira(MockEmptyJira):
  def issue(self, text):
    if text == "TES-58":
      return MockIssue()
    if text == "TES-12381":
      raise Exception("RUHROH OVERFLOW!")
    return None



def test_full_run(monkeypatch):
  # load test input
  with open(os.path.dirname(os.path.abspath(__file__)) + "/input.json") as jsonfile:
    event = {
      'body': jsonfile.read()
    }

  monkeypatch.setattr(circlebot.jiraclient, 'JIRA', MockJira)
  circle_webhook(event, FakeContext())

def test_run_without_hit(monkeypatch):
  # load test input
  with open(os.path.dirname(os.path.abspath(__file__)) + "/input.json") as jsonfile:
    event = {
      'body': jsonfile.read()
    }

  monkeypatch.setattr(circlebot.jiraclient, 'JIRA', MockEmptyJira)
  response = circle_webhook(event, FakeContext())
  assert "no issues found" in response["body"]



