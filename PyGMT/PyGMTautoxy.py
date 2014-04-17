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

"""PyGMT class for automatically resized cartesian plots."""

__all__ = ['AutoXY']

from PyGMTarea import AreaXY
import PyGMTutil, numpy, math

class AutoXY(AreaXY):
    """Cartesian plotting area."""

    def __init__(self,parent,pos=[0.,0.],size=[10.,10.],logx=False,logy=False):
        """Initialising GMT area.

        parent: can be either a Canvas or another Area.
        pos: position of area relative to the parent
        size: size of GMT area
        logx: set to True if the x axis should be logarithmic
        logy: set to True if the y axis should be logarithmic
        """

        # initialising data
        AreaXY.__init__(self,parent,pos=pos,size=size,logx=logx,logy=logy)

        self.ll = [None,None]
        self.ur = [None,None]
        self.regionstring = None

        self.finalised = False
        self.__plots = []

    def line(self,args,xloc,yloc):
        """Plot a line.

        args: arguments passed to psxy (for colours...)

        The line is defined a list of x and y locations
        """
        if (self.finalised):
            AreaXY.line(self,args,xloc,yloc)
        else:
            p = AutoXY_type_line(args,xloc,yloc)
            (self.ll[0],self.ll[1],self.ur[0],self.ur[1]) = p.get_bb((self.ll[0],self.ll[1],self.ur[0],self.ur[1]))
            self.__plots.append(p)

    def steps(self,args,xloc,yloc):
        """Plot steps.

        args: arguments passed to psxy (for colours...)

        The line is defined a list of x and y locations
        """
        if (self.finalised):
            AreaXY.steps(self,args,xloc,yloc)
        else:
            p = AutoXY_type_steps(args,xloc,yloc)
            (self.ll[0],self.ll[1],self.ur[0],self.ur[1]) = p.get_bb((self.ll[0],self.ll[1],self.ur[0],self.ur[1]))
            self.__plots.append(p)

    def point(self,xloc,yloc,xe,ye,args=''):
        """Plot a point with errors.
        
        xloc:   list of x-coordinates of locations
        yloc:
        xe:     list of x errors
        ye:     list of y errors"""

        if (self.finalised):
            AreaXY.point(self,xloc,yloc,xe,ye,args=args)
        else:
            p = AutoXY_type_point(xloc,yloc,xe,ye,args=args)
            (self.ll[0],self.ll[1],self.ur[0],self.ur[1]) = p.get_bb((self.ll[0],self.ll[1],self.ur[0],self.ur[1]))
            self.__plots.append(p)

    def plotsymbol(self,xloc,yloc,size='1',symbol='c',args=''):
        """Plot symbols.

        xloc:   list of x-coordinates of locations
        yloc:
        size:   list of or single value giving size of symbol (strings)
        symbol: list of or single symbol code, see manpage of psxy
        args:   more arguments
        """
        if (self.finalised):
            AreaXY.plotsymbol(self,xloc,yloc,size=size,symbol=symbol,args=args)
        else:
            p = AutoXY_type_symbols(args,xloc,yloc,size=size,symbol=symbol)
            (self.ll[0],self.ll[1],self.ur[0],self.ur[1]) = p.get_bb((self.ll[0],self.ll[1],self.ur[0],self.ur[1]))
            self.__plots.append(p)

    def image(self,grid,colourmap,args=''):
        """Create a colour image of a 2D grid.

        grid: is the GMT grid to be plotted
        colourmap: is the colourmap to be used
        args: further arguments"""

        if (self.finalised):
            AreaXY.image(self,grid,colourmap,args=args)
        else:
            p = AutoXY_type_image(grid,colourmap,args=args)
            (self.ll[0],self.ll[1],self.ur[0],self.ur[1]) = p.get_bb((self.ll[0],self.ll[1],self.ur[0],self.ur[1]))
            self.__plots.append(p)

    def contour(self,grid,contours,args):
        """Plot contours of a 2D grid.

        grid: is the GMT grid to be contoured
        contours: list of contour intervals
        args: further arguments"""

        if (self.finalised):
            AreaXY.contour(self,grid,contours,args)
        else:
            p = AutoXY_type_contour(grid,contours,args)
            (self.ll[0],self.ll[1],self.ur[0],self.ur[1]) = p.get_bb((self.ll[0],self.ll[1],self.ur[0],self.ur[1]))
            self.__plots.append(p)


    def finalise(self,expandx=False,expandy=False):
        """Finalise autoXY plot.

        i.e. set up region and do all the actual plotting.
        expandx, expandy: when set to True expand region to sensible value.
        """

        # setup region
        if self.ll[0] == self.ur[0]:
            self.ll[0]=self.ll[0]-1
            self.ur[0]=self.ur[0]+1
        if self.ll[1] == self.ur[1]:
            self.ll[1]=self.ll[1]-1
            self.ur[1]=self.ur[1]+1
        if expandx:
            interval =PyGMTutil.round_up(self.ur[0]-self.ll[0],factors=range(1,11))
            fact = 10.**math.floor(math.log10(interval))
            self.ll[0] = math.floor((self.ll[0]/fact-0.1))*fact
            self.ur[0] = math.ceil((self.ur[0]/fact+0.1))*fact
        if expandy:
            interval =PyGMTutil.round_up(self.ur[1]-self.ll[1],factors=range(1,11))
            fact = 10.**math.floor(math.log10(interval))
            self.ll[1] = math.floor((self.ll[1]/fact-.1))*fact
            self.ur[1] = math.ceil((self.ur[1]/fact+0.1))*fact
        self.setregion(self.ll,self.ur)

        self.finalised = True
        
        for p in range(0,len(self.__plots)):
            self.__plots[p].plot(self)

    def coordsystem(self,grid=False):
        """Draw coordinate system.

        grid: grid = anot if true and [xy]grid not set

        The resulting coordinate system is controlled by the following attributes:

        A.lablesize : axis label size in points
        A.labelfont : axis label font numer
        A.xlaboff   : label offset from axis
        A.ylaboff
        A.xlabel    : xaxis label string 
        A.ylabel    : yaxis label string
        A.xtic      : tick mark spacing
        A.ytic 
        A.xgrid     : grid spacing
        A.ygrid 
        A.xanot     : anotation spacing
        A.yanot 
        A.axis      : GMT axis string (WESN)
        """
        
        if (not self.finalised):
            self.finalise()
        AreaXY.coordsystem(self,grid=grid)
        

