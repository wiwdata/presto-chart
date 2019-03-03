#!/usr/bin/env python3

import argparse
import glob
import os
import shutil
import subprocess
import textwrap
import typing
from uuid import uuid4

from jinja2 import Environment
from jinja2 import FileSystemLoader

# Environment-variables for directory locations set during docker build.
HOME_DIRECTORY = os.environ['PRESTO_HOME']
CONFIGS_DIRECTORY = os.environ['PRESTO_CONFIGS_DIR']
CATALOG_DIRECTORY = os.environ['PRESTO_CATALOG_DIR']
DATA_DIRECTORY = os.environ['PRESTO_DATA_DIR']
TEMPLATE_DIRECTORY = os.environ['TEMPLATE_DIR']
TEMPLATE_DEFAULT_DIRECTORY = os.environ['TEMPLATE_DEFAULT_DIR']
TEMPLATE_CUSTOM_DIRECTORY = os.environ['TEMPLATE_CUSTOM_DIR']
TEMPLATE_CATALOG_DIRECTORY = os.environ['TEMPLATE_CATALOG_DIR']

ENVIRONMENT = Environment(
    loader=FileSystemLoader(TEMPLATE_DIRECTORY)
)


def _explode(line: str) -> typing.Tuple[str, str]:
    """
    Explodes a properties config line into a key value pair
    and returns that as a tuple. Lines without values are
    returned with an empty string as the value.
    """
    parts = line.split('=', 1)
    key = parts[0].strip()
    value = parts[1].strip() if len(parts) > 1 else ''
    return key, value


def _get_custom_values(directory: str, filename: str) -> dict:
    """
    Loads the user-specified custom properties file and explodes it into a
    dictionary for merging with the default values stored in the container.
    """
    path = os.path.join(directory, filename)
    if not os.path.exists(path):
        return {}

    with open(path, 'r') as f:
        lines = f.read().strip().split('\n')

    return dict([_explode(line) for line in lines if line.strip()])


def render(
        template_name: str,
        output_directory: str,
        custom_directory: str = None,
        **kwargs
) -> str:
    """
    Renders a template configuration file with the given
    arguments if the file does not already exist. The file may
    exist if a ConfigMap has been used to override the template
    entirely.
    """
    filename = os.path.basename(template_name).replace('.jinja2', '')
    template = ENVIRONMENT.get_template(template_name)
    lines = template.render(**kwargs).strip().split('\n')

    # Create output by merging default and custom configuration
    # file contents such that custom values override the default
    # ones if they are specified.
    defaults = dict([_explode(line) for line in lines if line.strip()])
    custom = (
        _get_custom_values(custom_directory, filename)
        if custom_directory else
        {}
    )
    configs = list({**defaults, **custom}.items())
    configs.sort(key=lambda x: x[0])
    output = '\n'.join(['{}={}'.format(*c) for c in configs])

    path = os.path.join(output_directory, filename)
    with open(path, 'w') as f:
        f.write(output)
    os.chmod(path, 0o755)

    print('\n[RENDERED]: {}'.format(path))
    print(textwrap.indent(output, '  '))
    return path


def bootstrap(arguments: dict):
    """
    Executes pre-launch run-time configurations using the given arguments
    to modify the configuration process.
    """
    target_path = os.path.join(CONFIGS_DIRECTORY, 'jvm.config')
    path = os.path.join(TEMPLATE_CUSTOM_DIRECTORY, 'jvm.config')
    if not os.path.exists(path):
        path = os.path.join(TEMPLATE_DEFAULT_DIRECTORY, 'jvm.config')
    shutil.copy2(path, target_path)
    os.chmod(target_path, 0o755)
    print('\n[ADDED]: jvm.config from {}'.format(path))

    print('\n--- Bootstrapping Configuration Files ---')
    glob_path = os.path.join(TEMPLATE_DEFAULT_DIRECTORY, '*.properties.jinja2')
    for path in glob.iglob(glob_path):
        template_path = path.replace(TEMPLATE_DIRECTORY, '').strip('/')
        render(
            template_name=template_path,
            output_directory=CONFIGS_DIRECTORY,
            custom_directory=TEMPLATE_CUSTOM_DIRECTORY,
            **arguments
        )

    print('\n--- Boostrapping Catalog Files ---')
    glob_path = os.path.join(TEMPLATE_CATALOG_DIRECTORY, '*.properties')
    for path in glob.iglob(glob_path):
        template_path = path.replace(TEMPLATE_DIRECTORY, '').strip('/')
        render(
            template_name=template_path,
            output_directory=CATALOG_DIRECTORY,
            **arguments
        )


def launch(arguments: dict):
    """Starts the presto service running within the container."""
    conf_dir = CONFIGS_DIRECTORY
    print('\n[LAUNCH]: Starting Presto')
    cmd = [
        'launcher', 'run',
        '--node-config={}/node.properties'.format(conf_dir),
        '--jvm-config={}/jvm.config'.format(conf_dir),
        '--config={}/config.properties'.format(conf_dir),
        '--log-levels-file={}/log.properties'.format(conf_dir)
    ]

    print(textwrap.indent('\n'.join(cmd), '  '), '\n\n')
    if not arguments['dry_run']:
        subprocess.run(cmd)
    else:
        print('[DRY-RUN]: Skipped launch call\n\n')


def parse() -> dict:
    """
    Parses command line arguments and returns a dictionary of results that
    also includes specific environment variables that can be used.
    """
    default_node_id = os.environ.get('POD_NAME') or str(uuid4())
    parser = argparse.ArgumentParser()
    parser.add_argument('--coordinator', action='store_true')
    parser.add_argument('--node-id', default=default_node_id)
    parser.add_argument('--log-level', default='INFO')
    parser.add_argument('--environment', default='production')
    parser.add_argument('--discovery-uri', default='127.0.0.1')
    parser.add_argument('--discovery-port', default='80')
    parser.add_argument('--dry-run', action='store_true')

    # Include environment variables with specific prefixes so these can be
    # rendered into the template.
    envs = {
        k: str(v)
        for k, v in os.environ.items()
        if k.startswith(('PRESTO_', 'TEMPLATE_', 'SECRET_', 'USER_'))
    }
    return {**envs, **vars(parser.parse_args())}


def run():
    """Executes the launch process with bootstrapped configuration."""
    arguments = parse()
    print('\n\n============== SETTINGS ==============')
    print('\n'.join([
        '  * {k}: {v}'.format(k=k, v=v)
        for k, v in sorted(arguments.items(), key=lambda x: x[0])
    ]))

    print('\n\n============== BOOTSTRAPPING ==============')
    bootstrap(arguments)

    print('\n\n============== LAUNCHING ==============')
    launch(arguments)


if __name__ == '__main__':
    run()
