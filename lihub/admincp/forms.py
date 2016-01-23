# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Matthias Klumpp <mak@debian.org>
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

from flask.ext.wtf import Form
from wtforms import HiddenField, SubmitField, RadioField, DateField, BooleanField
from wtforms.validators import AnyOf

class UserForm(Form):
    next = HiddenField()
    #role_code = RadioField(u"Role", [AnyOf([str(val) for val in USER_ROLE.keys()])],
    #        choices=[(str(val), label) for val, label in USER_ROLE.items()])
    active = BooleanField(u"Active")
    # A demo of datepicker.
    created_time = DateField(u'Created time')
    submit = SubmitField(u'Save')

class GlobalSettingsForm(Form):
    next = HiddenField()
    allow_registration = BooleanField(u"Allow user registrations")
    submit = SubmitField(u'Save')
