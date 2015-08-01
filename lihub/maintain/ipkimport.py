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

from ..repository.models import *
from ..extensions import db
from ..utils import get_current_time, REPO_ROOT
from gi.repository import Limba
from gi.repository import AppStream
from hashlib import sha256
import os
import glob
import shutil
import re

class IPKImporter():
    def __init__(self, search_dir):
        self._import_dir = search_dir
        self._asmdata = AppStream.Metadata()
        self._asmdata.set_locale("C")

    def _map_categories(self, cpt):
        xdg_cats = cpt.get_categories()
        if cpt.get_kind() != AppStream.ComponentKind.DESKTOP:
            return [Category.query.filter_by(idname="components").one()]
        if not xdg_cats:
            return [Category.query.filter_by(idname="other").one()]

        cats = list()
        cats.append(Category.query.filter_by(idname="science").one())

        return cats

    def _import_package(self, pkg_fname):
        pkg = Limba.Package()
        pkg.open_file(pkg_fname)

        if pkg.has_embedded_packages():
            print("SKIP: %s" % (pkg_fname))
            return

        pki = pkg.get_info()

        cpt_xml = pkg.get_appstream_data()

        self._asmdata.clear_components()
        self._asmdata.parse_data(cpt_xml)
        cpt = self._asmdata.get_component()

        pkgid = pkg.get_id()
        arch = pki.get_architecture()

        dest_pkgfname = "%s_%s.ipk" % (pkgid, arch)

        cpt_desc = cpt.get_description()
        if not cpt_desc:
            cpt_desc = "<p>A software component</p>"

        # we just accept packages for the master repository for now
        repo_name = "master"
        repo = Repository.query.filter_by(name=repo_name).one()

        repo_pool_path = os.path.join(REPO_ROOT, repo_name, "pool", pkgid[0])
        repo_icons_path = os.path.join(REPO_ROOT, repo_name, "assets", pkg.get_id(), "icons")
        pkg_dest = os.path.join(repo_pool_path, dest_pkgfname)

        pkg_sha256 = None
        f = open(pkg_fname, 'rb')
        with f:
            pkg_sha256 = sha256(f.read()).hexdigest()

        dbcpt = Component(
            cid=cpt.get_id(),
            kind=AppStream.ComponentKind.to_string(cpt.get_kind()),
            name=cpt.get_name(),
            summary=cpt.get_summary(),
            description=cpt_desc,
            developer_name=cpt.get_developer_name(),
            url=cpt.get_url(AppStream.UrlKind.HOMEPAGE),
            xml=cpt_xml,
            repository=repo
            )
        dbcpt.categories = self._map_categories(cpt)
        db.session.add(dbcpt)

        dbpkg = Package(
            name=pki.get_name(),
            version=pki.get_version(),
            fname=pkg_dest,
            architecture=arch,
            sha256sum=pkg_sha256,
            dependencies=pki.get_dependencies(),
            component=dbcpt,
            repository=repo
            )
        db.session.add(dbpkg)

        pkg.extract_appstream_icons(repo_icons_path)

        if not os.path.exists(repo_pool_path):
            os.makedirs(repo_pool_path)
        shutil.copyfile(pkg_fname, pkg_dest)

    def import_packages(self):
        for fname in glob.glob(self._import_dir+"/*.ipk"):
            self._import_package(fname)
        db.session.commit()
