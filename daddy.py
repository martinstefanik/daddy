#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021 Martin Stefanik
"""

import os
import json
import time
import requests
import click


VERSION = '1.0.0'


@click.command()
@click.argument(
    'filename',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    nargs=1
)
@click.option(
    '-o', '--output-file',
    type=click.Path(exists=False, dir_okay=False, writable=True),
    default='available.txt',
    show_default=True,
    help='Name of the output TXT file in which to store available domain names.'
)
@click.option(
    '-k', '--key',
    type=click.STRING,
    help='API key for godaddy.com.'
)
@click.option(
    '-s', '--secret',
    type=click.STRING,
    help='API secret for godaddy.com.'
)
@click.option(
    '-t', '--tld',
    type=click.STRING,
    default='com',
    show_default=True,
    help="Top level domain (e.g. 'com')."
)
@click.version_option(
    version=VERSION,
    message='%(version)s'
)
def daddy(filename, output_file, key, secret, tld):
    """
    Check availability of domains listed in FILENAME at godaddy.com.
    """
    # Obtain API credentials
    if key is None and secret is None:
        key, secret = get_credentials()
    elif key is None and secret is not None:
        raise click.ClickException('-k / --key option not specified.')
    elif key is not None and secret is None:
        raise click.ClickException('-s / --secret option not specified.')

    words = read_words_from_file(filename)
    available = []  # placeholder for available domains and their price

    # Prompt the user for what to do if `output_file` exists
    if os.path.exists(output_file):
        what_to_do = click.prompt(
            text=f'Warning: {output_file} already exists. How to proceed?\n',
            type=click.Choice(('1', '2', '3')), default=1, show_choices=False,
            show_default=False, prompt_suffix=' 1 - Abort\n'
            f' 2 - Overwrite existing {output_file}\n'
            f' 3 - Append to existing {output_file}\n'
            'Choice: '
        )
        what_to_do = int(what_to_do)
        if what_to_do == 1:
            raise click.Abort()
    else:
        what_to_do = 0  # zero indicates no file conflicts
    try:
        with click.progressbar(words, label='Progress:') as words:
            for word in words:
                d = get_domain_info(key, secret, word, tld)
                if d['available']:
                    text = f"{d['domain']} : {d['currency']} {d['price']:.2f}"
                    available.append(text)
        if not available:  # do not create the output file if not needed
            click.echo(f"There are no available domain names in {filename}.")
        else:
            mode = 'w' if what_to_do == 2 else 'a'
            with open(output_file, mode) as f:
                f.write('\n'.join(available))
    except KeyboardInterrupt:
        raise click.Abort('Interrupted.')


def get_credentials():
    """
    Get godaddy.com API credentials from the config file.
    """
    config = os.path.join(click.get_app_dir('daddy'), 'config')
    try:
        with open(config, 'r') as f:
            data = json.load(f)
            key = data['key']
            secret = data['secret']
    except FileNotFoundError:
        raise click.FileError(
            config, hint="File does not exist and '-k' and '-s' option not"
            "supplied."
        )
    except PermissionError:
        raise click.FileError(config, hint='File is not readable.')
    except json.JSONDecodeError:
        raise click.FileError(config, hint='JSON formatting issues found.')
    except KeyError as e:
        raise click.FileError(config, hint=f"Key '{e}' not present.")
    except Exception:
        raise click.FileError(config)

    return (key, secret)


def read_words_from_file(file_name):
    """
    Load the domain names from `file_name` into a list.
    """
    try:
        with open(file_name, 'r') as f:
            words = f.read().splitlines()
            words = [w.lower() for w in words]
    except Exception:
        raise click.FileError(file_name)

    return words


def get_domain_info(key, secret, word, tld):
    """
    Get a response dictionary for a given domain name.
    """
    if tld.startswith('.'):
        tld = tld[1:]
    url = f'https://api.godaddy.com/v1/domains/available?domain={word}.{tld}'
    headers = {'Authorization': f'sso-key {key}:{secret}'}
    try:
        resp = requests.get(url, headers=headers)

        # Handle godaddy.com API limit
        if (wait := json.loads(resp.content).get('retryAfterSec')) is not None:
            time.sleep(wait)
            resp = requests.get(url, headers=headers)

        resp.raise_for_status()
        resp = resp.json()
        resp['price'] = resp['price'] / (10 ** 6)
    except KeyError:
        pass
    except requests.exceptions.ConnectionError:
        raise click.ClickException("No internet connection.")
    except requests.exceptions.Timeout:
        raise click.ClickException("Connection timed out.")
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 401:
            raise click.ClickException('Invalid API key or secret.')
        elif err.response.status_code == 422:
            raise click.ClickException(
                f"TLD '{tld}' unavailable at godaddy.com."
            )
        else:
            raise click.ClickException(err)
    except Exception as err:
        click.echo(f"Warning: Could not check '{word}.{tld}':\n{err}")

    return resp


if __name__ == '__main__':
    daddy()  # pylint: disable=no-value-for-parameter
