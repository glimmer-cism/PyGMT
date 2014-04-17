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

"""Low level interface to GMT programms.

"""

__all__=['command','gridcommand','Defaults','getGMTpath']

import os,popen2,fcntl,select, warnings
from cStringIO import StringIO

def getGMTpath():
    """Find the path to GMT binaries."""

    path = os.environ['PATH'].split(':')
    for p in path:
        if os.path.exists(os.path.join(p,'gmtset')):
            return p
    raise RuntimeError, 'Cannot find gmt binaries'
    
def command(command, arguments, indata='', verbose=False, warn=True):
    """Execute GMT command.

    command: name of the GMT command
    arguments: string containing arguments for GMT command
    indata: data piped into GMT command
    verbose: if True, print command
    warn: if True, print warnings
    on success: this function returns the output of the GMT command
    """

    # helper function for non-blocking I/O
    def makeNonBlocking(fd):
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NDELAY)

    path_to_gmt = getGMTpath()
    com = os.path.join(path_to_gmt, command) + ' ' + arguments
    if verbose:
        print com
    # capture stdout and stderr from command
    child = popen2.Popen3(com, True)         
    infile = child.tochild
    infd = infile.fileno()
    outfile = child.fromchild 
    outfd = outfile.fileno()
    errfile = child.childerr
    errfd = errfile.fileno()
    # don't deadlock!
    makeNonBlocking(infd)            
    makeNonBlocking(outfd)            
    makeNonBlocking(errfd)
    outdata = StringIO()
    errdata = StringIO()
    outeof = erreof = 0
    chunksize = 1000
    i=0
    while 1:
        if infile.closed:
            ready = select.select([outfd,errfd],[],[]) # wait for input
        else:
            ready = select.select([outfd,errfd],[infd],[]) # wait for input             
        if outfd in ready[0]:
	    outchunk = outfile.read()
	    if outchunk == '': outeof = 1
	    outdata.write(outchunk)
	if errfd in ready[0]:
	    errchunk = errfile.read()
	    if errchunk == '': erreof = 1
	    errdata.write(errchunk)
        if child.poll()>=0: break
        if not infile.closed:
            if infd in ready[1]:
                end = min((i+1)*chunksize,len(indata))
                if i*chunksize<end:
                    infile.write(indata[i*chunksize:end])
                    i = i+1
                else:
                    infile.close()
    err = child.wait()
    if err != 0: 
	raise RuntimeError, '%s failed w/ exit code %d\n%s' % (command, err, errdata.getvalue())
    if len(errdata.getvalue()) > 0 and err == 0 and warn:
        warnings.warn('%s\n%s' %(command, errdata.getvalue()), RuntimeWarning)
    return outdata.getvalue()

def gridcommand(command, arguments, grid, verbose=False, warn=True):
    """Execute GMT command requiring a GMT grid.

    command: name of the GMT command
    arguments: string containing arguments for GMT command
    grid: GMT grid to be piped into GMT command
    verbose: if True, print command
    warn: if True, print warnings
    on success: this function returns the output of the GMT command
    """

    # helper function for non-blocking I/O
    def makeNonBlocking(fd):
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NDELAY)

    path_to_gmt = getGMTpath()
    com = os.path.join(path_to_gmt, command) + ' ' + arguments
    if verbose:
        print com
    # capture stdout and stderr from command
    child = popen2.Popen3(com, True)         
    infile = child.tochild
    infd = infile.fileno()
    outfile = child.fromchild 
    outfd = outfile.fileno()
    errfile = child.childerr
    errfd = errfile.fileno()
    # don't deadlock!
    makeNonBlocking(outfd)            
    makeNonBlocking(errfd)
    outdata = StringIO()
    errdata = StringIO()
    outeof = erreof = 0
    chunksize = 1000
    i=0
    written = False
    while 1:
        if infile.closed:
            ready = select.select([outfd,errfd],[],[]) # wait for input
        else:
            ready = select.select([outfd,errfd],[infd],[]) # wait for input
        if outfd in ready[0]:
	    outchunk = outfile.read()
	    if outchunk == '': outeof = 1
	    outdata.write('%s'%outchunk)
	if errfd in ready[0]:
            error = True
	    errchunk = errfile.read()
	    if errchunk == '': erreof = 1
	    errdata.write('%s'%errchunk)
        if not infile.closed:
            if infd in ready[1]:
                if not written:
                    grid.write(infile)
                    written = True
                else:
                    infile.close()
        if child.poll()>=0: break
    err = child.wait()
    if err != 0: 
	raise RuntimeError, '%s failed w/ exit code %d\n%s' % (command, err, errdata.getvalue())
    if len(errdata.getvalue()) > 0 and err == 0 and warn:
        warnings.warn('%s\n%s' %(command, errdata.getvalue()), RuntimeWarning)
    return outdata.getvalue()


class Defaults(dict):
    """GMT defaults.

    This dictionary contains the current GMT settings"""

    def __init__(self,defaults=None):
        """Initialise GMT default settings.

        Use default settings from dictionary defaults f the optional argument defaults is not None
        otherwise get defaults from gmtdefaults"""
        #initialising directory for modifications
        dict.__init__(self)
        #and the directory for the defaults

        # loading defaults
        if defaults == None:
            self.defaults = {}
            self.__load_defaults()
        else:
            if isinstance(defaults,dict):
                self.defaults = defaults
            else:
                raise TypeError, 'Expected a dictionary'

    def __load_defaults(self):
        defaults = command('gmtdefaults','-L')
        for l in defaults.split('\n'):
            l = l.lstrip()
            if len(l)>0 and l[0]!='#':
                d = l.split('=')
                self.defaults[d[0].strip()]=d[1].strip()
            
    def __setitem__(self,key,val):
        if self.defaults.has_key(key):
            dict.__setitem__(self,key,val)
            command('gmtset','%s %s'%(key,val))
        else:
            print self.defaults
            raise KeyError, key

    def __delitem__(self,key):
        if self.defaults.has_key(key):
            if self.has_key(key):
                dict.__delitem__(self,key)
                command('gmtset','%s %s'%(key,self.defaults[key]))
        else:
            raise KeyError, key

    def Reset(self):
        """D.Reset() -> reset GMT settings to defaults"""

        keys = self.keys()
        for k in keys:
            del self[k]
        
    def GetCurrentItem(self,key):
        """D.GetCurrentItem(key) -> return the current GMT setting for key"""
        try:
            return self.__getitem__(key)
        except KeyError:
            return self.defaults[key]

    def GetCurrentKeys(self):
        """D.GetCurrentKeys() -> return list of keys"""
        return self.defaults.keys()

    def GetCurrentSettings(self):
        """D.GetCurrentSettings() -> return a directory containing all current GMT settings"""

        settings = self.defaults.copy()
        for k in self:
            settings[k] = self.GetCurrentItem(k)
        return settings
            
