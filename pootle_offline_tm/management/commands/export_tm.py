# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'pootle.settings'

from pootle_app.management.commands import PootleCommand

from ...utils import TPExporter


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
        exporter = TPExporter(translation_project)
        if not exporter.has_changes() and not overwrite:
            self.stdout.write(
                'Translation project (%s) has not been changed.' %
                translation_project)
            return False

        filename = exporter.export()
        self.stdout.write('File "%s" has been saved.' % filename)

        return False
