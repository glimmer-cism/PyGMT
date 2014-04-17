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

"""Base class for GMT areas.

This is where all the fun happens"""

__all__=['Area','AreaXY','AreaGEO']

from PyGMTcommand import *
from PyGMTcanvas import *
from PyGMTutil import round_up, round_down
from StringIO import StringIO
import os, numpy, tempfile

class Area(object):
    """Base class for GMT areas."""

    def __init__(self,parent,pos=[0.,0.]):
        """Initialising GMT area.

        parent: can be either a Canvas or another Area.
        pos: position of area relative to the parent"""
        # setting up parent
        if isinstance(parent,Canvas):
            self.canvas = parent
        elif isinstance(parent,Area):
            self.canvas = parent.canvas
        else:
            raise TypeError, 'Expected a Canvas or an Area'
        # and defaults
        self.verbose = parent.verbose
        self.defaults = Defaults(parent.defaults.GetCurrentSettings())

        # position and size
        self.pos = pos
        for i in [0,1]:
            self.pos[i] = self.pos[i] + parent.pos[i]
        self.size = None

        # GMT projection and region
        self.ll = [None,None]
        self.ur = [None,None]
        self.regionstring = None
        self.projection = None

        # coordinate system stuff
        self.labelsize = self.defaults.GetCurrentItem('LABEL_FONT_SIZE')
        self.labelfont = self.defaults.GetCurrentItem('LABEL_FONT')
        self.xlabel = ''
        self.ylabel = ''
        self.xlaboff = 1.
        self.ylaboff = 1.5
        self.xtic = ''
        self.ytic = ''
        self.xgrid = ''
        self.ygrid = ''
        self.xanot = ''
        self.yanot = ''
        self.title = ''
        self.axis = self.defaults.GetCurrentItem('BASEMAP_AXES')

        # used for clipping
        self.__doplot = True
        
    def setregion(self,ll,ur,rectangular=True):
        """Set region string.

        ll: coords of lower left corner (WS)
        ur: coords of upper right corner (EN)
        rectangular: true if rectangular region (see e.g. psbasemap manpage)
        """

        self.ll = ll
        self.ur = ur
        if rectangular:
            self.regionstring = '%s/%s/%s/%sr'%(ll[0],ll[1],ur[0],ur[1])
        else:
            self.regionstring = '%s/%s/%s/%s'%(ll[0],ur[0],ll[1],ur[1])

    def GMTcommand(self,com,arguments,indata=''):
        """Simple plot command.

        com: name of the GMT command
        arguments: string containing arguments for GMT command
        indata: data piped into GMT command

        switch on verbose GMT execution by setting A.verbose = True

        This is a wrapper function for command, which automatically adds the
        file name, offsets, region and projection parameters.
        """

        # setting up displacements
        disp = [0,0]
        for i in [0,1]:
            disp[i] = self.pos[i]-self.canvas.pos[i]
            self.canvas.pos[i] = self.pos[i]
            
        # setting up argument string
        arg = "%s -K -O -X%f -Y%f >> %s"%(arguments, disp[0],disp[1],self.canvas.name)
        # running command
        command(com, arg, indata=indata, verbose=self.verbose)

    def canvascom(self,com, arguments, indata=''):
        """Plot to the GMT canvas.

        com: name of the GMT command
        arguments: string containing arguments for GMT command
        indata: data piped into GMT command

        switch on verbose GMT execution by setting A.verbose = True

        This is a wrapper function for command, which automatically adds the
        file name, offsets, region and projection parameters.
        """

        # checking if region and projection is set
        if self.regionstring == None:
            raise NotImplementedError, 'Region of interest is not specified yet'
        if self.projection == None:
            raise NotImplementedError, 'Projection is not specified yet'

        self.GMTcommand(com,'-R%s -J%s '%(self.regionstring,self.projection)+arguments,indata=indata)

    def gridcom(self,com,grid,arguments):
        """Plot grid to the GMT canvas.

        com: name of the GMT command
        grid: GMT grid to be plotted
        arguments: string containing arguments for GMT command"""
        
        # checking if region and projection is set
        if self.regionstring == None:
            raise NotImplementedError, 'Region of interest is not specified yet'
        if self.projection == None:
            raise NotImplementedError, 'Projection is not specified yet'

        # setting up displacements
        disp = [0,0]
        for i in [0,1]:
            disp[i] = self.pos[i]-self.canvas.pos[i]
            self.canvas.pos[i] = self.pos[i]
            
        # setting up argument string
        arg = "=bf -R%s -J%s %s -K -O -X%f -Y%f >> %s"%(self.regionstring,self.projection,
                                                    arguments, disp[0],disp[1],
                                                    self.canvas.name)
        gridcommand(com,arg,grid,verbose=self.verbose)

    def text(self,coords,text,textargs='12 0 0 LB',comargs=''):
        """Wrapper for pstext.

        coords: [x,y] coordinates of text
        text: text string (see pstext manpage for special formats)
        textargs: string containing \"size angle fontno justify\"
                  defaults: \"12 0 0 LB\", see pstext manpage
        comargs: arguments passed to pstext command"""

        # calling pstext
        self.canvascom('pstext',comargs,indata='%f %f %s %s\n'%(coords[0],coords[1],textargs,text))

    def partext(self,coords,text,textargs='12 0 0 LB 13p  6 c',comargs=''):
        """Wrapper for pstext in paragraph mode

        coords: [x,y] coordinates of text
        text: text string (see pstext manpage for special formats)
        textargs: string containing \"size angle fontno justify linespace parwidth parjust\"
                  defaults: \"12 0 0 LB 13p 6 c\", see pstext manpage
        comargs: arguments passed to pstext command"""

        # calling pstext
        self.canvascom('pstext','-M '+comargs,indata='>%f %f %s\n%s\n'%(coords[0],coords[1],textargs,text))


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

        # generating basemap string
        basemap = False
        yafg = False
        basemapstring = ''
        if self.xanot != '':
            basemap = True
            basemapstring = basemapstring + 'a%s'%self.xanot
        if self.xtic != '':
            basemap = True
            basemapstring = basemapstring + 'f%s'%self.xtic
        if self.xgrid != '':
            basemap = True
            basemapstring = basemapstring + 'g%s'%self.xgrid
        else:
            if grid and self.xanot != '':
                basemapstring = basemapstring + 'g%s'%self.xanot
        if basemap:
            if self.yanot != '':
                yafg = True
                if basemapstring[-1] != '/' : basemapstring = basemapstring + '/'
                basemapstring = basemapstring + 'a%s'%self.yanot
            if self.ytic != '':
                yafg = True
                basemapstring = basemapstring + 'f%s'%self.ytic
            if self.ygrid != '':
                yafg = True
                basemapstring = basemapstring + 'g%s'%self.ygrid
            else:
                if grid and self.yanot != '':
                    basemapstring = basemapstring + 'g%s'%self.yanot
            if yafg:
                basemapstring = basemapstring + '/'
        if self.title != '':
            basemapstring = basemapstring + ':.' + self.title + ':'

        # empty basemap string?
        if not basemap:
            x = '%f'%(round_up((self.ur[0]-self.ll[0])/self.size[0]))
            basemapstring = basemapstring + 'a%s'%x
            if grid:
                basemapstring = basemapstring + 'g%s'%x
        if not yafg:
            basemapstring = basemapstring + '/'
            y = '%f'%(round_up((self.ur[1]-self.ll[1])/self.size[1]))
            basemapstring = basemapstring + 'a%s'%y
            if grid:
                basemapstring = basemapstring + 'g%s'%y

        basemapstring=basemapstring+self.axis
        self.canvascom('psbasemap','-B%s'%basemapstring)
        
        # plotting axis labels
        linesp = '%f%s'%(1.1*float(self.labelsize[:-1]),self.labelsize[-1])
        if self.xlabel != '':
            plotlabel = False
            if 'N' in self.axis:
                p = 'LB'
                pp = 0.
                xbox = AreaXY(self,pos=[0.,self.size[1]+self.xlaboff],size=[self.size[0],5.])
                plotlabel = True
            elif 'S' in self.axis:
                p = 'LT'
                pp = 5.
                xbox = AreaXY(self,pos=[0.,-5.-self.xlaboff],size=[self.size[0],5.])
                plotlabel = True
            if plotlabel:
                textarg = '%s 0 %s %s %s %f c'%(self.labelsize[:-1],self.labelfont,p,linesp,self.size[0])
                xbox.partext([0.,pp],self.xlabel,textargs=textarg,comargs='-N')

        if self.ylabel != '':
            plotlabel = False
            if 'E' in self.axis:
                pp = 0.
                p = 'LT'
                ybox = AreaXY(self,pos=[self.size[0]+self.ylaboff,0.],size=[5.,self.size[1]])
                plotlabel = True
            elif 'W' in self.axis:
                pp = -5.+self.ylaboff
                p = 'LB'
                ybox = AreaXY(self,pos=[-5.,0.],size=[5.,self.size[1]])
                plotlabel = True
            if plotlabel:
                textarg = '%s 90 %s %s %s %f c'%(self.labelsize[:-1],self.labelfont,p,linesp,self.size[1])
                ybox.partext([pp,0],self.ylabel,textargs=textarg,comargs='-N')

    def plotsymbol(self,xloc,yloc,size='1',symbol='c',args=''):
        """Plot symbols.

        xloc:   list of x-coordinates of locations
        yloc:
        size:   list of or single value giving size of symbol (strings)
        symbol: list of or single symbol code, see manpage of psxy
        args:   more arguments
        """

        outstring = StringIO()
        if not isinstance(size,list):
            outsize = size
        if not isinstance(symbol,list):
            outsymbol = symbol
        for i in range(0,len(xloc)):
            if isinstance(size,list):
                outsize = size[i]
            if isinstance(symbol,list):
                outsymbol = symbol[i]
                
            outstring.write('%f %f %s %s\n'%(xloc[i],yloc[i],outsize,outsymbol))
            
        self.canvascom('psxy',args+' -S',indata=outstring.getvalue())

    def point(self,xloc,yloc,xe,ye,args=''):
        """Plot a point with errors.
        
        xloc:   list of x-coordinates of locations
        yloc:
        xe:     list of x errors
        ye:     list of y errors"""

        outstring = StringIO()
        for i in range(0,len(xloc)):
            outstring.write('%f %f %f %f\n'%(xloc[i],yloc[i],xe[i],ye[i]))
        self.canvascom('psxy',args+' -Exy0 ',indata=outstring.getvalue())
        
    def line(self,args,xloc,yloc):
        """Plot a line.

        args: arguments passed to psxy (for colours...)

        The line is defined a list of x and y locations
        """
        
        outstring = StringIO()
        for i in range(0,len(xloc)):
            if '%f'%xloc[i]!="nan" and '%f'%yloc[i]!="nan":
                outstring.write('%f %f\n'%(xloc[i],yloc[i]))

        self.canvascom('psxy',args,indata=outstring.getvalue())

    def steps(self,args,xloc,yloc):
        """Plot steps.

        args: arguments passed to psxy (for colours...)

        The line is defined a list of x and y locations
        """

        x = []
        y = []
        for i in range(0,len(xloc)-1):
            x.append(xloc[i])
            y.append(yloc[i])
            x.append(xloc[i+1])
            y.append(yloc[i])
        x.append(xloc[i+1])
        y.append(yloc[i+1])

        self.line(args,x,y)
        
    def image(self,grid,colourmap,args=''):
        """Create a colour image of a 2D grid.

        grid: is the GMT grid to be plotted
        colourmap: is the colourmap to be used
        args: further arguments"""

        if not self.__doplot:
            return
        self.gridcom('grdimage',grid,'-C%s %s'%(colourmap,args))

    def contour(self,grid,contours,args,cntrtype='c'):
        """Plot contours of a 2D grid.

        grid: is the GMT grid to be contoured
        contours: list of contour intervals
        args: further arguments
        cntrtype: contourtype, c for normal contour, a for annotated"""

        if not self.__doplot:
            return

        assert cntrtype in ['a','c']
        

        # checking if cntr levels are given, i.e. cntr is a list
        # if so create a tempory file
        if isinstance(contours,list):
            cntrfile = tempfile.NamedTemporaryFile(suffix='.cntr')
            cntr  = cntrfile.name
            for c in contours:
                cntrfile.write("%f\t%s\n"%(float(c),cntrtype))
            cntrfile.flush()
        if isinstance(contours,str):
            cntr = contours
            
        self.gridcom('grdcontour',grid,'-C%s %s'%(cntr,args))

        # clean up
        if isinstance(contours,list):
            cntrfile.close()

    def clip(self,grid,contour):
        """Create a clip path from contouring grid."""

        c = float(contour)

        # create a file containing contour level
        cntrfile = tempfile.NamedTemporaryFile(suffix='.cntr')
        cntrname  = cntrfile.name
        cntrfile.write("%f\tc\n"%c)
        cntrfile.flush()

        # sorting out boundaries
        grid.data[0,:] = numpy.where(grid.data[0,:]>c,c-0.1,grid.data[0,:]).astype('f')
        grid.data[-1,:] = numpy.where(grid.data[-1,:]>c,c-0.1,grid.data[-1,:]).astype('f')
        grid.data[:,0] = numpy.where(grid.data[:,0]>c,c-0.1,grid.data[:,0]).astype('f')
        grid.data[:,-1] = numpy.where(grid.data[:,-1]>c,c-0.1,grid.data[:,-1]).astype('f')
        
        # creating clip path by contouring grid
        clipfile = tempfile.NamedTemporaryFile(suffix='.clip')
        clipname = clipfile.name
        arg = "=bf -R%s -J%s -C%s -M -D%s > /dev/null"%(self.regionstring,self.projection,cntrname,clipname)
        gridcommand('grdcontour',arg,grid,verbose=self.verbose)

        nl = len(clipfile.readlines())

        if nl>1:
            # creating clip path
            self.canvascom('psclip','%s -M'%clipname)
        else:
            self.__doplot = False

        clipfile.close()
        cntrfile.close()

    def unclip(self):
        """Reset clip path."""
        if not self.__doplot:
            self.__doplot = True
            return
        self.canvascom('psclip','-C')

    def project(self,long,lat,inv=False):
        """Project long, lat to projected grid.
 
        long: list of longitudes
        lat:  list of latitudes
        inv:  do inverse transform if true
 
        return a tuple containing x and y locations
        """
 
        instring = StringIO()
        for i in range(0,len(long)):
            instring.write('%f %f\n'%(long[i],lat[i]))
 
        # setting up arguments
        if inv:
            args = '-I '
        else:
            args = ''
        args = args + '-R%s -J%s'%(self.regionstring,self.projection)
        outstring = command('mapproject',args,indata=instring.getvalue(), verbose=self.verbose)

        xloc = []
        yloc = []
        for s in outstring.split('\n'):
            d = s.split()
            if len(d) > 1:
                xloc.append(float(d[0]))
                yloc.append(float(d[1]))
        return (xloc,yloc)
                                                              


        