class AutoXY_type_line(object):
    """class for line plots."""

    def __init__(self,args,xloc,yloc):
        """Initialise.

        args: arguments passed to psxy (for colours...)
        x, y: point coordinates."""

        self.args = args
        self.xloc = []
        self.yloc = []
        for i in range(0,len(xloc)):
            if xloc[i]!="nan" and yloc[i]!="nan":
                if '%f'%xloc[i]!="nan" and '%f'%yloc[i]!="nan":
                    self.xloc.append(xloc[i])
                    self.yloc.append(yloc[i])

    def get_bb(self,bb):
        """Get bounding box.
        bb: old bounding box"""

        new_bb = [min(self.xloc),min(self.yloc),max(self.xloc),max(self.yloc)]
        for i in range(0,2):
            if bb[i] != None:
                new_bb[i] = min(bb[i],new_bb[i])
        for i in range(2,4):
            if bb[i] != None:
                new_bb[i] = max(bb[i],new_bb[i])        
        return tuple(new_bb)

    def plot(self,area):
        """Plot data.

        area: area to be used for plotting"""

        area.line(self.args,self.xloc,self.yloc)

class AutoXY_type_steps(AutoXY_type_line):
    """class for steps."""

    def plot(self,area):
        """Plot data.

        area: area to be used for plotting"""

        area.steps(self.args,self.xloc,self.yloc)

class AutoXY_type_symbols(AutoXY_type_line):
    """class for symbol plots."""

    def __init__(self,args,xloc,yloc,size='1',symbol='c'):
        """Initialise.

        args: arguments passed to psxy (for colours...)
        x, y: point coordinates.
        size:   list of or single value giving size of symbol (strings)
        symbol: list of or single symbol code, see manpage of psxy"""
        
        self.args = args
        self.size = size
        self.symbol = symbol
        self.xloc = []
        self.yloc = []
        for i in range(0,len(xloc)):
            if '%f'%xloc[i]!="nan" and '%f'%yloc[i]!="nan":
                self.xloc.append(xloc[i])
                self.yloc.append(yloc[i])

    def plot(self,area):
        """Plot data.

        area: area to be used for plotting"""

        area.plotsymbol(self.xloc,self.yloc,size=self.size,symbol=self.symbol,args=self.args)

class AutoXY_type_image(object):
    """Class for image plots."""

    def __init__(self,grid,colourmap,args=''):
        """Initialise.

        grid: is the GMT grid to be plotted
        colourmap: is the colourmap to be used
        args: further arguments"""

        self.grid = grid
        self.colourmap = colourmap
        self.args = args

    def get_bb(self,bb):
        """Get bounding box.
        bb: old bounding box"""

        new_bb = [self.grid.x_minmax[0],self.grid.y_minmax[0],self.grid.x_minmax[1],self.grid.y_minmax[1]]
        for i in range(0,2):
            if bb[i] != None:
                new_bb[i] = min(bb[i],new_bb[i])
        for i in range(2,4):
            if bb[i] != None:
                new_bb[i] = max(bb[i],new_bb[i])
        return tuple(new_bb)

    def plot(self,area):
        """Plot data.

        area: area to be used for plotting"""

        area.image(self.grid,self.colourmap,args=self.args)

class AutoXY_type_contour(AutoXY_type_image):
    """Class for contour plots."""

    def __init__(self,grid,contours,args):
        """ Initialise.

        grid: is the GMT grid to be contoured
        contours: list of contour intervals
        args: further arguments"""

        self.grid = grid
        self.contours = contours
        self.args = args

    def plot(self,area):
        """Plot data.

        area: area to be used for plotting"""

        area.contour(self.grid,self.contours,self.args)

class AutoXY_type_point(AutoXY_type_line):
    """Class for point plots (with error bars)."""

    def __init__(self,xloc,yloc,xe,ye,args=''):
        """Plot a point with errors.
        
        xloc:   list of x-coordinates of locations
        yloc:
        xe:     list of x errors
        ye:     list of y errors"""

        self.xloc = []
        self.yloc = []
        self.xe = []
        self.ye = []
        for i in range(0,len(xloc)):
            if '%f'%xloc[i]!="nan" and '%f'%yloc[i]!="nan":
                self.xloc.append(xloc[i])
                self.yloc.append(yloc[i])
                self.xe.append(xe[i])
                self.ye.append(ye[i])

        self.args = args

    def plot(self,area):
        """Plot data.

        area: area to be used for plotting"""

        area.point(self.xloc,self.yloc,self.xe,self.ye,args=self.args)
