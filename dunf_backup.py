#!/usr/bin/python3

from os import path
import sys
from argparse import ArgumentParser
from subprocess import call
import configparser
from time import strftime
from timeit import default_timer

__author__ = 'Mihkal Dunfjeld'
__version__ = "1.0.0"


def args():
    parser = ArgumentParser()
    mu = parser.add_mutually_exclusive_group()
    mu.add_argument("-f", "--full", help="Performs full backup with"
                    "maximum compression", action="store_true")
    mu.add_argument("-c", "--copy", help="Performs full backup with "
                    "no compression", action="store_true")
    mu.add_argument("-i", "--increment", help="Performs incremental backup",
                    action="store_true")
    parser.add_argument("-d", "--destination", nargs=1,
                        help="Manually specify destination")
    return parser.parse_args()


class Config(object):
    def __init__(self, config=configparser.ConfigParser()):
        """Initializes config object and reads config file."""
        self._config = config
        self.read_config()

    def read_config(self):
        """Reads the config file."""
        try:
            return self._config.read('./dunf_backup.ini')
        except configparser.ParsingError:
            print("Config file not found...")

    def get_destination(self):
        """Returns user specified destination directory if -d flag is set. If
        flag is not set default destination is fetched from config."""
        return args.destination[0] if args.destination else \
            str(self._config.get('Default', option='destination'))

    def include_list(self):
        """Fetches all include paths from dunf_backup.ini and returns them
        as a single space-separeted string."""
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
        self._config = config

    def include_list(self):
        """Returns path to include list"""
        return self._config.include_list()

    def exclude_list(self):
        """Returns path to exclude list"""
        return self._config.exclude_list()

    def get_destination(self):
        """Returns path to destination directory."""
        return self._config.get_destination()

    @staticmethod
    def get_filename():
        """Creates filename that is derived from time and type of compression."""
        timestamp = strftime("%Y_%m_%d__%H_%M")  # yyyy_mm_dd__hh_mm
        if args.full:
            return "arch_backup_{}_full_compression.7z".format(timestamp)
        elif args.copy:
            return "arch_backup_{}.tar.gz".format(timestamp)
        else:
            pass

    def full_compression(self, dest):
        """Performs backup with full compression."""
        start_time = default_timer()
        call("7za a -t7z -mx9 -mmt=on " + dest + self.get_filename() +
             self.include_list() + " -xr@" + self.exclude_list(), shell=True)
        elapsed = default_timer() - start_time
        print("Saved to {}...".format(dest))
        print("Backup completed in {} seconds...".format(elapsed.__round__(3)))

    def copy_files(self, dest):
        """Performs backup with no compression."""
        start_time = default_timer()
        call("tar --exclude " + self.exclude_list() + " -cvf " + dest +
             self.get_filename() + " " + self.include_list(), shell=True)
        elapsed = default_timer() - start_time
        print("Saved to {}...".format(dest))
        print("Backup completed in {} seconds...".format(elapsed.__round__(3)))

    def incremental_backup(self, dest):
        raise NotImplementedError


# Should I continue with this or just abandon the idea?
def check_dependency():
    """Checks if 7-zip is installed and asks the user """
    if not path.exists("/usr/bin/7za"):
        print("Missing dependency p7zip-full")
        call("sudo pacman -S p7zip", shell=True)


def main():
    """Main entry point"""
    backup = Backup()
    dest = backup.get_destination()
    if len(sys.argv) < 2:
        print("dunf BACKUP SCRIPT {}".format(__version__))
        print("For help, use the '-h' or '--help' parameter")
    elif args.full:
        backup.full_compression(dest)
    elif args.copy:
        backup.copy_files(dest)
    elif args.increment:
        backup.incremental_backup(dest)
    else:
        pass


if __name__ == "__main__":
    args = args()
    sys.exit(main())
