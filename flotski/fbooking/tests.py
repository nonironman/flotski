import datetime

from django.test import TestCase
from models import User, Room, Permission, PermissionToUser, Guest


class ModelTestCase(TestCase):
    users = []
    rooms = []
    permissions = []
    guests = []

    def setUp(self):
        user = User.objects.create(username='mremnev', first_name='maksim', last_name='remnev', password='ChangeMe1')
        self.users.append(user)
        room = Room.objects.create(beds=2, description='two-bed room')
        self.rooms.append(room)
        read_permission = Permission.objects.create(access='R',description="Read access")
        write_permission = Permission.objects.create(access='W',description="Write access")
        update_permission = Permission.objects.create(access='U',description="Update access")
        delete_permission = Permission.objects.create(access='D',description="Delete access")
        self.permissions.extend([read_permission, write_permission, update_permission, delete_permission])

        guest_1 = Guest.objects.create(first_name="Ichkebek", last_name="Tiger", passport='12345678', birthdate=datetime.date(1967,02,12))
        self.guests.append(guest_1)

# Users
    def test_add_user(self):
        pass

    def test_remove_user(self):
        pass

    def test_update_user(self):
        pass
# Permissions
    def test_add_permission(self):
        pass

    def test_remove_permission(self):
        pass

    def test_update_permission(self):
        pass

# Permission To user
    def test_assign_existing_permissions_to_user(self):
        for user in self.users:
            for permission in self.permissions:
                PermissionToUser.objects.create(user_id=user, permission_id=permission)

    def test_assign_duplicated_permissions_to_user(self):
        pass

    def test_add_duplicate_user_to_permission_to_uesr(self):
        pass

    def test_assign_non_existing_permission_to_user(self):
        non_existing_permission = Permission(access='Z', description='not saved permission')
        try:
            for user in self.users:
                PermissionToUser.objects.create(user_id=user, permission_id=non_existing_permission)
        except ValueError as e:
            print type(e)

# Rooms
    def test_add_room(self):
        pass

    def test_remove_room(self):
        pass
    def test_update_room(self):
        pass

# Booking
    def test_create_booking(self):
        pass

    def test_create_booking_with_invalid_user_id(self):
        pass

    def test_create_booking_with_invalid_room_id(self):
        pass

    def test_create_booking_without_start_and_end_dates_specified(self):
        pass

# Guests
    def test_add_guest(self):
        pass
    def test_update_guest(self):
        pass
    def test_remove_guest(self):
        pass

# Guests To Booking
    def add_guest_to_existing_booking(self):
        pass
    def add_guests_to_non_existing_booking(self):
        pass
    def remove_guests_from_booking(self):
        pass