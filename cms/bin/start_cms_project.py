from django.core import management

import argparse
import getpass
import json
import os
import os.path
import stat
import shutil
import subprocess
import sys

EXTERNAL_APPS = {
    'faqs': 'FAQs',
    'jobs': 'jobs',
    'people': 'people',
}


class Output:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def info(self, string):
        print('[{}INFO{}] {}'.format(
            self.OKGREEN,
            self.ENDC,
            string,
        ))

    def warn(self, string):
        print('[{}WARN{}] {}'.format(
            self.WARNING,
            self.ENDC,
            string,
        ))


parser = argparse.ArgumentParser(
    description="Start a new CMS project.",
)

parser.add_argument(
    "project_name",
    help="The name of the project to create.",
)

parser.add_argument(
    "dest_dir",
    default=None,
    nargs="?",
    help="The destination dir for the created project.",
)

for app in EXTERNAL_APPS:
    parser.add_argument(
        '--with-' + app,
        action='store_true'
    )

    parser.add_argument(
        '--without-' + app,
        action='store_true'
    )

parser.add_argument(
    '--skip-frontend',
    action='store_true'
)


def git(*args):
    return subprocess.check_call(['git'] + list(args))


def make_executable(path):
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    # Fix Python 2.x.
    global input
    try:
        input = raw_input
    except NameError:
        pass

    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def configure_apps(path, apps, project):

    # Check to make sure all app choices aren't False
    temp_path = os.path.join(path, 'apps', 'temp')
    os.makedirs(temp_path)

    for app in apps:
        if apps[app]:
            try:
                app_folder = os.path.join(temp_path, app)

                git(
                    "clone",
                    "git://github.com/onespacemedia/cms-{}.git".format(app),
                    app_folder,
                    "-q"
                )

                for src_dir, dirs, files in os.walk(app_folder):
                    for d in dirs:
                        if d == 'apps':
                            shutil.move(
                                os.path.join(app_folder, d, app),
                                os.path.join(path, 'apps')
                            )

                            # Replace the {{ project_name }} placeholder.
                            with open(os.path.join(path, 'apps', app, 'models.py'), 'r') as f:
                                lines = f.readlines()

                            with open(os.path.join(path, 'apps', app, 'models.py'), 'w') as f:
                                for line in lines:
                                    line = line.replace('{{ project_name }}', project)
                                    f.write(line)

                        elif d == 'templates':
                            shutil.move(
                                os.path.join(app_folder, d, app),
                                os.path.join(path, 'templates')
                            )

                Output().info('Installed {} app'.format(app))

            except Exception as e:
                print("Error: {}".format(e))

        else:
            with open(os.path.join(path, 'settings', 'base.py')) as f:
                lines = f.readlines()

            with open(os.path.join(path, 'settings', 'base.py'), "w") as f:
                for line in lines:
                    # Don't write out lines for disabled applications.
                    if line.strip() != '"{}.apps.{}",'.format(project, app):
                        f.write(line)

    shutil.rmtree(temp_path)


def main():
    args = parser.parse_args()
    dest_dir = args.dest_dir or args.project_name
    # Create the project.
    try:
        os.makedirs(dest_dir)
    except OSError:
        pass
    management.call_command(
        "startproject",
        args.project_name,
        dest_dir,
        template=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "project_template")),
        extensions=["py", "txt", "conf", "gitignore", "md", "css", "js", 'json'],
        user=getpass.getuser(),
        project_slug=args.project_name.replace("_", "-"),
    )

    apps = {}

    for app in EXTERNAL_APPS:
        # Has the user specified if they want or don't want this app?
        if not getattr(args, 'with_' + app) and not getattr(args, 'without_' + app):
            apps[app] = query_yes_no("Would you like the {} module?".format(EXTERNAL_APPS[app]))
        else:
            if getattr(args, 'with_' + app) and getattr(args, 'without_' + app):
                print('You cannot use --with-{app} and --without-{app} together.'.format(
                    app=app,
                ))
                exit()

            if getattr(args, 'with_' + app):
                apps[app] = True

            if getattr(args, 'without_' + app):
                apps[app] = False

    # Make management scripts executable.
    make_executable(os.path.join(dest_dir, "manage.py"))
    path = os.path.abspath(os.path.join(dest_dir, args.project_name))
    configure_apps(path, apps, args.project_name)

    # If we don't have usertools, then we need to do a couple of things.
    try:
        from usertools.admin import UserAdmin
    except ImportError:
        # We don't have usertools, so remove the line from INSTALLED_APPS, and
        # add a template override for the admin.
        Output().warn('Usertools is not installed')

        with open(os.path.join(path, 'settings', 'base.py')) as f:
            lines = f.readlines()

        with open(os.path.join(path, 'settings', 'base.py'), "w") as f:
            for line in lines:
                # Don't write out lines for disabled applications.
                if line.strip() == '"usertools",':
                    f.write(line.replace('"usertools",', '# "usertools",'))
                else:
                    f.write(line)

        template_path = os.path.join(path, 'templates', 'admin', 'auth', 'user')
        os.makedirs(template_path)
        with open(os.path.join(template_path, 'change_list.html'), 'w') as f:
            f.write('{% extends "admin/change_list.html" %}')
            f.write('\n')

    # Create the server.json for the `server_management` tools.
    server_json = {
        "local": {
            "database": {
                "name": args.project_name
            }
        },
        "remote": {
            "server": {
                "ip": ""
            },
            "database": {
                "name": args.project_name,
                "user": args.project_name,
                "password": ""
            }
        },
        "opbeat": {
            "organization_id": "dde034beb33d4b77bb9937c39f0c158f",
            "app_id": "",
            "secret_token": ""
        }
    }

    with open(os.path.join(path, 'server.json'), 'w') as f:
        f.write(json.dumps(server_json, indent=4))

    # Run `npm` commands.
    if not getattr(args, 'skip_frontend'):
        with open(os.devnull, 'w') as f:
            Output().info("Installing bower, babel and gulp")
            subprocess.call(['npm', 'install', '-g', 'bower', 'gulp', 'babel'], stdout=f, stderr=subprocess.STDOUT)

            Output().info("Installing npm dependancies")
            subprocess.call(['npm', 'install'], stdout=f, stderr=subprocess.STDOUT)

            Output().info("Running gulp")
            subprocess.call(['gulp', 'styles'], stdout=f, stderr=subprocess.STDOUT)

    # Give some help to the user.
    Output().info('CMS project created')

if __name__ == "__main__":  # pragma: no cover
    main()
