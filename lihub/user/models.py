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
from sqlalchemy import Column, types
from sqlalchemy.ext.mutable import Mutable
from flask import current_app
from flask.ext.security import Security, UserMixin, RoleMixin, SQLAlchemyUserDatastore
from flask.ext.security.utils import encrypt_password, verify_password

from ..extensions import db
from ..utils import make_dir, get_current_time, SEX_TYPE, STRING_LEN, run_command
from .constants import DEFAULT_USER_AVATAR
from ..repository.models import Repository


roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))

class UserDetail(db.Model):

    __tablename__ = 'user_details'

    id = Column(db.Integer, primary_key=True)

    url = Column(db.String(STRING_LEN))
    location = Column(db.String(STRING_LEN))
    bio = Column(db.String(STRING_LEN))

    sex_code = db.Column(db.Integer)

    @property
    def sex(self):
        return SEX_TYPE.get(self.sex_code)

    created_time = Column(db.DateTime, default=get_current_time)


class Role(db.Model, RoleMixin):

    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class KeyImportException(Exception):
    pass


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(STRING_LEN), nullable=False, unique=True)
    email = Column(db.String(STRING_LEN), nullable=False, unique=True)
    created_time = Column(db.DateTime, default=get_current_time)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    pgpfpr = Column(db.String(STRING_LEN), unique=False)

    avatar = Column(db.String(STRING_LEN))

    user_detail_id = Column(db.Integer, db.ForeignKey("user_details.id"))
    user_detail = db.relationship("UserDetail", uselist=False, backref="user")


    _password = Column('password', db.String(STRING_LEN), nullable=False)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = encrypt_password(password)
    # Hide password encryption by exposing password field only.
    password = db.synonym('_password',
                          descriptor=property(_get_password,
                                              _set_password))

    def check_password(self, password):
        if self.password is None:
            return False
        return verify_password(self.password, password)


    # ================================================================
    # Class methods

    @classmethod
    def authenticate(cls, login, password):
        user = cls.query.filter(db.or_(User.name == login, User.email == login)).first()

        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False

        return user, authenticated

    @classmethod
    def search(cls, keywords):
        criteria = []
        for keyword in keywords.split():
            keyword = '%' + keyword + '%'
            criteria.append(db.or_(
                User.name.ilike(keyword),
                User.email.ilike(keyword),
            ))
        q = reduce(db.and_, criteria)
        return cls.query.filter(q)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first_or_404()

    def check_name(self, name):
        return User.query.filter(db.and_(User.name == name, User.email != self.id)).count() == 0

    @property
    def gpghome(self):
        root = current_app.config['USERS_FOLDER']
        path = os.path.join(root, self.name, "gpg")
        make_dir(path)
        return path


    def import_pgpkey(self, fingerprint):
        """
        Import an OpenPGP key
        """

        keyring = os.path.join(self.gpghome, "keyring.gpg")

        # FIXME: Delete old key (or even the whole keyring?)

        (gpg_output, gpg_output_stderr, exit_status) = run_command([
            "gpg", "--batch", "--status-fd", "1",
            "--no-default-keyring", "--keyring", keyring,
            "--recv-key", fingerprint,
        ])

        if exit_status == -1:
            raise KeyImportException(
                "Unknown problem while importing key.")

        if gpg_output.count('[GNUPG:] IMPORTED') and gpg_output.count('[GNUPG:] IMPORT_OK'):
            self.pgpfpr = fingerprint
        else:
            raise KeyImportException(
                "Unknown problem while importing key."
            )


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