class AreaXY(Area):
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
        Area.__init__(self,parent,pos=pos)
        self.size = size

        # resize region
        self.re_llx = False
        self.re_lly = False
        self.re_urx = False
        self.re_ury = False
        self.setregion([0.,0.],size)

        if logx:
            xstring = '%fl'%size[0]
        else:
            xstring = '%f'%size[0]
        if logy:
            ystring = '%fl'%size[1]
        else:
            ystring = '%f'%size[1]
        
        self.projection='X%s/%s'%(xstring,ystring)

        # setting up paper size
        self.paper = Area(self,pos=[0,0.])
        self.paper.size = size
        self.paper.setregion([0.,0.],size,rectangular=True)
        self.paper.projection='X%f/%f'%(size[0],size[1])
        
    def setregion(self,ll,ur):
        """Set region string.

        ll: coords of lower left corner (WS)
        ur: coords of upper right corner (EN)

        The region of interested can be automatically adjusted if the
        corresponding attribute is set to True:
        A.re_llx A.re_lly A.re_urx A.re_ury
        """

        if self.re_llx:
            ll[0] = round_down(ll[0])
        if self.re_lly:
            ll[1] = round_down(ll[1])
        if self.re_urx:
            ur[0] = round_up(ur[0])
        if self.re_ury:
            ur[1] = round_up(ur[1])
        Area.setregion(self,ll,ur,rectangular=True)

