#!/usr/bin/python3

from os import path
from sys import argv
from argparse import ArgumentParser
from subprocess import call, check_output
from time import strftime
from timeit import default_timer
import configparser
import sys, os

__author__ = 'Mihkal Dunfjeld'
__version__ = "0.2.1"




# ---------------------- ARGPARSE ----------------------------------------------
parser = ArgumentParser()
mutually_exclusive = parser.add_mutually_exclusive_group()
mutually_exclusive.add_argument("-f", "--full", help="Performs full backup with"
                                "maximum compression", action="store_true")
mutually_exclusive.add_argument("-c", "--copy", help="Performs full backup with "
                                "no compression", action="store_true")
mutually_exclusive.add_argument("-i", "--increment", help="Performs incremental backup",
                                action="store_true")

parser.add_argument("-d", "--destination", nargs=1, help="Manually specify destination")
args = parser.parse_args()
FULL_COMPRESSION = args.full
NO_COMPRESSION = args.copy
DESTINATION = args.destination

# ------------------------ CONFIG PARSER ---------------------------------------


class Config(object):
    config = configparser.ConfigParser()

    def read_config(self):
        try:
            return self.config.read('config.ini')
        except configparser.ParsingError:
            print("Config file not found...")

    def get_destination(self):
        if DESTINATION:
            counter = 0
            for param in argv:
                if param == '-d' or param == '--destination':
                    destination = str(argv[counter+1])
                    return destination
                counter += 1
        else:
            destination = self.config.get('Default', option='destination')
            return str(destination)

    def get_include_list(self):
        include_list = self.config.get('Default', option='include_list')
        return include_list

    def get_exclude_list(self):
        exclude_list = self.config.get('Default', option='exclude_list')
        return exclude_list

    def create_config(self):
        pass

# ------------------------ GLOBAL VARIABLES  AND FUNCTIONS ------------------------------------


# Checks if 7-zip is installed, if not asks the user to install it. Works with apt-get
def check_dependency():
    if not path.exists("/usr/bin/7za"):
        print("Missing dependency p7zip-full")
        call("sudo apt-get install p7zip-full", shell=True)


def get_filename():
    current_time = strftime("%Y_%m_%d__%H_%M")      # yyyy_mm_dd__hh_mm
    if FULL_COMPRESSION:
        return "ubuntu_backup_" + current_time + "_full_compression.7z"
    elif NO_COMPRESSION:
        return "ubuntu_backup_" + current_time + "_no_compression.7z"
    else:
        pass

# ------------------------------------------------------------------------------


class Backup(object):
    config = Config()
    config.read_config()

    def include_list(self):
        return self.config.get_include_list()

    def exclude_list(self):
        return self.config.get_exclude_list()

    # Does a full backup using maximum compression
    def full_compression(self, dest, file_name):
        start_time = default_timer()
        call("7za a -t7z -mx9 -mmt=on " + dest + file_name + " -ir@" + self.include_list() +
             " -xr@" + self.exclude_list(), shell=True)
        elapsed = default_timer() - start_time
        print("Saved to " + dest)
        print("Backup completed in ", elapsed.__round__(3), " seconds")

    # Does a full backup with no compression.
    def no_compression(self, dest, file_name):
        start_time = default_timer()
        call("7za a -t7z -mx0 " + dest + file_name + " -ir@" + self.include_list() + \
             " -xr@" + self.exclude_list(),  shell=True)
        elapsed = default_timer() - start_time
        print("Saved to " + dest)
        print("Backup completed in ", elapsed.__round__(3), " seconds")

if __name__ == "__main__":
    backup = Backup()
    dest = backup.config.get_destination()
    file_name = get_filename()
    if len(argv) < 2:
        print("dunf BACKUP SCRIPT ", __version__)
        print("For help, use the '-h' or '--help' parameter")
    elif FULL_COMPRESSION:
        backup.full_compression(dest, file_name)
    elif NO_COMPRESSION:
        backup.no_compression(dest, file_name)
    else:
        pass
