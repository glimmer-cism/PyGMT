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

"""Plotting legends and keys."""

__all__ = ['KeyArea','colourkey']

from PyGMTarea import AreaXY

class KeyArea(AreaXY):
    """Legends and keys."""

    def __init__(self,parent,pos=[0.,0.],size=[5.,5.]):
        """Initialising Key area.

        parent: can be either a Canvas or another Area.
        pos: position of area relative to the parent
        size: size of GMT area
        """

        AreaXY.__init__(self,parent,pos=pos,size=size)
        # number of rows and columns
        self.__num=[3,4]
        self.__entrysize = [float(self.size[0])/float(self.__num[0]),float(self.size[1])/float(self.__num[1])]
        self.__legendnr = 0

    def __setnum(self,var):
        try:
            l = len(var)
        except:
            raise TypeError, 'Expected a list or an array'
        if l != 2:
            raise ValueError, 'Expected array or list of size 2'
        self.__num[0]=var[0]
        self.__num[1]=var[1]
        self.__entrysize = [float(self.size[0])/float(self.__num[0]),float(self.size[1])/float(self.__num[1])]
    def __getnum(self):
        return self.__num
    num = property(__getnum,__setnum)

    def __pos(self):
        y = (self.num[1]-0.5 - int(self.__legendnr)/int(self.num[0]) )*self.__entrysize[1]
        x = ( int(self.__legendnr)%int(self.num[0]) )*self.__entrysize[0]
        self.__legendnr = self.__legendnr+1
        return (x,y)

    def plot_symbol(self,name,colour,symbol,size='0.5'):
        (x,y) = self.__pos()
        self.plotsymbol([x+0.4],[y],size=size,symbol=symbol,args='-G%s -W0'%colour)
        self.text([x+0.8,y],name,textargs='10 0 0 ML')

    def plot_line(self,name,pen):
        (x,y) = self.__pos()
        self.line('-W%s'%pen,[x,x+0.7],[y,y])
        self.text([x+0.8,y],name,textargs='10 0 0 ML')
        
    def plot_box(self,name,colour):
        self.plot_symbol(name,colour,'s','0.7')

def colourkey(parent,colourmap,title='',args='',pos=[0.,0.],size=[10.,1.],labeloff=1.8):
    """Plotting a colour legend.

    parent: can be either a Canvas or another Area.
    colourmap: name of colourmap file
    args: some GMT arguments for psscale
    title: title of legend
    pos: position of area relative to the parent
    size: size of legend
    """

    area = AreaXY(parent,pos=pos,size=size)
    linesp = '%f%s'%(1.1*float(area.labelsize[:-1]),area.labelsize[-1])
    if size[0]>size[1]:
        area.GMTcommand('psscale','-D%f/%f/%f/%fh -C%s %s'%(size[0]/2.,size[1],size[0],size[1],colourmap,args))
        xbox = AreaXY(area,pos=[0.,-2.8],size=[size[0],2.])
        textarg = '%s 0 %s %s %s %f c'%(area.labelsize[:-1],area.labelfont,'LT',linesp,size[0])
        xbox.partext([0.,2.],title,textargs=textarg,comargs='-N')
    else:
        area.GMTcommand('psscale','-D%f/%f/%f/%f -C%s %s'%(0.,size[1]/2.,size[1],size[0],colourmap,args))
        ybox = AreaXY(area,pos=[size[0]+labeloff,0.],size=[2.,size[1]])
        textarg = '%s 90 %s %s %s %f c'%(area.labelsize[:-1],area.labelfont,'LT',linesp,size[1])
        ybox.partext([0.,0],title,textargs=textarg,comargs='-N')