class AreaGEO(Area):
    """Geographic plotting area."""

    def __init__(self,parent,projection,pos=[0.,0.],size=10.):
        """Initialising GMT area.

        parent: can be either a Canvas or another Area.
        projection: GMT projection string (excluding size)
        pos: position of area relative to the parent
        size: size of GMT area
              the area is assumed square if only a single value for size is given.
        """

        # initialising data
        Area.__init__(self,parent,pos=pos)
        if isinstance(size,list):
            sizestring = '%f/%f'%(size[0],size[1])
            self.size = size
        else:
            sizestring = '%f'%(size)
            self.size = [size,None]
        self.projection = '%s/%s'%(projection,sizestring)

        self.paper = Area(self,pos=[0.,0.])
        
    def setregion(self,ll,ur,rectangular=True):
        """Set region string.

        ll: coords of lower left corner (WS)
        ur: coords of upper right corner (EN)
        rectangular: true if rectangular region (see e.g. psbasemap manpage)
        """

        Area.setregion(self,ll,ur,rectangular=rectangular)

        # checking if we need to calculate the ysize
        if self.size[1] == None:
            (x,y) =  self.project([ur[0]],[ur[1]])
            self.size[1] = y[0]

        self.paper.size = self.size
        self.paper.setregion([0.,0.],self.size,rectangular=True)
        self.paper.projection='X%f/%f'%(self.size[0],self.size[1])

    def project(self,long,lat,inv=False):
        """Project long, lat to projected grid.

        long: list of longitudes
        lat:  list of latitudes
        inv:  do inverse transform if true

        return a tuple containing x and y locations
        """

        instring = StringIO()
        for i in range(0,len(long)):
            instring.write('%f %f\n'%(long[i],lat[i]))

        # setting up arguments
        if inv:
            args = '-I '
        else:
            args = ''
        args = args + '-R%s -J%s'%(self.regionstring,self.projection)
        outstring = command('mapproject',args,indata=instring.getvalue(), verbose=self.verbose)
        
        xloc = []
        yloc = []
        for s in outstring.split('\n'):
            d = s.split()
            if len(d) > 1:
                xloc.append(float(d[0]))
                yloc.append(float(d[1]))

        return (xloc,yloc)

    def coastline(self,args):
        """Plot coastline.

        args: arguments past on to pscoast
        """

        self.canvascom('pscoast',args)
