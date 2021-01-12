#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a list of available dot com domains from a TXT file with words.

Author: Martin Stefanik
"""

import sys
import json
import time
from math import ceil
from datetime import timedelta
import requests


def get_credentials():
    try:
        with open('.credentials.json', 'r') as f:
            data = json.load(f)
            key = data['key']
            secret = data['secret']
    except FileNotFoundError:
        print(
            "Error: Couldn't locate '.credentials.json' with API credentials "
            "for 'godaddy.com'."
        )
        sys.exit(1)
    except PermissionError:
        print("Error: No read permission for '.credentials.json'.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Formatting issues in '.credentials.json' detected.")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: The key {e} isn't present in '.credentials.json'.")
        sys.exit(1)
    except Exception:
        print(f"Error: Failed to get credentials from '.credentials.json'.")
        sys.exit(1)

    return (key, secret)


def get_words_from_file(file_name):
    try:
        with open(file_name, 'r') as f:
            words = f.read().splitlines()
            words = [w.lower() for w in words]
    except FileNotFoundError:
        print(f"Error: File '{file_name}' doesn't exist.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: No read permission for '{file_name}'.")
        sys.exit(1)
    except Exception:
        print(f"Error: Couldn't process '{file_name}'.")
        sys.exit(1)

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
        print("Error: No internet connection.")
        sys.exit(1)
    except Exception as e:
        print(f"Warning: Couldn't check '{word}.{tld}':\n{e}\nSkipping.")

    return resp


def main():
    key, secret = get_credentials()
    words = get_words_from_file('words.txt')
    for word in words:
        info = get_domain_info(key, secret, word)
        if info['available']:
            print(f"{info['domain']}: {info['currency']} {info['price']:.2f}")
        else:
            print(f"{info['domain']} not available.")


if __name__ == '__main__':
    main()
