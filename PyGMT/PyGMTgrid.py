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

"""Class for handling GMT grids."""

__all__=['Grid','read_grid','triangulate']

import numpy,gmtio,os,tempfile
from PyGMTcommand import command
from StringIO import StringIO

class Grid(object):
    """GMT grid.

    This class discribes GMT grids. The data is stored as a numpy Python
    array. """

    def __init__(self):
        """Initialise  grid structure"""
        self.__x_minmax = numpy.zeros(2,dtype='f')
        self.__y_minmax = numpy.zeros(2,dtype='f')
        self.__node_offset = 0
        self.__z_scale = 1.0
        self.z_offset = 0.0
        self.xunits = ''
        self.yunits = ''
        self.zunits = ''
        self.title = ''
        self.command = ''
        self.remark = ''
        self.__data = None

    # Minimum and maximum x values
    def __set_x_minmax(self,val):
        try:
            l = len(val)
        except:
            raise TypeError, 'Expected a list or an array'
        if l != 2:
            raise ValueError, 'Expected array or list of size 2'
        if val[0]>=val[1]:
            raise ValueError, 'minimum value must be larger than maximum: %f, %f'%(val[0],val[1])
        self.__x_minmax[0] = val[0]
        self.__x_minmax[1] = val[1]
    def __get_x_minimax(self):
        return self.__x_minmax
    x_minmax = property(__get_x_minimax,__set_x_minmax)

    # Minimum and maximum y values
    def __set_y_minmax(self,val):
        try:
            l = len(val)
        except:
            raise TypeError, 'Expected a list or an array'        
        if l != 2:
            raise ValueError, 'Expected array or list of size 2'
        if val[0]>=val[1]:
            raise ValueError, 'minimum value must be larger than maximum: %f, %f'%(val[0],val[1])
        self.__y_minmax[0] = val[0]
        self.__y_minmax[1] = val[1]
    def __get_y_minimax(self):
        return self.__y_minmax
    y_minmax = property(__get_y_minimax,__set_y_minmax)

    # node offset
    def __set_node_offset(self,val):
        if val not in [0,1]:
            raise ValueError, 'Node_offset can be either 0 or 1.'
        self.__node_offset = val
    def __get_node_offset(self):
        return self.__node_offset
    node_offset = property(__get_node_offset,__set_node_offset)

    # z scale
    def __set_z_scale(self,val):
        __z_scale = float(val)
    def __get_z_scale(self):
        return self.__z_scale
    z_scale = property(__get_z_scale,__set_z_scale)    

    # data
    def __set_data(self,val):
        if type(val) is not numpy.ndarray:
            raise ValueError, 'Expected a numpy array'
        if len(val.shape) != 2:
            raise ValueError, 'Expected a numpy array with two dimensions'
        self.__data = val
    def __get_data(self):
        return self.__data
    data = property(__get_data,__set_data)    

    def __check_grid(self):
        if self.__data == None:
            raise AssertionError, 'Data array is not set yet'
        if self.__x_minmax[0] == self.__x_minmax[1]:
            raise AssertionError, 'X min/max is not set yet'
        if self.__y_minmax[0] == self.__y_minmax[1]:
            raise AssertionError, 'Y min/max is not set yet'
    
    def write(self,file):
        """Write grid to GMT binary file.

        file: is an open file handle"""

        self.__check_grid()

        gmtio.write(file,self.__x_minmax,self.__y_minmax,self.__node_offset,self.z_scale,self.z_offset,self.xunits,self.yunits,self.zunits,self.title,self.remark,self.__data)

    def grdtrack(self,trackx,tracky):
        """Sample grid along a track specified as xy pairs.

        trackx: x coordinates of transect
        tracky: y coordinates of transect        
        """

        #write grid to a temporary file
        grdfile = tempfile.NamedTemporaryFile(suffix='.grd')
        grdname  = grdfile.name
        self.write(grdfile.file)
        grdfile.flush()

        xydata = StringIO()
        for i in range(0,len(trackx)):
            xydata.write('%f %f\n'%(trackx[i],tracky[i]))

        arg = '-G%s=bf -Q '%grdname
        zdata = command('grdtrack',arg,indata=xydata.getvalue())
        profile = []
        i = 0
        lines = zdata.split('\n')
        j = 0
        for i in range(0,len(trackx)):
            if j<len(lines)-1:
                l = lines[j]
                z = l.split()
            else:
                profile.append(float('NaN'))
                continue
            if (abs(trackx[i]-float(z[0]))>5. or abs(tracky[i]-float(z[1]))>5.):
                profile.append(float('NaN'))
                continue
            profile.append(float(z[2]))
            j = j + 1
            
        # cleaning up
        grdfile.close()
        return profile

    def project(self,args):
        """Project grid using grdproject.

        args: GMT grdproject args."""


        ingrdfile = tempfile.NamedTemporaryFile(suffix='-in.grd')
        ingrdname  = ingrdfile.name
        self.write(ingrdfile.file)
        ingrdfile.flush()

        outgrdfile = tempfile.NamedTemporaryFile(suffix='-out.grd')
        outgrdname  = outgrdfile.name
        
        command('grdproject','%s=bf -G%s=bf %s'%(ingrdname,outgrdname,args))

        prj = read_grid(outgrdfile.file)

        ingrdfile.close()
        outgrdfile.close()
        return prj
        
    def gridinfo(self):
        """Print grid info."""
        print 'x_minmax    :',self.__x_minmax
        print 'y_minmax    :',self.__y_minmax
        print 'node_offset :',self.__node_offset
        print 'z_scale     :',self.z_scale
        print 'z_offset    :',self.z_offset
        print 'xunits      :',self.xunits
        print 'yunits      :',self.yunits
        print 'zunits      :',self.zunits
        print 'title       :',self.title
        print 'command     :',self.command
        print 'remark      :',self.remark
        print 'size        :',self.__data.shape

def read_grid(file):
    """Read GMT grid from file handle or filename string
    
     * If file is a file object (return by open), then file is assumed to be
       doubles in the host byte order (i.e. GMT binary grid)

     * If file is a string, that filename is read by libgmt and can be any
       valid grid file that GMT can read.
     """

    # new grid
    grid = Grid()
    (grid.x_minmax,grid.y_minmax,grid.node_offset,grid.z_scale,grid.z_offset,grid.xunits,grid.yunits,grid.zunits,grid.title,grid.remark,grid.data) = gmtio.read(file)

    return grid

def triangulate(x,y,z,xinc,yinc):
    """Triangulate (x,y,z) points and return a GMT grid.

    x: list/array containing x values
    y: list/array containing y values
    z: list/array containing z values
    xinc: spacing in x direction
    yinc: spacing in y direction
    """

    if len(x)!=len(y) or len(x)!=len(z):
        raise ValueError, 'Expecting same length of arrays'

    xyzdata = StringIO()
    for i in range(0,len(x)):
        xyzdata.write('%f %f %f\n'%(x[i],y[i],z[i]))

    region=command('minmax','-I%f/%f'%(xinc,yinc),indata=xyzdata.getvalue())

    grdname = '.grid'
    arg = '-G%s=bf -I%f/%f %s '%(grdname,
                                xinc,yinc,
                                region)
    command('triangulate',arg,indata=xyzdata.getvalue())



    grdfile = file(grdname)
    grid = read_grid(grdfile)
    grdfile.close()
    # cleaning up
    os.remove(grdname)

    return grid
