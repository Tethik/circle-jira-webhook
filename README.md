# Circle Jira Webhook
Webhook for automatically updating JIRA issues with CircleCI build status.

<!-- CircleCI posts a json containing this to our url:
```
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
```

We take said payload, then try to match against the env supplied JIRA_KEY_FORMAT regex to find references to a
JIRA issue. When it finds something that looks like it, it attempts to look up that key in JIRA and then puts
the CircleCI badge on the issue. If the issue already has that CircleCI badge for that specific branch, it will
be ignored. An issue can have more than one branch build badge attached to it. -->

To invoke this functionality when working on a JIRA issue, simply tag your branch at some point in a commit by putting `TES-<id>`
in the commit message.

# Setup serverless
```
yarn install
```

You may have to fix your aws login with permissions too.

## Running / Testing locally
Set up virtualenv with
```
pipenv install --dev
```

Activate the virtualenv.
```
pipenv shell
```

Inside the new shell, run tests with coverage:
```
py.test --cov=circlebot
```

## Deploying
```bash
pipenv shell # if not already activated
nvm use v8
pip freeze > requirements.txt # workaround to lock dependencies if you changed any
serverless deploy
```

## Check logs
```
serverless logs -f circle
```
