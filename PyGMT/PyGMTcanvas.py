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

"""Basic class used for setting up """

__all__=['Canvas','PaperSize']

from PyGMTcommand import *
import os


def PaperSize(size,orientation):
    """Paper sizes."""
    
    paper = {'a4' : [18., 24.7],
             'a3' : [29.7, 37.0]}
    size = size.lower()
    if size in paper:
        if orientation.lower() == 'portrait':
            return [paper[size][0],paper[size][1]]
        else:
            return [paper[size][1],paper[size][0]]

class Canvas:
    """Defines GMT output media.


    """
    def __init__(self,name,size='A4',orientation='portrait',reset=True):
        """Initialise new GMT output.

        name: name of postscript file to be written to
        size: paper size (default A4)
        orientation: orientation of output media (default portrait)
        reset: if True .gmtdefaults and .gmtcommands is deleted and thus reset to global settings"""

        # getting rid of GMT files
        if reset:
            try:
                os.remove('.gmtcommands')
            except:
                pass
            try:
                os.remove('.gmtdefaults')
            except:
                pass

        # setting up basic defaults
        self.defaults = Defaults()
        self.defaults['PAPER_MEDIA'] = size
        self.defaults['PAGE_ORIENTATION'] = orientation
        self.papersize = PaperSize(size,orientation)

        self.verbose = False
        #start a new plot
        self.name = name
        command('pstext','-JX1 -R0/1/0/1 -K > %s'%self.name,'0 0 10 0 0 0 ',warn=False)

        #setting position
        self.pos = [0.,0.]
        
    def close(self):
        """Finishing off GMT plot."""

        #start a new plot
        command('pstext','-JX1 -R0/1/0/1 -O >> %s'%self.name,'0 0 10 0 0 0 ',warn=False)
        
