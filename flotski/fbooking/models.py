# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Room(models.Model):
    description = models.CharField(max_length=255, null=True)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255, null=True)

class Guest(models.Model):
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    passport = models.CharField(max_length=15, unique=True)
    birth_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class PermissionToUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'permission')

class GuestToBooking(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('guest', 'booking')
