#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a list of available dot com domains from a TXT file with words.

Author: Martin Stefanik
"""

import os
import sys
import json
import time
from math import ceil
from datetime import timedelta
import requests
from progress.bar import IncrementalBar
import click


@click.command()
@click.argument(
    'filename',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    nargs=1
)
@click.option(
    '-o', '--output-file',
    default='available.txt',
    show_default=True,
    type=click.Path(exists=False, dir_okay=False, writable=True),
    help='Name of the output file in which available domains are to be stored.'
)
@click.version_option(
    version='1.0.0',
    message='%(version)s'
)
def check_availability(filename, output_file):
    key, secret = get_credentials()
    words = get_words_from_file(filename)
    available = []
    bar = IncrementalBar(
        'Progress', max=len(words),
        suffix='%(index)d / %(max)d || Elapsed time: %(elapsed_td)s'
    )
    what_to_do = 0
    if os.path.exists(output_file):
        what_to_do = click.prompt(
            text=f'\n{output_file} already exists. How to proceed?\n',
            type=click.Choice(('1', '2', '3')), default=1, show_choices=False,
            show_default=False, prompt_suffix=' 1 - Abort\n'
            f' 2 - Overwrite existing {output_file}\n'
            f' 3 - Append to existing {output_file}\n'
            'Choice: '
        )
        what_to_do = int(what_to_do)
        if what_to_do == 1:
            raise click.Abort()
    try:
        for word in words:
            d = get_domain_info(key, secret, word)
            bar.next()
            if d['available']:
                text = f"{d['domain']} : {d['currency']} {d['price']:.2f}"
                available.append(text)
        mode = 'w' if what_to_do == 2 else 'a'
        with open(output_file, mode) as f:
            f.write('\n'.join(available))
    except KeyboardInterrupt:
        bar.finish()
        raise click.Abort('Interrupted.')
    else:
        bar.finish()


def get_credentials():
    creds = '.credentials.json'
    try:
        with open(creds, 'r') as f:
            data = json.load(f)
            key = data['key']
            secret = data['secret']
    except FileNotFoundError:
        raise click.FileError(creds, hint='file does not exist')
    except PermissionError:
        raise click.FileError(creds, hint='file is not readable')
    except json.JSONDecodeError:
        raise click.FileError(creds, hint='JSON formatting issues found')
    except KeyError as e:
        raise click.FileError(creds, hint=f"key '{e}' not present")
    except Exception:
        raise click.FileError(creds)

    return (key, secret)


def get_words_from_file(file_name):
    try:
        with open(file_name, 'r') as f:
            words = f.read().splitlines()
            words = [w.lower() for w in words]
    except Exception:
        raise click.FileError(file_name)

    return words


def get_domain_info(key, secret, word, tld='com'):
    if tld.startswith('.'):
        tld = tld[1:]
    url = f'https://api.godaddy.com/v1/domains/available?domain={word}.{tld}'
    headers = {'Authorization': f'sso-key {key}:{secret}'}
    try:
        resp = requests.get(url, headers=headers)
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
    except Exception as e:
        click.echo(
            f"Warning: Couldn't check '{word}.{tld}':\n{e}\nSkipping."
        )

    return resp


if __name__ == '__main__':
    check_availability()  # pylint: disable=no-value-for-parameter
