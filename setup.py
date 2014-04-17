#!/usr/bin/env python

# Copyright 2004, Magnus Hagdorn
# 
# This file is part of PyGMT.
# 
# PyGMT is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# PyGMT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PyGMT; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from distutils.core import setup, Extension
import os, sys,os.path
import numpy

if not hasattr(sys, 'version_info') or sys.version_info < (2,3,0,'alpha',0):
    raise SystemExit, "Python 2.3 or later required to build Numeric."

def check_lib(libname,prefix_var,header):
    """Check if we can find header either in the directory where the environment
    variable prefix_var points to, or /usr/local or /usr."""

    prefix = []

    try:
        prefix.append(os.environ[prefix_var])        
    except KeyError:
        for p in ['/usr/local', '/usr']:
            prefix.append(p)
    for p in prefix:
        include = os.path.join(p, 'include')
        lib = os.path.join(p, 'lib')
        if os.path.exists(os.path.join(include, header)):
            break
    else:
        print 'Error, cannot find %s library in /usr/local and /usr.'%libname
        print 'Set environment variable %s to point to the prefix'%prefix_var
        print 'where %s is installed.'%libname
        sys.exit(1)
    return (include,lib)


(gmt_include, gmt_lib) = check_lib('gmt','GMTHOME','gmt.h')
(ncdf_include, ncdf_lib) = check_lib('netcdf','NETCDF_PREFIX','netcdf.h')

# get path to numpy includes
numpy_inc = os.path.join(sys.modules['numpy'].__path__[0],'core','include')

print
print 'Configuration'
print '-------------'
print 'GMT           : %s, %s'%(gmt_include, gmt_lib)
print 'netCDF        : %s, %s'%(ncdf_include, ncdf_lib)
print 'numpy include : %s'%numpy_inc
print

ext_modules = [
    Extension('PyGMT.gmtio',
              ['src/gmtiomodule.c'],
              include_dirs=[gmt_include,ncdf_include,numpy_inc],
              library_dirs=[gmt_lib,ncdf_lib],
              libraries=['gmt','psl','netcdf']
              ),
    ]

setup (name = "PyGMT",
       version = "0.6",
       description = "Python bindings for the Generic Mapping Tools",
       author = "Magnus Hagdorn",
       author_email = "Magnus.Hagdorn@ed.ac.uk",
       url = "http://www.glg.ed.ac.uk/~mhagdorn/PyGMT/PyGMT.html",
       license = 'GPL',
       packages = ['PyGMT'],
       ext_modules = ext_modules,
       )



#EOF
