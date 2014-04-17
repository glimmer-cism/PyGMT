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

import PyGMT

plot = PyGMT.Canvas('blub.ps',size='A4')
plot.defaults['LABEL_FONT_SIZE']='12p'
plot.defaults['ANNOT_FONT_SIZE']='10p'
area = PyGMT.AreaGEO(plot,'B33.500000/60.500000/52.833332/68.166664',pos=[1,0],size=10.)
area.verbose=True
area.setregion([7,49],[59.92,71.95])
area.coastline('-W')
area.coordsystem(grid=True)
plot.close()
