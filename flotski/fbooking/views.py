# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Flotski booking system")
