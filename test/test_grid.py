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

import numpy,PyGMT

a=numpy.zeros([11,21])
x=numpy.arange(0,11,1.)
y=numpy.arange(10,20.5,0.5)
for j in range(0,21):
    for i in range(0,11):
        a[i,j] = x[i]*x[i] + y[j]*y[j]
b=PyGMT.PyGMTgrid.Grid()
b.x_minmax=[x[0],x[-1]]
b.y_minmax=[y[0],y[-1]]
b.xunits='xu'
b.yunits='yu'
b.zunits='zu'
b.z_title='blub'
b.title='blub'
b.remark='blubber'
b.data = a
b.gridinfo()

f=open('x','w')
b.write(f)
f.close()
