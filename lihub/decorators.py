# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Wilson Xu <imwilsonxu@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public  License
# as published by the Free Software Foundation; either version
# 3.0 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program.

from functools import wraps

from flask import abort
from flask.ext.security import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.has_role('admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
