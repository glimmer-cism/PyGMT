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

"""Utility functions."""

__all__=['round_up','round_down','interval']

import math

def round_up(value, factors=[1.,2.,5.,10.]):
    """Round upwards to some factor of ten.

    value: the value to be rounded up
    factors: the list of factors of ten to be rounded up to
    """

    if value < 0:
        return -round_down(-value)
    if value == 0.:
        return 0.

    pow10 = 10**math.floor(math.log10(value))
    interval = pow10
    difference = abs(interval - value)
    for f in factors:
        if (abs(f*pow10-interval) < difference) or (interval < value):
            interval = f*pow10
            difference = abs(interval - value)
    return interval

def round_down(value, fractions=[1.,0.5,0.2,0.1]):
    """Round downwards to some fraction of ten.

    value: the value to be rounded up
    fractions: the list of fractions of ten to be rounded down to
    """

    if value < 0:
        return -round_up(-value)
    if value == 0:
        return 0.

    pow10 = 10**math.ceil(math.log10(value))
    interval = pow10
    difference = abs(interval - value)
    for f in fractions:
        if (abs(f*pow10-interval) < difference) or (interval > value):
            interval = f*pow10
            difference = abs(interval - value)
    return interval

def interval(interval):
    """Expand interval to next fraction/multiple of 10.

    see also round_up and round_down
    """
    
    return [round_down(interval[0]),round_up(interval[1])]
