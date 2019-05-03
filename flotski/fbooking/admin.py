# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from fbooking.models import Room, Booking, Guest, GuestToBooking

admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Guest)
admin.site.register(GuestToBooking)
