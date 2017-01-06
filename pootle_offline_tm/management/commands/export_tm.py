# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'pootle.settings'

from django.conf import settings
from django.core.cache import caches

from translate.storage import tmx

from pootle_app.management.commands import PootleCommand
from pootle_store.constants import TRANSLATED


cache = caches['offline_tm']


class Command(PootleCommand):
    help = "Export TM from Pootle to .tmx files."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--overwrite",
            action="store_true",
            default=False,
            help=u"Overwrite already exported files.",
        )

    def handle_translation_project(self, translation_project, **options):
        """
        :return: flag if child stores should be handled
        """
        overwrite = options.get('overwrite', False)
        tp_revision_cache_key = 'revision:%s' % translation_project.pootle_path
        tp_cached_revision = cache.get(tp_revision_cache_key, 0)
        tp_max_unit_revision = translation_project.data_tool.max_unit_revision
        if tp_cached_revision == tp_max_unit_revision and not overwrite:
            self.stdout.write(
                'Translation project (%s) has not been changed.' %
                translation_project)
            return False

        source_language = translation_project.project.source_language.code
        target_language = translation_project.language.code
        stores = translation_project.stores.live()

        tmxfile = tmx.tmxfile()
        for store in stores.filter().iterator():
            for unit in store.units.filter(state=TRANSLATED):
                tmxfile.addtranslation(unit.source, source_language,
                                       unit.target, target_language,
                                       unit.developer_comment)

        directory = os.path.join(settings.OFFLINE_TM_DIR,
                                 translation_project.language.code)
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = "".join([translation_project.project.fullname,
                            '.', translation_project.language.code, '.tmx'])
        filename = os.path.join(directory, filename)
        with open(filename, 'wb') as output:
            tmxfile.serialize(output)
            self.stdout.write('File "%s" has been saved.' % filename)

        cache.set(tp_revision_cache_key, tp_max_unit_revision)

        return False
