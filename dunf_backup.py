#!/usr/bin/python3

from os import path
import sys
from argparse import ArgumentParser
from subprocess import call
import configparser
from time import strftime
from timeit import default_timer
from io import StringIO
from io import BytesIO


__author__ = 'Mihkal Dunfjeld'
__version__ = "0.2.3"




# ---------------------- ARGPARSE ----------------------------------------------
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


# ------------------------ CONFIG PARSER ----------------------------------------
class Config(object):
    def __init__(self):
        """Initializes config object and reads config file."""
        self._config = configparser.ConfigParser()
        self.read_config()

    def read_config(self):
        """Reads the config file."""
        try:
            return self._config.read('./config.ini')
        except configparser.ParsingError:
            print("Config file not found...")

    def get_destination(self):
        """Returns user specified destination directory if -d flag is set. If
        flag is not set default destination is fetched from config."""
        return args.destination[0] if args.destination else \
            str(self._config.get('Default', option='destination'))

    def get_include_list(self):
        """Returns the path to the file containing paths to be included
        in backup."""
        return self._config.get('Default', option='include_list')

    def include_list(self):
        f = StringIO()
        paths = []
        for key, value in self._config.items('Include'):
            f.write(str(value))
        return f

    def get_exclude_list(self):
        """Returns the path to the file containing paths to be excluded
        in backup."""
        return self._config.get('Default', option='exclude_list')


# --------------------------- Backup Class --------------------------------------
class Backup(object):
    def __init__(self, config = Config()):
        self._config = config

    def include_list(self):
        """Returns path to include list"""
        return self._config.include_list()

    def exclude_list(self):
        """Returns path to exclude list"""
        return self._config.get_exclude_list()

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
            return "arch_backup_{}_no_compression.7z".format(timestamp)
        else:
            pass

    def full_compression(self, dest):
        """Performs backup with full compression."""
        start_time = default_timer()
        call("7za a -t7z -mx9 -mmt=on " + dest + self.get_filename() + " -ir@" \
             + self.include_list() + " -xr@" + self.exclude_list(), shell=True)
        elapsed = default_timer() - start_time
        print("Saved to {}...".format(dest))
        print("Backup completed in {} seconds...".format(elapsed.__round__(3)))

    def no_compression(self, dest):
        """Performs backup with no compression."""
        start_time = default_timer()
        call("7za a -ttar -mx0 " + dest + self.get_filename() + " -ir@" + \
             self.include_list() + " -xr@" + self.exclude_list(),  shell=True)
        elapsed = default_timer() - start_time
        print("Saved to {}...".format(dest))
        print("Backup completed in {} seconds...".format(elapsed.__round__(3)))

    def incremental_backup(self, dest, file_name):
        raise NotImplementedError
        pass


# Should I continue with this or just abandon the idea?
def check_dependency():
    """Checks if 7-zip is installed and asks the user """
    if not path.exists("/usr/bin/7za"):
        print("Missing dependency p7zip-full")
        call("sudo pacman -S p7zip", shell=True)
# ------------------------------------ MAIN -------------------------------------
def main():
    """Main entry point"""

   # args = args()
    backup = Backup()
    dest = backup.get_destination()
    if len(sys.argv) < 2:
        print("dunf BACKUP SCRIPT {}".format(__version__))
        print("For help, use the '-h' or '--help' parameter")
    elif args.full:
        backup.full_compression()
    elif args.copy:
        print(backup.include_list())
        backup.no_compression(dest)
    elif args.increment:
        backup.incremental_backup()
    else:
        pass

if __name__ == "__main__":
    args = args()
    sys.exit(main())