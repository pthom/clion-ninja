# Ninja support for CLion IDE

This script enables Ninja-powered builds in CLion IDE by wrapping around CMake, which it uses.

## Disclaimer

This script is provided AS IS with no guarantees given or responsibilities taken by the author. 
This script relies on undocumented features of CLion IDE and may lead to instability of build and/or IDE.
Use it on your own risk under [WTFPL](http://www.wtfpl.net/) terms.

## Getting started

Supported OS: I've tested this scipt under Ubuntu and python 2.7. I suppose it should work on Mac and Windows too but I've never tested it.

0. Make sure you have python 2.7 installed.
1. Download cmake_ninja_wrapper.py and give it execution permission.
2. Edit REAL_CMAKE variable at the beginning of the script to point at CLion's bundled CMake binary (recommended) or at system CMake.
3. In CLion, go to Settings → Build, Execution, Deployment → Toolchains
4. Under "CMake executable" select cmake_ninja_wrapper.py script.
 
Make sure that CLion successfully detects make program (it should be still /usr/bin/make) and C/C++ compiler. At this point you are done. Go, reload you CMake project and try to build it.

## Troubleshooting

In case of any troubles try setting TRACING variable at the beginning of the file to True and re-parsing CMake project in IDE. After that look at /tmp/cmake_wrapper.log for any insights :-)
