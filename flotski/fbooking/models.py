# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Room(models.Model):
    VACANT = 'V'
    OCCUPIED = 'O'
    MAINTENANCE = 'M'
    ROOM_STATE_CHOICES = (
        (VACANT, 'Vacant'),
        (OCCUPIED, 'Occupied'),
        (MAINTENANCE, 'Maintenance')
    )
    description = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=1, choices=ROOM_STATE_CHOICES, default=VACANT)
    beds = models.IntegerField()

class Permission(models.Model):
    access = models.CharField(max_length=1, unique=True)
    description = models.CharField(max_length=255)

class User(models.Model):
    username = models.CharField(max_length=15)
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    password = models.CharField(max_length=64)
    description = models.CharField(max_length=255, null=True)

class Booking(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True)

class Guest(models.Model):
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    passport = models.CharField(max_length=15, unique=True)
    birthdate = models.DateField()

class PermissionToUser(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    permission_id = models.ForeignKey(Permission, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user_id', 'permission_id')

class GuestToBooking(models.Model):
    guest_id = models.ForeignKey(Guest, on_delete=models.CASCADE)
    booking_id = models.ForeignKey(Booking, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('guest_id', 'booking_id')
