# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from pootle.core.delegate import url_patterns
from pootle.core.plugin import provider

from .urls import urlpatterns


@provider(url_patterns)
def offline_tm_url_provider(**kwargs_):
    return dict(offline_tm=urlpatterns)
