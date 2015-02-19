from django.core import management

import argparse
import getpass
import os
import os.path
import stat
import shutil
import subprocess
import sys


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

# parser.add_argument(
#     "--noinput",
#     action="store_false",
#     default=True,
#     dest="interactive",
#     help="Tells Django to NOT prompt the user for input of any kind.",
# )


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
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def configure_apps(path, apps, project):

    # Check to make sure all app choices aren't False
    print 'Creating temporary folder...'
    temp_path = os.path.join(path, 'apps', 'temp')
    temp_folder = os.makedirs(temp_path)

    for app in apps:
        if apps[app]:
            try:
                app_folder = os.path.join(temp_path, app)

                git(
                    "clone",
                    "git@github.com:onespacemedia/cms-{}.git".format(app),
                    app_folder
                )

                for src_dir, dirs, files in os.walk(app_folder):
                    for d in dirs:
                        if d == 'apps':
                            shutil.move(
                                os.path.join(app_folder, d, app),
                                os.path.join(path, 'apps')
                            )
                        elif d == 'templates':
                            shutil.move(
                                os.path.join(app_folder, d, app),
                                os.path.join(path, 'templates')
                            )

            except Exception as e:
                print "Error: {}".format(e)

        else:
            f = open(os.path.join(path, 'settings', 'base.py'))
            lines = f.readlines()
            f.close()

            f = open(os.path.join(path, 'settings', 'base.py'), "w")
            for line in lines:
                if line.strip() != '"{}.apps.{}",'.format(project, app):
                    f.write(line)

            f.close()

    print 'Removing temporary folder...'
    shutil.rmtree(temp_path)

    print 'Remember to update each apps models.py with the correct urlconf'


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
        extensions=("py", "txt", "conf", "gitignore", "md", "css", "js"),
        user=getpass.getuser(),
        project_slug=args.project_name.replace("_", "-"),
    )
    apps = {
        'faqs': query_yes_no("Would you like the FAQs app?"),
        'jobs': query_yes_no("Would you like the Jobs app?"),
        'people': query_yes_no("Would you like the People app?")
    }
    # Make management scripts executable.
    make_executable(os.path.join(dest_dir, "manage.py"))
    configure_apps(os.path.abspath(os.path.join(dest_dir, args.project_name)), apps, args.project_name)
    # Give some help to the user.
    print('CMS project created.')

if __name__ == "__main__":
    main()
