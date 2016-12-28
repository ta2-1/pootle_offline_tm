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

    def _export_by_stores(self, translation_project, tp_max_unit_revision):
        source_language = translation_project.project.source_language.code
        target_language = translation_project.language.code
        stores = translation_project.stores.live()

        for store in stores.filter(state=TRANSLATED).iterator():
            revision_cache_key = 'revision:%s' % store.pootle_path
            cached_revision = cache.get(revision_cache_key)
            store_max_unit_revision = store.data_tool.max_unit_revision

            if cached_revision == store_max_unit_revision:
                continue

            # store might be updated after we stored tp_max_unit_revision
            tp_max_unit_revision = max(tp_max_unit_revision,
                                       store_max_unit_revision)

            tmxfile = tmx.tmxfile()
            for unit in store.units:
                tmxfile.addtranslation(unit.source, source_language,
                                       unit.target, target_language,
                                       unit.developer_comment)

            filename = '__'.join(store.pootle_path.split('/') + [store.name])
            filename = os.path.join(settings.OFFLINE_TM_DIR, filename + '.tmx')
            with open(filename, 'wb') as output:
                tmxfile.serialize(output)

        return tp_max_unit_revision

    def handle_translation_project(self, translation_project, **options):
        """
        :return: flag if child stores should be handled
        """
        tp_revision_cache_key = 'revision:%s' % translation_project.pootle_path
        tp_cached_revision = cache.get(tp_revision_cache_key, 0)
        tp_max_unit_revision = translation_project.data_tool.max_unit_revision
        if tp_cached_revision == tp_max_unit_revision:
            self.stdout.write(
                'Translation project (%s) has been changed.' %
                translation_project)
            return False

        tp_max_unit_revision = self._export_by_stores(
            translation_project,
            tp_max_unit_revision)

        cache.set(tp_revision_cache_key, tp_max_unit_revision)

        return False
