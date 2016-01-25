#!/usr/bin/python3

__author__ = 'Mihkal Dunfjeld'
__version__ = "0.2.0"


from os import path
from sys import argv
from argparse import ArgumentParser
from subprocess import call, check_output
from time import strftime
from timeit import default_timer
import configparser

# ---------------------- ARGPARSE ----------------------------------------------



parser = ArgumentParser()
mutually_exclusive = parser.add_mutually_exclusive_group()
mutually_exclusive.add_argument("-f", "--full", help="Performs full backup with"
                                "maximum compression", action="store_true")
mutually_exclusive.add_argument("-c", "--copy", help="Performs full backup with "
                                "no compression", action="store_true")
mutually_exclusive.add_argument("-i", "--increment", help="Performs incremental backup",
                                action="store_true")

parser.add_argument("-d", '--destination', help="Manually specify destination",
                    action="store_true")
args = parser.parse_args()
FULL_COMPRESSION = args.full
NO_COMPRESSION = args.copy
DESTINATION = args.destination




# ------------------------ CONFIG PARSER ---------------------------------------


config = configparser.ConfigParser()
config.read('config.ini')
def read_config():
    try:
        return config.read('config.ini')

    except configparser.ParsingError:
        print("Config file not found...")

def get_destination():
    if DESTINATION:
        counter = 0
        for var in argv:
            if var == '-d' or var == '--destination':
                return argv[counter+1]
            counter += 1
    else:
        destination = config.get('Default', option='destination')
        return destination





def create_config(self):
    pass
# ------------------------ GLOBAL VARIABLES ------------------------------------


def check_destination(dest):
    if not path.isdir(dest):
        print("Destination not found...")


# ------------------------------------------------------------------------------

class Backup(object):
    # This is where files are stored
    # destination = "/media/md/CrucialMX100/backups/"

     # Current date and time, format: year_month_day__hour_minute
    current_time = strftime("%Y_%m_%d__%H_%M")
    include = " -r@"
    exclude = " xr@"

    # Path to the file that contains paths to included in backup script
    i_list = "/home/md/scripts/dunf_backup/dunf_include.conf"
    e_list = "/home/md/scripts/dunf_backup/dunf_exclude.conf"

    # Output full compression filename
    full_compress_filename = " ubuntu_backup_" + current_time + "_full_compression.7z"

    # Output no compression filename
    no_compress_filename = " ubuntu_backup_" + current_time + "_no_compression.7z "

    # Full compression 7-Zip parameters
    full_compress_args = " a -t7z -mx9 -mmt=on " + get_destination() + \
                         full_compress_filename + include + i_list + exclude + e_list

    # No compression 7-Zip parameters
    no_compress_args = " a -t7z -mx0 " + get_destination() + \
                       no_compress_filename + include + i_list + exclude + e_list

    def check_dependency(self):
        if path.exists("/usr/bin/7za"):
            return True
        else:
            print("Missing dependency p7zip-full")
            call("sudo apt-get install p7zip-full", shell=True)

    # Does a full backup using maximum compression
    def full_compression(self, dest):
        start_time = default_timer()
        call("7za" + self.full_compress_args, shell=True)
        elapsed = default_timer() - start_time
        print("Backup completed in ", elapsed.__round__(3), " seconds")

    # Does a full backup with no compression.
    def no_compression(self, dest):
        start_time = default_timer()
        call("7za a -t7z -mx0 " + dest + self.no_compress_filename + self.include + self.i_list + \
              self.exclude + self.e_list,  shell=True)
        elapsed = default_timer() - start_time
        print("Backup completed in ", elapsed.__round__(3), " seconds")

if __name__ == "__main__":
    backup = Backup()
    # read_config()
    dest = get_destination()
    # backup.check_destination(dest)
    backup.check_dependency()
    if len(argv) < 2:
        print("dunf BACKUP SCRIPT ", __version__)
        print("For help, use the '-h' or '--help' parameter")
    elif FULL_COMPRESSION:
        backup.full_compression(dest)
    elif NO_COMPRESSION:
        backup.no_compression(dest)
    else:
        pass
