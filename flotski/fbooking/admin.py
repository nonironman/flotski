# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from fbooking.models import User, Room, Permission, Booking, Guest, PermissionToUser, GuestToBooking

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Permission)
admin.site.register(Booking)
admin.site.register(Guest)
admin.site.register(PermissionToUser)
admin.site.register(GuestToBooking)
