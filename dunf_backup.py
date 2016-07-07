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


def Args():
    parser = ArgumentParser()
    mu = parser.add_mutually_exclusive_group()
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
    args = Args()

    def __init__(self, config=configparser.ConfigParser()):
        """Initializes config object and reads config file."""
        self._config = config
        print(self.args)
        self.read_config()

    def read_config(self):
        """Reads the config file."""
        if self.args.config is None:
            try:
                return self._config.read(path.join(environ['HOME'],
                                                   '.dunf_backup.ini'))
            except configparser.ParsingError:
                print("Config file not found. Creating config file "
                      "{}/.dunf_backup.ini.".format(environ['HOME']))
                self.create_config()
                sys.exit(0)
        else:  # If config is user specified
            if path.exists(self.args.config[0]):
                return self._config.read(self.args.config[0])
            else:
                print("Config file does not exist...")
                sys.exit(1)

    def create_config(self):
        """Creates INI file with appropriate sections and default values
        if INI file does not exist."""
        raise NotImplementedError

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
        as a single string."""
        paths = []
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
        call("tar --exclude={a} {b} {c}{d} {e}".format(
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
    dst = backup.get_destination()
    a = backup.get_args()
    compression = a.compression
    if a.type == 'f':
        backup.run_backup(dst, compression)
        pass
    elif a.type == 'i':
        raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
