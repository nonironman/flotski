# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import models as auth_models
from django.db import models

class Room(models.Model):
    ACTIVE = 1
    INACTIVE = 0
    ROOM_STATE = (
        (ACTIVE, 'active'),
        (INACTIVE, 'inactive'),
    )
    description = models.CharField(max_length=255, null=True)
    beds = models.PositiveSmallIntegerField()
    state = models.PositiveSmallIntegerField(choices=ROOM_STATE, default=ACTIVE)

class Booking(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    user = models.ForeignKey(auth_models.User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255, null=True)

class Guest(models.Model):
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    passport = models.CharField(max_length=15, unique=True)
    birth_date = models.DateField()
    user = models.ForeignKey(auth_models.User, on_delete=models.CASCADE)

class GuestToBooking(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('guest', 'booking')
