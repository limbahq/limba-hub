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

from flask import Markup

from flask.ext.wtf import Form
from wtforms import (ValidationError, HiddenField, BooleanField, TextField,
        PasswordField, SubmitField)
from wtforms.validators import Required, Length, EqualTo, Email
from flask.ext.wtf.html5 import EmailField

from ..user import User
from ..utils import (PASSWORD_LEN_MIN, PASSWORD_LEN_MAX,
        USERNAME_LEN_MIN, USERNAME_LEN_MAX)


class LoginForm(Form):
    next = HiddenField()
    login = TextField(u'Username or email', [Required()])
    password = PasswordField('Password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class SignupForm(Form):
    next = HiddenField()
    email = EmailField(u'Email', [Required(), Email()],
            description=u"What's your email address?")
    password = PasswordField(u'Password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
            description=u'%s characters or more! Be tricky.' % PASSWORD_LEN_MIN)
    name = TextField(u'Choose your username', [Required(), Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)],
            description=u"Don't worry. you can change it later.")
    agree = BooleanField(u'Agree to the ' +
        Markup('<a target="blank" href="/terms">Terms of Service</a>'), [Required()])
    submit = SubmitField('Sign up')

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first() is not None:
            raise ValidationError(u'This username is taken')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError(u'This email is taken')


class RecoverPasswordForm(Form):
    email = EmailField(u'Your email', [Email()])
    submit = SubmitField('Send instructions')


class ChangePasswordForm(Form):
    activation_key = HiddenField()
    password = PasswordField(u'Password', [Required()])
    password_again = PasswordField(u'Password again', [EqualTo('password', message="Passwords don't match")])
    submit = SubmitField('Save')


class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(u'Password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    submit = SubmitField('Reauthenticate')


class CreateProfileForm(Form):
    name = TextField(u'Choose your username', [Required(), Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)],
            description=u"Don't worry. you can change it later.")
    email = EmailField(u'Email', [Required(), Email()], description=u"What's your email address?")
    password = PasswordField(u'Password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
            description=u'%s characters or more! Be tricky.' % PASSWORD_LEN_MIN)
    submit = SubmitField(u'Create Profile')

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first() is not None:
            raise ValidationError(u'This username is taken.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError(u'This email is taken.')
