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

from flask import Blueprint, render_template, send_from_directory, abort
from flask import current_app as APP
from flask.ext.security import login_required, current_user

from ..extensions import db

from .models import Repository


repository = Blueprint('repository', __name__, url_prefix='/repository')


@repository.route('/')
def index():
    return render_template('user/index.html', user=current_user)


@repository.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    repos = Repository.query.filter_by(user=current_user)

    return render_template('repos/manage.html', user=current_user,
            active="repocp", repos=repos)
