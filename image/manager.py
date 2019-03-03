import argparse
import os
import subprocess

IMAGE = 'wiwdata/presto'
TAG = '0.217'


def build():
    """Build image"""
    return subprocess.run([
        'docker', 'build',
        '--tag', f'{IMAGE}:{TAG}',
        '--build-arg', 'PRESTO_VERSION={}'.format(TAG),
        os.path.realpath(os.path.dirname(__file__))
    ])


def run():
    """Run container with bash shell."""
    return subprocess.run([
        'docker', 'run',
        '--rm', '-it',
        f'{IMAGE}:{TAG}',
        '/bin/bash'
    ])


def push():
    """Push image to docker hub."""
    return subprocess.run(['docker', 'push', f'{IMAGE}:{TAG}'])


def main():
    """Manages the presto image."""
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['build', 'run', 'push'])
    args = parser.parse_args()

    actions = {'build': build, 'run': run, 'push': push}
    actions[args.action]()


if __name__ == '__main__':
    main()
