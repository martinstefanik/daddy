# Daddy

Command line tool for bulk checking availability of domain names at [godaddy.com](https://www.godaddy.com). Given a TXT file with one domain name per line, the script outputs into another TXT file a list of those domains that are available for purchase as well as their price. Domain names that are not valid domain names (e.g. words that end with a dash) are skipped. `daddy` is useful for instance to avoid the frustration with spending a long time on figuring out a good name for a startup, only to find that no reasonable domain for this startup is available.

The tool has only been tested on Linux, but should work on Windows and Mac as well.

# Installation and removal

The tool can be installed manually using `pip` by downloading/cloning the repo and by running

```
pip install --user .
```

inside the directory. The directory can be removed after the installation is complete.

Alternatively, if `git` is installed on the system, `daddy` can also be installed by running

```
pip install --user git+https://github.com/martinstefanik/daddy
```

In order to remove `daddy`, simply run

```
pip uninstall daddy
```

# Usage

Since `daddy` builds on the [godaddy.com](https://www.godaddy.com) API, it requires the user to create an account as well as an API endpoint. The API endpoint can be created [here](https://developer.godaddy.com/keys). Make sure to create a *production* endpoint. The OTE endpoint is used for testing purposes only and the domain name databases are not kept up to date.

Details about the usage of the tool can be obtained by running `daddy --help`.

Rather than supplying the API key and API secret to `daddy` every time it is run, a better option is to store these in `daddy`'s config file. The location of this file depends on the operating system:

| OS      | Config file location                           |
| ------- | ---------------------------------------------- |
| Unix    | `~/.config/daddy/config`                       |
| macOS   | `~/.daddy/config`                              |
| Windows | `C:\Users\<user>\AppData\Roaming\daddy\config` |

The `config` file has to be formatted as s JSON file. The API key and API secret are store in the `key` and `secret` keys, respectively.
