"""
Copyright(C) 2016, Stamus Networks
Written by Eric Leblond <eleblond@stamus-networks.com>

This file is part of Scirius.

Scirius is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Scirius is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Scirius.  If not, see <http://www.gnu.org/licenses/>.
"""

from django.conf import settings
import tarfile
import tempfile
import shutil
import os
import sys

from dbbackup.dbcommands import DBCommands
from dbbackup.storage.base import BaseStorage, StorageError
from dbbackup.utils import filename_generate

class SCBackup(object):
    def __init__(self):
        self.storage = BaseStorage.storage_factory()
        self.servername = 'db'

    def backup_git_sources(self):
        # Create a tar of the git sources in the target directory
        sys.stdout.write("%s in %s\n" % (settings.GIT_SOURCES_BASE_DIRECTORY, self.directory))
        ts = tarfile.open(os.path.join(self.directory, 'sources.tar'), 'w')
        call_dir = os.getcwd()
        os.chdir(settings.GIT_SOURCES_BASE_DIRECTORY)
        ts.add('.')
        ts.close()
        os.chdir(call_dir)

    def backup_db(self):
        database = settings.DATABASES['default']
        self.dbcommands = DBCommands(database)
        with open(os.path.join(self.directory, 'dbbackup'), 'w') as outputfile:
            self.dbcommands.run_backup_commands(outputfile)

    def run(self):
        self.directory = tempfile.mkdtemp() 
        self.backup_db()
        self.backup_git_sources()
        # create tar archive of dir
        call_dir = os.getcwd()
        os.chdir(self.directory)
        filename = filename_generate('tar.bz2', self.dbcommands.settings.database['NAME'], self.servername)
        outputfile = tempfile.SpooledTemporaryFile()
        ts = tarfile.open(filename, 'w:bz2', fileobj=outputfile)
        ts.add('sources.tar')
        ts.add('dbbackup')
        ts.close()
        self.storage.write_file(outputfile, filename)
        os.chdir(call_dir)
        
class SCRestore(object):
    def __init__(self, filepath = None):
        self.storage = BaseStorage.storage_factory()
        if filepath:
            self.filepath = filepath
        else:
            self.filepath = self.storage.get_latest_backup()
        self.servername = 'db'

    def restore_git_sources(self):
        sys.stdout.write("Restoring to %s from %s\n" % (settings.GIT_SOURCES_BASE_DIRECTORY, self.directory))
        ts = tarfile.open(os.path.join(self.directory, 'sources.tar'), 'r')
        shutil.rmtree(settings.GIT_SOURCES_BASE_DIRECTORY, ignore_errors = True)
        if not os.path.exists(settings.GIT_SOURCES_BASE_DIRECTORY):
            os.mkdir(settings.GIT_SOURCES_BASE_DIRECTORY)
        os.chdir(settings.GIT_SOURCES_BASE_DIRECTORY)
        ts.extractall()

    def restore_db(self):
        database = settings.DATABASES['default']
        self.dbcommands = DBCommands(database)
        filepath = os.path.join(self.directory, 'dbbackup')
        with open(filepath, 'r') as inputfile:
            self.dbcommands.run_restore_commands(inputfile)

    def run(self):
        # extract archive in tmp directory
        inputfile = self.storage.read_file(self.filepath)
        call_dir = os.getcwd()
        ts = tarfile.open(self.filepath, 'r', fileobj=inputfile)
        tmpdir = tempfile.mkdtemp() 
        os.chdir(tmpdir)
        ts.extractall()
        ts.close()
        self.directory = tmpdir
        self.restore_git_sources()
        self.restore_db()
        shutil.rmtree(tmpdir)
        os.chdir(call_dir)

