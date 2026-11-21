# EECE 435L — Lab 10

**Joey Saade** · Jenkins CI/CD for a Python application

Repository: https://github.com/JS9872/435L_Lab10

## Submission contents

- `jenkins_project/Jenkinsfile_Joey_Saade`: the graded Jenkins pipeline.
- `jenkins_project/app.py` and `tests/test_app.py`: greeting and automated tests.
- `jenkins_project/deploy.py`: versioned local deployment and smoke test.
- `jenkins/job-config.xml`: importable **Python-CI-CD** job configuration.
- `jenkins/plugins.txt`: required Jenkins plugins.
- `report/`: report, screenshots, and evidence from the actual Jenkins build.
- `Submission.txt`: repository link for Moodle.

## Run locally

Python 3.12 is the verified version. From `jenkins_project`:

```powershell
python -m venv venv
./venv/Scripts/python.exe -m pip install -r requirements.txt
./venv/Scripts/python.exe -m flake8 app.py deploy.py tests
./venv/Scripts/python.exe -m pytest -v
./venv/Scripts/python.exe -m coverage run -m pytest -v
./venv/Scripts/python.exe -m coverage report
./venv/Scripts/python.exe -m bandit app.py deploy.py
./venv/Scripts/python.exe deploy.py --destination ../local-deployments --build-number manual-1 --commit local
```

On Linux, use `python3` to create the environment and `venv/bin/python`
for subsequent commands. Each deployment uses a new build identifier;
an existing release is never overwritten.

## Configure Jenkins

1. Run Jenkins with a supported Java runtime and ensure Python and Git are
   available on the build agent's PATH.
2. Install the plugins in `jenkins/plugins.txt`, including their dependencies.
   SSH Agent is installed to satisfy the lab prerequisites; deployment here
   uses the permitted local option and requires no SSH credentials.
3. Create a Pipeline job named **Python-CI-CD**. Select **Pipeline script from
   SCM**, Git, repository `https://github.com/JS9872/435L_Lab10.git`, branch
   `*/main`, and script path
   `jenkins_project/Jenkinsfile_Joey_Saade`. Alternatively, import the supplied
   `jenkins/job-config.xml` through Jenkins CLI `create-job`.
4. Choose **Build Now**. No webhook or public Jenkins endpoint is required.

The stages are **Setup → Lint → Test → Coverage → Security Scan → Deploy**.
The application must have 100% statement and branch coverage. Bandit scans
both application and deployment code, with no skipped rules or suppressed
findings. Failed stages prevent deployment. The job publishes JUnit results
and archives coverage, security, and deployment artifacts before cleaning
the workspace.

Deployment is retained outside the disposable workspace at
`JENKINS_HOME/deployments/Python-CI-CD/build-<number>/`. It contains the copied
`app.py` and a manifest recording the Git commit, SHA-256, greeting, and smoke
test result. This is a local file deployment of a CLI program; the assignment
does not require a web service or remote production server.

## This machine

The lab Jenkins instance listens only on `http://localhost:8080`.
Runtime files are outside this repository under
`%LOCALAPPDATA%\435L-Lab10`. The local administrator is `joey`; its generated
password is in the access-restricted `admin-password.txt` file there.
Anonymous access is read-only; changing configuration and triggering builds
requires login. No passwords, tokens, virtual environments, or Jenkins home
files are committed.

Use `jenkins/start-local.ps1` to restart this prepared instance if it is stopped.
The script assumes the runtime downloaded for this lab is present.
