"""
This script is used to compare log files which are usually hard to compare for various reasons:
 - some data should not be compared (timestamps, thread identifiers, etc)
 - irrelevant events in the wrong order mess up with the diff
Hence, the script tries to get the relevant data and stores them with a clean format in a well defined file hierarchy.
Then, the output folders can be compared with a proper tool such as meld or kompare.
"""

import sys
import re
import tempfile
import os
import subprocess

# ULOGCAT FORMAT
#########################################
# Examples:
# 03-23 15:39:00.412 I SENSORSSVC  (aap-4752/AndroidAutoMsg-5000)   : Activate driver distraction restrictions with mask 0x0
# 03-23 15:39:00.412 I             (aap-4752/readerThread-6272)     : Phone reported protocol version 1.7
# 03-23 15:39:00.404 I DISPMAN     (display-focus-m-1577)           : onRequireInputCategory request from 'aap'
# 03-24 08:39:18.608 I             (parrot-logpacka-2055/parrot-logpacka-2088): logpackager-ulogcat-stream-plugin: Recording is stopped

# Regexp for an ulogcat line
ULOGCAT_RE = r"^(?P<date>\d\d-\d\d \d\d:\d\d:\d\d.\d\d\d) (?P<level>.) (?P<tag>[^( ]*)\s*\((?:(?P<processname>.*)-(?P<processid>.*)\/)?(?P<threadname>[^\/]*)-(?P<threadid>\d+)\)\s*: (?P<content>.*)$"

# Output format for an ulogcat line
ULOGCAT_OUTPUT_FORMAT = (
    "DATE {level} {tag} ({processname}-PID/{threadname}-TID): {content}"
)

ULOGCAT_CONFIG = (ULOGCAT_RE, ULOGCAT_OUTPUT_FORMAT)


# LOGCAT FORMAT
#########################################
# Examples:
# 03-24 08:36:15.304  4688  5002 D PM_AapThread: Send DriverDistraction: 0
# 03-24 08:36:15.306  4688  5002 I PM_AapThread: Request type: PmPopUp(AAP_USB_ERROR, DISMISS)
# 03-24 08:36:15.308  4451  4451 I VehiclePropertyService: onChangeEvent id = 555745548
# 03-24 08:36:15.308  4451  4451 D VehiclePropertyService: onChangeEvent: property ignored
# Regexp for a logcat line
LOGCAT_RE = r"^(?P<date>\d\d-\d\d \d\d:\d\d:\d\d.\d\d\d)\s+(?P<processid>\d+)\s+(?P<threadid>\d+)\s+(?P<level>.)\s+(?P<tag>[^:]*):(?P<content>.*)$"

# Output format for a logcat line
LOGCAT_OUTPUT_FORMAT = "DATE PID TID {level} {tag} {content}"

LOGCAT_CONFIG = (LOGCAT_RE, LOGCAT_OUTPUT_FORMAT)


# DMESG FORMAT
#########################################
# Examples:
# [43189.299397] usb 1-4: new high-speed USB device number 27 using xhci_hcd
# [43189.460250] usb 1-4: New USB device strings: Mfr=1, Product=2, SerialNumber=3
# [43189.460255] usb 1-4: Product: USB download gadget
# [43288.264615] usb 1-4: USB disconnect, device number 27
# Regexp for a dmesg line
DMESG_RE = r"^\[(?P<date>\d+\.\d+)\] (?P<content>.*)$"
# Output format for a dmesg line
DMESG_OUTPUT_FORMAT = "{content}"

DMESG_CONFIG = (DMESG_RE, DMESG_OUTPUT_FORMAT)


# FORMAT CONFIGURATION
#########################################

# Log format used - could be ULOGCAT_CONFIG, LOG_CONFIG, DMESG_CONFIG
LOG_CONFIG = ULOGCAT_CONFIG


def extract_data(filepath):
    """Extract relevant data from file whose path is provided - return a dictionnary."""
    with open(filepath, encoding="ISO-8859-1") as f:
        log_re, out_format = LOG_CONFIG
        no_match = []
        bigdict = dict()
        for line in f:
            line = line.strip()
            if line:
                m = re.match(log_re, line)
                if m is None:
                    no_match.append(line)
                else:
                    d = m.groupdict()
                    out_line = out_format.format(**d)
                    d["ALL"] = "ALL"
                    for k, v in d.items():
                        bigdict.setdefault(k, dict()).setdefault(v, []).append(out_line)
        if no_match:
            print("%s lines from %s did not match:" % (len(no_match), filepath))
            for line in no_match:
                print("  '" + line + "'")
            print("%s lines from %s did not match" % (len(no_match), filepath))
        return bigdict


def store_relevant_data_in_a_tmp_folder(filepath):
    """Store relevant data from file whose path is provided into a tmp folder."""
    # Extract relevant data from file
    bigdict = extract_data(filepath)
    # Store data in multiple files in a temporary folder
    tmpdir = tempfile.mkdtemp()
    print("%s analysed in %s" % (filepath, tmpdir))
    for k in ["tag", "threadname", "threadid", "processname", "processid", "ALL"]:
        if k in bigdict:
            newdir = tmpdir + "/" + k
            os.mkdir(newdir)
            for value, lines in bigdict[k].items():
                cleanval = "".join(c if c.isalnum() else "_" for c in str(value))
                newfile = "%s/%s_%s.txt" % (newdir, k, cleanval)
                with open(newfile, "x") as file2:
                    for line in lines:
                        file2.write(line + "\n")
    return tmpdir


def compare_files(filepaths, difftool="meld"):
    """Compare files by storing relevant data into a file hierarchy compared by a dedicated tool."""
    # Store relevant data in /tmp folders
    tmpdirs = [store_relevant_data_in_a_tmp_folder(filepath) for filepath in filepaths]

    # Compare final directories in /tmp
    subprocess.run([difftool] + tmpdirs)


if __name__ == "__main__":
    filepaths = sys.argv[1:]
    compare_files(filepaths)
