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

from flask import Blueprint, render_template, request, flash
from flask.ext.login import login_required

from ..extensions import db
from ..decorators import admin_required

from ..user import User
from .forms import UserForm, GlobalSettingsForm
from .models import GlobalSettings


admincp = Blueprint('admincp', __name__, url_prefix='/admincp')


@admincp.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def index():
    conf = GlobalSettings.query.first()
    if not conf:
        conf = GlobalSettings()
    form = GlobalSettingsForm(obj=conf, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(conf)

        db.session.add(conf)
        db.session.commit()

        flash('Global settings updated.', 'success')

    return render_template('admincp/index.html', conf=conf, form=form, active='index')


@admincp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admincp/users.html', users=users, active='users')


@admincp.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    form = UserForm(obj=user, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(user)

        db.session.add(user)
        db.session.commit()

        flash('User updated.', 'success')

    return render_template('admincp/user.html', user=user, form=form)
