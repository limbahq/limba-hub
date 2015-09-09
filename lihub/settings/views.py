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

import os
import hashlib

from datetime import datetime

from flask import Blueprint, render_template, current_app, request, flash
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..user import User
from ..utils import allowed_file, make_dir
from .forms import ProfileForm, PasswordForm
from ..repository import Repository


settings = Blueprint('settings', __name__, url_prefix='/settings')


@settings.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter_by(name=current_user.name).first_or_404()
    form = ProfileForm(obj=user.user_detail,
            email=current_user.email,
            #role_code=current_user.role_code,
            active=current_user.active,
            next=request.args.get('next'))

    if form.validate_on_submit():

        if form.avatar_file.data:
            upload_file = request.files[form.avatar_file.name]
            if upload_file and allowed_file(upload_file.filename):
                # Don't trust any input, we use a random string as filename.
                # or use secure_filename:
                # http://flask.pocoo.org/docs/patterns/fileuploads/

                user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], "user_%s" % user.id)
                current_app.logger.debug(user_upload_dir)

                make_dir(user_upload_dir)
                root, ext = os.path.splitext(upload_file.filename)
                today = datetime.now().strftime('_%Y-%m-%d')
                # Hash file content as filename.
                hash_filename = hashlib.sha1(upload_file.read()).hexdigest() + "_" + today + ext
                user.avatar = hash_filename

                avatar_ab_path = os.path.join(user_upload_dir, user.avatar)
                # Reset file curso since we used read()
                upload_file.seek(0)
                upload_file.save(avatar_ab_path)

        form.populate_obj(user)
        form.populate_obj(user.user_detail)

        db.session.add(user)
        db.session.commit()

        flash('Public profile updated.', 'success')

    return render_template('settings/profile.html', user=user,
            active="profile", form=form)


@settings.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    user = User.query.filter_by(name=current_user.name).first_or_404()
    form = PasswordForm(next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(user)
        user.password = form.new_password.data

        db.session.add(user)
        db.session.commit()

        flash('Password updated.', 'success')

    return render_template('settings/password.html', user=user,
            active="password", form=form)

@settings.route('/repocp', methods=['GET', 'POST'])
@login_required
def repocp():
    user = User.query.filter_by(name=current_user.name).first_or_404()

    repos = Repository.query.filter_by(user=user)

    return render_template('settings/repos.html', user=user,
            active="repocp", repos=repos)
