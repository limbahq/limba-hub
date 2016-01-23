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
from lihub.repository import Repository, RepoPermission, Category, RepoFlag
from lihub.utils import MALE, OTHER

try:
    from lihub.local_config import DefaultConfig
except:
    from lihub.config import DefaultConfig
    if not os.path.isdir(DefaultConfig.INSTANCE_FOLDER_PATH):
        raise Exception("Tried to load default configuration, but it's path doesn't exist. This is usually a configuration issue, you probably wanted to load a local configuration.")

try:
    from flask_frozen import Freezer
except:
    pass


app = create_app()
manager = Manager(app)


@manager.command
def run():
    """Run on local machine."""

    app.run()


@manager.command
def freeze():
    """Create a static version of the LimbaHub HTML pages."""

    freezer = Freezer(app)
    freezer.freeze()


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
                sex_code=OTHER,
                url=u'http://admin.example.com',
                location=u'Berlin',
                bio=u'Master of the Universe!'))
    admin_role = user_datastore.create_role(name='admin', description="The masters of each and everything.")
    user_role = user_datastore.create_role(name='user', description="A normal, uploading user of the service.")
    user_datastore.add_role_to_user(admin, admin_role)

    user = user_datastore.create_user(
                name=u'matthias',
                email=u'mak@debian.org',
                password=u'sample123',
                pgpfpr=u'0000000000000000D0ABLE00000000000000000',
                active=True,
                user_detail=UserDetail(
                sex_code=MALE,
                url=u'http://blog.tenstral.net',
                location=u'Berlin',
                bio=u'The average guy.'))
    user_datastore.add_role_to_user(user, user_role)

    master_repo = Repository(
            name=u'master',
            user=admin,
            toplevel=True)
    master_nonfree_repo = Repository(
            name=u'nonfree',
            user=admin,
            toplevel=True,
            flag=RepoFlag.NONFREE)
    db.session.add(master_repo)
    db.session.add(master_nonfree_repo)

    master_perm = RepoPermission(user=admin,
                pkgname=u'*',
                repository=master_repo,
                details="Default permissions")
    nonfree_perm = RepoPermission(user=admin,
                pkgname=u'*',
                repository=master_nonfree_repo,
                details="Default permissions")
    db.session.add(master_perm)
    db.session.add(nonfree_perm)

    cat_office    = Category(idname="office",        name="Office", description="Office software")
    cat_tools     = Category(idname="tools",         name="Tools", description="Helpful utilities")
    cat_customize = Category(idname="customization", name="Customization", description="Customize your OS")
    cat_develop   = Category(idname="development",   name="Development", description="Software development")
    cat_graphics  = Category(idname="graphics",      name="Graphics", description="Graphics & design")
    cat_network   = Category(idname="network",       name="Network", description="Internet & network")
    cat_science   = Category(idname="science",       name="Science", description="Scientific software")
    cat_educate   = Category(idname="education",     name="Education", description="Education")
    cat_media     = Category(idname="multimedia",    name="Multimedia", description="Audio & Video")
    cat_games     = Category(idname="games",         name="Games", description="Games")
    cat_system    = Category(idname="system",        name="System", description="System tools")
    cat_other     = Category(idname="other",         name="Other", description="Miscellaneous software")
    cat_tech      = Category(idname="components",    name="Technical Items", description="Technical items")

    db.session.add(cat_office)
    db.session.add(cat_tools)
    db.session.add(cat_customize)
    db.session.add(cat_develop)
    db.session.add(cat_graphics)
    db.session.add(cat_network)
    db.session.add(cat_science)
    db.session.add(cat_educate)
    db.session.add(cat_media)
    db.session.add(cat_games)
    db.session.add(cat_system)
    db.session.add(cat_other)
    db.session.add(cat_tech)

    db.session.add(Category(idname="arcade", name="Arcade", description="Arcade Games", parent=cat_games))

    db.session.commit()


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
