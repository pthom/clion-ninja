#!/usr/bin/python

import sys
import os
import subprocess
import shutil
import re

# ---------------------- Configuration section ------------------------------

REAL_CMAKE = "/usr/bin/cmake"
TRACING = False

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

    proc = subprocess.Popen(passing_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = proc.stdout.readline()
        if not line: break
        sys.stdout.write(line)
        trace(line)
    return proc.wait()

def is_real_project():
    """Detect if called inside clion private directory."""
    cwd = os.getcwd()
    return "clion" in cwd and "cmake" in cwd and "generated" in cwd

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
            cache_data = cache_file.read()

        pattern = '%s=.*' % re.escape(variable)
        replacement = '%s=%s' % (variable, value)
        cache_data = re.sub(pattern, replacement, cache_data)

        with open(self.path, 'w') as cache_file:
            cache_file.write(cache_data)

    def ninjafy(self):
        self.alter('CMAKE_GENERATOR:INTERNAL', 'Ninja')
        self.alter('CMAKE_MAKE_PROGRAM:FILEPATH', '/usr/bin/ninja')

    def makefy(self):
        self.alter('CMAKE_GENERATOR:INTERNAL', 'Unix Makefiles')
        self.alter('CMAKE_MAKE_PROGRAM:FILEPATH', '/usr/bin/make')

def ninjafy_argv(original):
    """Replace Unix Makefiles generator with Ninja"""
    processed = []
    next_g = False
    for a in original:
        if a == '-G':
            next_g = True
        elif next_g and 'Unix Makefiles' in a:
            a = a.replace('Unix Makefiles', 'Ninja')

        processed.append(a)

    return processed



trace('Originally called:', sys.argv)

# Enable wrapping logic only when called inside clion private directory.
if not is_real_project():
    sys.exit(call_cmake(sys.argv[1:]))

# Check if generator argument was specified
if '-G' in sys.argv:
    # Generate Makefile artifacts required by CLion
    cache = CMakeCache('CMakeCache.txt')
    cache.makefy()
    call_cmake(sys.argv[1:])

    # Generate Ninja artifacts for actual build
    passing_args = ninjafy_argv(sys.argv[1:])
    cache.ninjafy()
    call_cmake(passing_args)
else:
    call_cmake(sys.argv[1:])