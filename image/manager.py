import argparse
import os
import subprocess

import requests

IMAGE = 'wiwdata/presto'
VERSION_URL = 'https://api.github.com/repos/prestodb/presto/tags'


def build(version: str):
    """Build image"""
    return subprocess.run([
        'docker', 'build',
        '--tag', f'{IMAGE}:{version}',
        '--build-arg', 'PRESTO_VERSION={}'.format(version),
        os.path.realpath(os.path.dirname(__file__))
    ])


def run(version: str):
    """Run container with bash shell."""
    return subprocess.run([
        'docker', 'run',
        '--rm', '-it',
        f'{IMAGE}:{version}',
        '/bin/bash'
    ])


def push(version: str):
    """Push image to docker hub."""
    return subprocess.run(['docker', 'push', f'{IMAGE}:{version}'])


def main():
    """Manages the presto image."""
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['build', 'run', 'push', 'version'])
    parser.add_argument('--version')
    args = parser.parse_args()

    version = args.version
    if version is None:
        version = requests.get(VERSION_URL).json()[0]['name']

    if args.action == 'version':
        print(f'Presto Version {version}')
        return

    actions = {'build': build, 'run': run, 'push': push}
    actions[args.action](version)


if __name__ == '__main__':
    main()
