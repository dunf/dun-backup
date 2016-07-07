#!/usr/bin/python3

from os import path, environ
import sys
from argparse import ArgumentParser
from subprocess import call
import configparser
from time import strftime
from timeit import default_timer

__author__ = 'Mihkal Dunfjeld'
__version__ = "1.1.0"


def argss():
    parser = ArgumentParser()
    parser.add_argument("-t", "--type", choices=['i', 'f'], default='f',
                        help='Specifies backup type.'
                             ' (i)ncremental or (f)ull backup.')
    parser.add_argument("-c", "--compression",
                        help="Whether to compress the files"
                        "or not.", action="store_true")
    parser.add_argument("-d", "--destination", nargs=1,
                        help="Manually specify destination")
    parser.add_argument("-C", "--config", nargs=1, help="Specify path to config"
                                                        "file.")
    return parser.parse_args()


class Config(object):
    args = argss()

    def __init__(self, config=configparser.ConfigParser()):
        """Initializes config object and reads config file."""
        self._config = config
        self.read_config()

    def read_config(self):
        """Reads the config file."""
        if self.args.config is None:
            p = path.join(environ['HOME'], '.dunf_backup.ini')
            if path.exists(p):
                return self._config.read(path.join(environ['HOME'],
                                                   '.dunf_backup.ini'))
            else:
                self.create_config(p)
                sys.exit(0)
        else:
            if path.exists(self.args.config[0]):
                return self._config.read(self.args.config[0])
            else:
                print("Config file does not exist...")
                sys.exit(1)

    def create_config(self, cfg_path):
        """Creates INI file with appropriate sections and default values
        if INI file does not exist."""
        p = '{}/Downloads/'.format(environ['HOME'])
        self._config.add_section('Default')
        self._config.set('Default', 'destination', p)
        self._config.add_section('Include')
        self._config.add_section('Exclude')
        with open(cfg_path, 'w') as file:
            self._config.write(file)
        print("Config file not found. Creating config file {}".format(cfg_path))

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
            paths.append(value)
        return ' '.join(paths)

    def exclude_list(self):
        """Fetches all exclude paths from dunf_backup.ini and returns them
        as a single string. An empty string in index 0 is added to get --exclude
        at the front of the first path in index 1."""
        paths = ['']
        for key, value in self._config.items('Exclude'):
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
            return "arch_backup_{}_compressed.tar.gz".format(timestamp)
        else:
            return "arch_backup_{}.tar.gz".format(timestamp)

    def run_backup(self, destination, compression):
        """Runs the backup script..."""
        tar_option = ' -czvf' if compression else ' -cvf'
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


def main():
    """Main entry point"""
    backup = Backup()
    destination = backup.get_destination()
    argument = backup.get_args()
    compression = argument.compression
    if argument.type == 'f':
        backup.run_backup(destination, compression)
        pass
    elif argument.type == 'i':
        raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
