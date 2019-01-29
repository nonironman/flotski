# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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

class Permission(models.Model):
    READ = 'r'
    CREATE = 'c'
    CHANGE = 'h'
    DELETE = 'd'
    ACCESS = (
        (READ, 'read'),
        (CREATE, 'create'),
        (CHANGE, 'change'),
        (DELETE, 'delete'),
    )
    access = models.CharField(choices=ACCESS, max_length=1, unique=True)
    description = models.CharField(max_length=255)

class User(models.Model):
    ACTIVE = 1
    INACTIVE = 0
    USER_STATE = (
        (ACTIVE, 'active'),
        (INACTIVE, 'inactive'),
    )
    username = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    password = models.CharField(max_length=64)
    state = models.PositiveSmallIntegerField(choices=USER_STATE,default=ACTIVE)
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
