from jira import JIRA
import re

class JiraClient(object):
    def __init__(self, auth, custom_field, key_format):
        self.custom_field = custom_field
        self.key_format = key_format
        self.jira = JIRA('https://massagio-it.atlassian.net', basic_auth=auth)

    def jira_issues_from_commit_text(self, commit_text):
        # look for regex
        unique = set()
        issues = []
        for match in re.finditer(self.key_format, commit_text):
            key = match.group(0)
            if key in unique:
                continue
            unique.add(key)
            try:
                issue = self.jira.issue(key)
                if issue:
                    issues.append(issue)
            except Exception as ex:
                print("Error for ", key, ex)
        return issues

    def attach_badge_to_jira_issue(self, issue, badge_url, markup):
        current_badges = getattr(issue.fields, self.custom_field) or ""

        # Attempt to not overwrite existing badges.
        if current_badges and badge_url in current_badges:
            print("%s badge already exists in issue" % issue.key)
            return

        issue.update(fields={self.custom_field: current_badges + " " + markup})
        print("%s was updated with circleci badge" % issue.key)
