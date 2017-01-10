# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.shortcuts import redirect

from pootle_translationproject.views import TPBrowseView

from .utils import TPExporter


class OfflineTMView(TPBrowseView):

    def get(self, request, *args, **kwargs):
        # TODO check permissions and get TP explicitly
        super(OfflineTMView, self).get()
        exporter = TPExporter(self.tp)
        return redirect(exporter.get_url())
