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
from ..utils import run_command


class DscFileException(Exception):
    pass


class DSCFile:
    def __init__(self):
        self.content = dict()
        self.fname = ""

    def open(self, fname):
        with open(fname) as f:
            lines = f.readlines()

        self.fname = fname

        # we are really relaxed about the file format here, as long as we can
        # get data out, it's fine
        self.content = dict()
        current_key = None
        current_value = None
        for line in lines:
            if line == "-----BEGIN PGP SIGNATURE-----\n":
                break
            if line.startswith(" "):
                if current_key:
                    current_value += "\n"+line.strip()
                    continue
            elif current_key:
                self.content[current_key] = current_value
                current_value = None
                current_key = None
            if ':' in line:
                parts = line.split(':', 2)
                current_key = parts[0].strip()
                current_value = parts[1].strip()
        if current_key:
            self.content[current_key] = current_value


    def get_val(self, key):
        return self.content.get(key)


    def get_files(self):
        files_raw = self.get_val("Files")
        files = dict()

        for line in files_raw.split("\n"):
            if not ' ' in line:
                continue
            parts = line.split(" ", 2)
            files[parts[0].strip()] = parts[1].strip()
        return files


    def validate(self, gpghome):
        """
        Validate the GPG signature of a .dsc file.
        """

        keyring = os.path.join(gpghome, "keyring.gpg")

        (gpg_output, gpg_output_stderr, exit_status) = run_command([
            "gpg", "--batch", "--status-fd", "1",
            "--no-default-keyring", "--keyring", keyring,
            "--verify", self.fname,
        ])

        if exit_status == -1:
            raise DscFileException(
                "Unknown problem while verifying signature")

        if gpg_output.count('[GNUPG:] GOODSIG'):
            pass
        elif gpg_output.count('[GNUPG:] BADSIG'):
            raise DscFileException("Bad signature")
        elif gpg_output.count('[GNUPG:] ERRSIG'):
            raise DscFileException("Error verifying signature")
        elif gpg_output.count('[GNUPG:] NODATA'):
            raise DscFileException("No signature on")
        else:
            raise DscFileException(
                "Unknown problem while verifying signature"
            )

        key = None
        for line in gpg_output.split("\n"):
            if line.startswith('[GNUPG:] VALIDSIG'):
                key = line.split()[2]
        return key
