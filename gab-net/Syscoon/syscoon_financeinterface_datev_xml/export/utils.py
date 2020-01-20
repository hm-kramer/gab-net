# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import os
from jinja2 import Environment, FileSystemLoader
from functools import wraps


jenv = Environment(loader=FileSystemLoader(
    os.path.join(os.path.dirname(__file__))))


def iso_dtime_date(dtime):
    return dtime.split(' ')[0]


def flip(func):
    """
    :param func: function
    :returns: function that accepts positional
              arguments in reverse order

    Most usefull for cases when positional arguments
    are not in the needed order so that functools.partial
    can be used to "freeze" them.

    Example:

    is_int = partial(flip(isinstance), int)

    Can be used as a decorator aswell but doesn't
    really make sense :).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        args = tuple(reversed(args))
        return func(*args, **kwargs)
    return wrapper
