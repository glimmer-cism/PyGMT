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

import PyGMT,string
print dir(PyGMT)

l= PyGMT.command('gmtdefaults','-L')
for i in string.split(l,'\n'):
    print i

l = PyGMT.command('mapproject','-R7.000000/49.000000/60.182301/71.915405r -JB33.500000/60.500000/52.833332/68.166664/10',20*'20 50\n')
print len(l)
print l[0:40]

defaults = PyGMT.Defaults()
print defaults.GetCurrentKeys()
defaults['X_ORIGIN'] = '0.c'
print defaults
del defaults['X_ORIGIN']

defaults['X_ORIGIN'] = '0.c'
defaults['Y_ORIGIN'] = '0.c'
defaults['ANNOT_MIN_ANGLE'] = '10'
print defaults.GetCurrentSettings()
defaults.Reset()
print defaults.GetCurrentSettings()
