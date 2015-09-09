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
from ..utils import get_current_time
from gi.repository import Limba
from gi.repository import AppStream
import os
import glob
import shutil
import gzip

def safe_move_file(old_fname, new_fname):
    if not os.path.isfile(old_fname):
        return
    if os.path.isfile(new_fname):
        os.remove(new_fname)
    os.rename(old_fname, new_fname)

class IndicesUpdater():
    def __init__(self):
        pass

    def rebuild_index_for_repo(self, repo):

        idx = dict()

        for pkg in repo.packages:
            xml = pkg.component.xml
            if not xml:
                continue

            pki = Limba.PkgInfo()
            pki.set_name(pkg.name)
            pki.set_appname(pkg.component.name)
            pki.set_version(pkg.version)
            pki.set_checksum_sha256(pkg.sha256sum)
            pki.set_repo_location("???")
            if pkg.dependencies:
                pki.set_dependencies(pkg.dependencies)

            if not idx.get(pkg.architecture):
                idx[pkg.architecture] = dict()
            if not idx[pkg.architecture].get('asdata'):
                idx[pkg.architecture]['asdata'] = AppStream.Metadata()
            if not idx[pkg.architecture].get('ipk'):
                idx[pkg.architecture]['ipk'] = Limba.PkgIndex()
            idx[pkg.architecture]['asdata'].parse_data(xml)
            idx[pkg.architecture]['ipk'].add_package(pki)

        for arch, idx in idx.items():
            repo_index_path = os.path.join(repo.root_dir, "indices", arch)
            if not os.path.exists(repo_index_path):
                os.makedirs(repo_index_path)

            asdata_fname = os.path.join(repo_index_path, "Metadata.xml.gz")
            ipkidx_fname = os.path.join(repo_index_path, "Index.gz")

            idx['asdata'].save_distro_xml(asdata_fname+".new")
            idx['ipk'].save_to_file(ipkidx_fname+".new")
            safe_move_file(asdata_fname+".new", asdata_fname)
            safe_move_file(ipkidx_fname+".new", ipkidx_fname)

    def rebuild_indices(self):
        repos = Repository.query.all()
        for repo in repos:
            self.rebuild_index_for_repo(repo)
