# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import os

from io import BytesIO
from zipfile import ZipFile

from django.conf import settings
from django.utils.functional import cached_property

from translate.storage import tmx

from pootle.core.delegate import revision
from pootle_store.constants import TRANSLATED


class TPExporter(object):

    def __init__(self, context):
        self.context = context

    @property
    def exported_revision(self):
        return revision.get(self.context.__class__)(
            self.context).get(key="pootle.offline.tm")

    @cached_property
    def revision(self):
        return revision.get(self.context.__class__)(
            self.context).get(key="stats")

    def relative_path(self):
        return "%s/%s" % (
            self.context.language.code,
            self.filename)

    def get_url(self):
        return "%s/%s" % (settings.MEDIA_URL, self.relative_path)

    def update_exported_revision(self):
        revision.get(self.context.__class__)(
            self.context).set(keys=["pootle.offline.tm"], value=self.revision)

    def has_changes(self):
        return self.revision == self.exported_revision

    @property
    def directory(self):
        return os.path.join(settings.OFFLINE_TM_DIR,
                            self.context.language.code)

    @property
    def filename(self):
        filename = self.context.project.fullname.replace(' ', '_')
        filename = ".".join([filename, self.revision, 'tmx'])
        return "%s.zip" % filename

    @property
    def abs_filepath(self):
        return os.path.join(self.directory, self.filename)

    def export(self):
        source_language = self.context.project.source_language.code
        target_language = self.context.language.code
        stores = self.context.stores.live()

        tmxfile = tmx.tmxfile()
        for store in stores.filter().iterator():
            for unit in store.units.filter(state=TRANSLATED):
                tmxfile.addtranslation(unit.source, source_language,
                                       unit.target, target_language,
                                       unit.developer_comment)

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        bs = BytesIO()
        tmxfile.serialize(bs)
        with open(self.abs_filepath, "wb") as f:
            with ZipFile(f, "w") as zf:
                zf.writestr(self.filename, bs.getvalue())

        self.update_exported_revision()

        return self.abs_filepath

