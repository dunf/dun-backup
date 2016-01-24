#!/usr/bin/python3.4

__author__ = 'dunf'



from os import path
from sys import argv
from argparse import ArgumentParser
from subprocess import call, check_output
from time import strftime
from timeit import default_timer

# ---------------------- ARGPARSE ----------------------------------------------
parser = ArgumentParser()
mutually_exclusive = parser.add_mutually_exclusive_group()
mutually_exclusive.add_argument("-f", "--full", help="Performs full backup with"
                                "maximum compression", action="store_true")
mutually_exclusive.add_argument("-c", "--copy", help="Performs full backup with "
                                "no compression", action="store_true")
mutually_exclusive.add_argument("-i", "--increment", help="Performs incremental backup",
                                action="store_true")

args = parser.parse_args()
FULL_COMPRESSION = args.full
NO_COMPRESSION = args.copy


# ------------------------ GLOBAL VARIABLES ------------------------------------

# ------------------------------------------------------------------------------

class Backup(object):
    # This is where files are stored
    destination = "/media/md/CrucialMX100/backups/"

     # Current date and time, format: year_month_day__hour_minute
    current_time = strftime("%Y_%m_%d__%H_%M")

    # Path to the file that contains paths to included in backupscript
    include_list = "/home/md/scripts/dunf_backup/dunf_include.conf"

    exclude_list = "/home/md/scripts/dunf_backup/dunf_exclude.conf"


    # Output full compression filename
    full_compress_filename = "ubuntu_backup_" + current_time + "_full_compression.7z"

    # Output no compression filename
    no_compress_filename = "ubuntu_backup_" + current_time + "_no_compression.7z"

    # Full compression 7-Zip parameters
    full_compress_args = " a -t7z -mx9 -mmt=on " + destination + \
                         full_compress_filename + " -ir@" + include_list + " -xr@" + exclude_list

    # No compression 7-Zip parameters
    no_compress_args = " a -t7z -mx0 " + destination + \
                       no_compress_filename + " -ir@" + include_list + " -xr@" + exclude_list


    # Incremental backup parameters
    # Kommer i v0.2.0

    def check_dependency(self):
        if path.exists("/usr/bin/7za"):
            return True
        else:
            call("sudo apt-get install p7zip-full")

    # Does a full backup using maximum compression
    def full_compression(self):
        if path.isdir(self.destination):
            start_time = default_timer()
            call("7za" + self.full_compress_args, shell=True)
            elapsed = default_timer() - start_time
            print("Backup completed in ", elapsed.__round__(3), " seconds")
        else:
            print("Destination not found...")



    # Does a full backup with no compression.
    def no_compression(self):
        if path.isdir(self.destination):
            start_time = default_timer()
            call("7za" + self.no_compress_args, shell=True)
            elapsed = default_timer() - start_time
            print("Backup completed in ", elapsed.__round__(3), " seconds")
        else:
            print("Destination not found...")



if __name__ == "__main__":
    backup = Backup()
    backup.check_dependency()
    if len(argv) < 2:
        print("dunf BACKUP SCRIPT v0.1.2")
        print("For help, use the '-h' or '--help' parameter")
    elif FULL_COMPRESSION:
        backup.full_compression()
    elif NO_COMPRESSION:
        backup.no_compression()
    else:
        pass
