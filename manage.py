#!/usr/bin/env python
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

from flask.ext.script import Manager

from lihub import create_app
from lihub.extensions import db
from lihub.user import User, UserDetail, user_datastore
from lihub.repository import Repository, Category, RepoFlag
from lihub.utils import MALE
from lihub.config import DefaultConfig


app = create_app()
manager = Manager(app)


@manager.command
def run():
    """Run on local machine."""

    app.run()


@manager.command
def initdb():
    """Init/reset database."""

    db.drop_all()
    db.create_all()

    admin = user_datastore.create_user(
                name=u'admin',
                email=u'admin@example.com',
                password=u'123456',
                pgpfpr=u'0000000000000000DEADBEEF0000000000000000',
                active=True,
                user_detail=UserDetail(
                sex_code=MALE,
                url=u'http://admin.example.com',
                location=u'Berlin',
                bio=u'Master of the Universe!'))
    admin_role = user_datastore.create_role(name='admin', description="The masters of each and everything.")
    user_datastore.add_role_to_user(admin, admin_role)

    master_repo = Repository(
            name=u'master',
            user=admin,
            toplevel=True
            )
    master_nonfree_repo = Repository(
            name=u'nonfree',
            user=admin,
            toplevel=True,
            flag=RepoFlag.NONFREE
            )
    db.session.add(master_repo)
    db.session.add(master_nonfree_repo)

    db.session.add(Category(idname="office",        name="Office", description="Office software"))
    db.session.add(Category(idname="tools",         name="Tools", description="Helpful utilities"))
    db.session.add(Category(idname="customization", name="Customization", description="Customize your OS"))
    db.session.add(Category(idname="development",   name="Development", description="Software development"))
    db.session.add(Category(idname="graphics",      name="Graphics", description="Graphics & design"))
    db.session.add(Category(idname="internet",      name="Internet", description="Internet & network"))
    db.session.add(Category(idname="science",       name="Science", description="Scientific software"))
    db.session.add(Category(idname="multimedia",    name="Multimedia", description="Audio & Video"))
    db.session.add(Category(idname="games",         name="Games", description="A nice description"))
    db.session.add(Category(idname="system",        name="System", description="System tools"))
    db.session.add(Category(idname="other",         name="Other", description="Miscellaneous software"))
    db.session.add(Category(idname="components",    name="Technical Items", description="Technical items"))

    db.session.commit()


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
