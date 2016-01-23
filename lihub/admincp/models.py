# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Matthias Klumpp <mak@debian.org>
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

import os
from sqlalchemy import Column, Table, types
from sqlalchemy.ext.mutable import Mutable
from flask import current_app

from ..extensions import db

class GlobalSettings(db.Model):

    __tablename__ = 'global_settings'

    id = Column(db.Integer, primary_key=True)
    allow_registration = Column(db.Boolean())
