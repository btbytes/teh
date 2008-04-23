#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Pradeep Gowda on 2008-04-23.
Copyright (c) 2008 Yashotech. All rights reserved.
"""

import sys
import os
import re


def slugify(string):
    '''
    >>> slugify("Hello world !")
    'hello_world'
    '''
    string = re.sub('\s+', '_', string)
    string = re.sub('[^\w.-]', '', string)
    return string.strip('_.- ').lower()
    
def _test():
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test()

