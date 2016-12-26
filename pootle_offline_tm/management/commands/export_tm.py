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

from translate.storage import tmx

from pootle_app.management.commands import PootleCommand


class Command(PootleCommand):
    help = "Export TM from Pootle to .tmx files."

    def handle_translation_project(self, translation_project, **options):
        """
        :return: flag if child stores should be handled
        """
        stores = translation_project.stores.live()
        for store in stores.iterator():
            tmxfile = tmx.tmxfile()
            source_language = translation_project.project.source_language.code
            target_language = translation_project.language.code
            for unit in store.units:
                tmxfile.addtranslation(unit.source, source_language,
                                       unit.target, target_language,
                                       unit.developer_comment)

            filename = os.path.join(settings.OFFLINE_TM_DIR, store.name + '.tmx')
            with open(filename, 'wb') as output:
                tmxfile.serialize(output)

        return False
