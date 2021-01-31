"""
``$ nlwiki_articlequality -h``
::

    This script provides access to a set of utilities for extracting features
    and building article quality classifiers.

    * extract_E_and_D -- Gathers E and D quality labels from XML dumps
    * fetch_failed_A_nominations -- Gathers B quality labels from failed A class nominations

    Usage:
        nlwiki_articlequality (-h | --help)
        nlwiki_articlequality <utility> [-h | --help]

    Options:
        -h | --help  Prints this documentation
        <utility>    The name of the utility to run
"""
import sys
import traceback
from importlib import import_module


USAGE = """Usage:
    nlwiki_articlequality (-h | --help)
    nlwiki_articlequality <utility> [-h | --help]\n"""


def main():

    if len(sys.argv) < 2:
        sys.stderr.write(USAGE)
        sys.exit(1)
    elif sys.argv[1] in ("-h", "--help"):
        sys.stderr.write(__doc__ + "\n")
        sys.exit(1)
    elif sys.argv[1][:1] == "-":
        sys.stderr.write(USAGE)
        sys.exit(1)

    module_name = sys.argv[1]
    try:
        module = import_module(".utilities." + module_name,
                               package="nlwiki_articlequality")
    except ImportError:
        sys.stderr.write(traceback.format_exc())
        sys.stderr.write("Could not find utility {0}.\n".format(module_name))
        sys.exit(1)

    module.main(sys.argv[2:])
