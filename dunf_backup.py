#!/usr/bin/python3

import os
import sys

import configparser
from argparse import ArgumentParser
from subprocess import call

from time import strftime
from timeit import default_timer

__author__ = 'Mihkal Dunfjeld'
__version__ = "1.2.0"


def argss():
    parser = ArgumentParser()
    parser.add_argument("-t", "--type", choices=['i', 'f'], default='f',
                        help='Specifies backup type...'
                             ' (i)ncremental or (f)ull backup.')
    parser.add_argument("-c", "--compression",
                        help="Whether to compress the files"
                        "or not..", action="store_true")
    parser.add_argument("-d", "--destination", nargs=1,
                        help="Manually specify destination...")
    parser.add_argument("-C", "--config", nargs=1, help="Specify path to config"
                                                        "file.")
    parser.add_argument('-e', '--encrypt', action='store_true',
                        help='Use GPG to encrypt output file...')
    return parser.parse_args()


class Config(object):
    args = argss()

    def __init__(self, config=configparser.ConfigParser()):
        """Initializes config object and reads config file."""
        self._config = config
        self.read_config()

    def read_config(self):
        """Attempts to read the config file and creates a new one if it does not
        exist. If -C option is passed, that file is read instead."""
        if self.args.config is None:
            p = os.path.join(os.environ['HOME'], '.dunf_backup.ini')
            if os.path.exists(p):
                return self._config.read(p)
            else:
                self.create_config(p)
                sys.exit(0)
        else:
            file = self.args.config[0]
            if os.path.isfile(file):
                return self._config.read(file)
            sys.exit(1)

    def create_config(self, cfg_path):
        """Creates INI file with appropriate sections and default values
        if INI file does not exist."""
        p = '{}/Documents/'.format(os.environ['HOME'])
        self._config.add_section('Default')
        self._config.set('Default', 'destination', p)
        self._config.set('Default', 'number_of_backups', '5')
        self._config.add_section('Include')
        self._config.add_section('Exclude')
        with open(cfg_path, 'w') as file:
            self._config.write(file)
        print("Config file not found. Creating config file {}".format(cfg_path))

    def get_config_entry(self, section, key):
        return self._config.get(section, option=key)

    def get_destination(self):
        """Returns user specified destination directory if -d flag is set. If
        flag is not set default destination is fetched from config."""
        return self.args.destination[0] if self.args.destination else \
            str(self._config.get('Default', option='destination'))

    def include_list(self):
        """Fetches all include paths from config file and returns them
        as a single space-separated string."""
        paths = []
        for key, value in self._config.items('Include'):
            if os.path.exists(value):
                paths.append(value)
        return ' '.join(paths)

    def exclude_list(self):
        """Fetches all exclude paths from dunf_backup.ini and returns them
        as a single string. An empty string in index 0 is added to get --exclude
        at the front of the first path in index 1."""
        paths = ['']
        for key, value in self._config.items('Exclude'):
            if os.path.exists(value):
                paths.append(value)
        return ' --exclude='.join(paths)


class Backup(object):
    def __init__(self, config=Config()):
        """Initializes the Backup() object with destination, include/exclude
        lists."""
        self._config = config
        self._destination = self._config.get_destination()
        self._include_list = self._config.include_list()
        self._exclude_list = self._config.exclude_list()

    def get_args(self):
        """Returns the status of all arguments whether they are passed to the
        script or not."""
        return self._config.args

    def get_destination(self):
        """Returns path destination directory."""
        return self._destination

    @staticmethod
    def get_filename():
        """Creates filename that is derived from time and type of compression."""
        timestamp = strftime("%Y_%m_%d__%H_%M")  # yyyy_mm_dd__hh_MM
        if Config.args.compression:
            return "backup_{}_compressed.tar.gz".format(timestamp)
        else:
            return "backup_{}.tar.gz".format(timestamp)

    def run_backup(self, destination, compress, encrypt):
        """Runs the backup script..."""
        tar_option = ' -czvf' if compress else ' -cvf'
        start_time = default_timer()
        call("tar{a} {b} {c}{d} {e}".format(
             a=self._exclude_list,
             b=tar_option,
             c=destination,
             d=self.get_filename(),
             e=self._include_list), shell=True)
        elapsed = default_timer() - start_time
        print("Saved to {}...".format(destination))
        print("Backup completed in {} seconds...".format(elapsed.__round__(3)))

    def rotate(self):
        """Deletes all but the x newest backups"""
        x = self._config.get_config_entry('Default', 'number_of_backups')
        old_files = [i for i in sorted(os.listdir(self._destination))[:-int(x)]]
        for file in old_files:
            os.remove(os.path.join(self._destination, file))


def main():
    """Main entry point"""
    backup = Backup()
    destination = backup.get_destination()
    argument = backup.get_args()
    compress = argument.compression
    encrypt = argument.encrypt
    if argument.type == 'f':
        backup.run_backup(destination, compress, encrypt)
        backup.rotate()
    elif argument.type == 'i':
        raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
