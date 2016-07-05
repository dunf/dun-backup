#!/usr/bin/python3

from os import path, environ
import sys
from argparse import ArgumentParser
from subprocess import call
import configparser
from time import strftime
from timeit import default_timer

__author__ = 'Mihkal Dunfjeld'
__version__ = "1.0.0"


class Config(object):
    def __init__(self, config=configparser.ConfigParser()):
        """Initializes config object and reads config file."""
        self._config = config
        self.read_config()

    def read_config(self):
        """Reads the config file."""
        try:
            return self._config.read(path.join(environ['HOME'],
                                               '.dunf_backup.ini'))
        except configparser.ParsingError:
            print("Config file not found...")
            self.create_config()

    def create_config(self):
        """Creates INI file with appropriate sections and default values
        if it does not exist."""
        raise NotImplementedError

    def get_destination(self):
        """Returns user specified destination directory if -d flag is set. If
        flag is not set default destination is fetched from config."""
        return args.destination[0] if args.destination else \
            str(self._config.get('Default', option='destination'))

    def include_list(self):
        """Fetches all include paths from dunf_backup.ini and returns them
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

    def get_destination(self):
        """Returns path destination directory."""
        return self._destination

    @staticmethod
    def get_filename():
        """Creates filename that is derived from time and type of compression."""
        timestamp = strftime("%Y_%m_%d__%H_%M")  # yyyy_mm_dd__hh_MM
        if args.full:
            return "arch_backup_{}_full_compression.7z".format(timestamp)
        elif args.copy:
            return "arch_backup_{}.tar.gz".format(timestamp)
        else:
            pass

# Probably won't work at the moment.
    def full_compression(self, dst):
        """Performs backup with full compression."""
        start_time = default_timer()
        call("7za a -t7z -mx9 -mmt=on " + dst + self.get_filename() +
             self._include_list + " -xr@" + self._exclude_list, shell=True)
        elapsed = default_timer() - start_time
        print("Saved to {}...".format(dst))
        print("Backup completed in {} seconds...".format(elapsed.__round__(3)))

    def copy_files(self, dst):
        """Performs backup with no compression."""
        start_time = default_timer()
        call("tar --exclude " +
             self._exclude_list +
             " -cvf " +
             dst +
             self.get_filename() +
             " " +
             self._include_list, shell=True)
        elapsed = default_timer() - start_time
        print("Saved to {}...".format(dst))
        print("Backup completed in {} seconds...".format(elapsed.__round__(3)))

    def incremental_backup(self, dst):
        raise NotImplementedError


# Should I continue with this or just abandon the idea?
def check_dependency():
    """Checks if 7zip is installed and asks the user to install it if its not."""
    if not path.exists("/usr/bin/7za"):
        print("Missing dependency p7zip-full")
        call("sudo pacman -S p7zip", shell=True)


def args():
    parser = ArgumentParser()
    mu = parser.add_mutually_exclusive_group()
    mu.add_argument("-f", "--full", help="Performs full backup with"
                    "maximum compression", action="store_true")
    mu.add_argument("-c", "--copy", help="Copy files to archive with no "
                    "compression", action="store_true")
    mu.add_argument("-i", "--increment", help="Performs incremental backup",
                    action="store_true")
    parser.add_argument("-d", "--destination", nargs=1,
                        help="Manually specify destination")
    return parser.parse_args()


def main():
    """Main entry point"""
    backup = Backup()
    dst = backup.get_destination()
    if len(sys.argv) < 2:
        print("dunf BACKUP {}".format(__version__))
        print("For help, use the '-h' or '--help' parameter")
    elif args.full:
        backup.full_compression(dst)
    elif args.copy:
        backup.copy_files(dst)
    elif args.increment:
        backup.incremental_backup(dst)
    else:
        pass


if __name__ == "__main__":
    args = args()
    sys.exit(main())
