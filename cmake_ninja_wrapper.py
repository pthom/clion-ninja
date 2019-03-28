#!/usr/bin/python

import sys
import os
import subprocess
import shutil
import re
import select
import os.path

# ---------------------- Configuration section ------------------------------

if os.path.exists("/usr/local/bin/cmake"):
    REAL_CMAKE = "/usr/local/bin/cmake"
else:
    REAL_CMAKE = "/usr/bin/cmake"


if os.path.exists("/usr/local/bin/ninja"):
    NINJA_PATH = "/usr/local/bin/ninja"
else:
    NINJA_PATH = "/usr/bin/ninja"


TRACING = True


# --------------------------- Code section ----------------------------------

def trace(message, argv = []):
    if not TRACING:
        return

    with open('/tmp/cmake_wrapper.log', 'a') as log:
        if not argv == []:
            log.write("\n\n")

        log.write(message)

        if not argv == []:
            argv = '"%s"' % ('" "'.join(argv))
            log.write("\n\n\t%s\n\tat: %s\n" % (argv, os.getcwd()))

def call_cmake(passing_args):
    """Call real cmake as a subprocess passing it's output both to stdout and trace file."""
    passing_args = [REAL_CMAKE] + passing_args
    trace("Calling real cmake:", passing_args)

    proc = subprocess.Popen(passing_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
    while True:
        reads = [proc.stdout.fileno(), proc.stderr.fileno()]
        ret = select.select(reads, [], [])

        for fd in ret[0]:
            if fd == proc.stdout.fileno():
                line = proc.stdout.readline()
                sys.stdout.write(line)
                sys.stdout.flush()
                trace(line)
            if fd == proc.stderr.fileno():
                line = proc.stderr.readline()
                sys.stderr.write(line)
                sys.stderr.flush()
                trace(line)

        if proc.poll() != None:
            break

    for line in proc.stdout:
        sys.stdout.write(line)
        trace(line)

    for line in proc.stderr:
        sys.stderr.write(line)
        trace(line)

    return proc.poll()

class CMakeCache(object):
    """CMake cache management utility"""
    def __init__(self, path):
        super(CMakeCache, self).__init__()
        self.path = path

    def alter(self, variable, value):
        """
        Change a variable value in CMake cache.
        TODO: Add variable if it doesn't already exist
        """
        if not os.path.isfile(self.path):
            return

        with open(self.path, 'r') as cache_file:
            cache_file_stat = os.stat(myfile)
            cache_data = cache_file.read()

        pattern = '%s=.*' % re.escape(variable)
        replacement = '%s=%s' % (variable, value)
        cache_data = re.sub(pattern, replacement, cache_data)

        with open(self.path, 'w') as cache_file:
            cache_file.write(cache_data)
            os.utime(cache_file, (cache_file_stat.st_atime, cache_file_stat.st_mtime))

    def ninjafy(self):
        self.alter('CMAKE_GENERATOR:INTERNAL', 'Ninja')
        self.alter('CMAKE_MAKE_PROGRAM:FILEPATH', NINJA_PATH)

    def makefy(self):
        self.alter('CMAKE_GENERATOR:INTERNAL', 'Unix Makefiles')
        self.alter('CMAKE_MAKE_PROGRAM:FILEPATH', '/usr/bin/make')

def ninjafy_argv(original):
    """Replace Unix Makefiles generator with Ninja"""
    found = False
    foundG = False
    processed = []
    next_g = False
    for a in original:
        if a == '-G':
            next_g = True
            foundG = True
        elif next_g and 'Unix Makefiles' in a:
            #a = a.replace('CodeBlocks - Unix Makefiles', 'Ninja')
            a = "Ninja"
            next_g = False
            found = True
        processed.append(a)
    trace("ninjafy_argv => found = " + str(found) + " FoundG=" + str(foundG))
    return processed



trace('Originally called:', sys.argv)

# Check if generator argument was specified
if '-G' in sys.argv:
    # Generate Makefile artifacts required by CLion
    cache = CMakeCache('CMakeCache.txt')
    cache.makefy()
    exit_code = call_cmake(sys.argv[1:])
    if exit_code != 0:
        sys.exit(exit_code)

    # Generate Ninja artifacts for actual build
    passing_args = ninjafy_argv(sys.argv[1:])
    cache.ninjafy()
    sys.exit(call_cmake(passing_args))
else:
    sys.exit(call_cmake(sys.argv[1:]))
