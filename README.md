# README #

Application for finding of differences in the tests between Jenkins job and control branch (staging). Data for the control branch is taken from the aggregated set of passing tests on the staging

### How do I get set up and run it? ###
```bash
git clone [repository_url]
cd jenkins_job_results
python3 -m venv venv
pip install -r requiriments.txt
cp config_local.py.template config_local.py
nano config_local.py # modify needed variables

# run tests
venv/bin/python tests.py

# run application
venv/bin/python run.py
```

### Run as user service

```bash

# change paths to project
nano <path_to_project>/resourses/jenkins_job.service

# copy config to sysremd
mkdir ~/.config/systemd/user/
cp <path_to_project>/resourses/jenkins_job.service ~/.config/systemd/user/
cd ~/.config/systemd/user/
chmod 754 . 

# reload config
systemctl --user daemon-reload

# setup new service and enable him
systemctl --user enable jenkins_job.service

# run new service
systemctl --user start jenkins_job.service

# check state
systemctl --user status jenkins_job.service

# need reload
systemctl --user restart jenkins_job.service

```

### Manage project ###

* manage shell 
```bash
venv/bin/manage.py shell
```
* db migrations
```bash
venv/bin/python manage.py db migrate 
venv/bin/python manage.py db upgrade
venv/bin/python manage.py db downgrade
```
