import datetime

from django.db import IntegrityError
from parameterized import parameterized
from django.test import TestCase
from models import User, Room, Permission, PermissionToUser, Guest
from django.core.exceptions import ObjectDoesNotExist


class UserModelTestCase(TestCase):
    def _prepare_test_user_object(self, username, password, first_name, last_name, description=None):
        user = User()
        user.username = username
        user.password = password
        user.first_name = first_name
        user.last_name = last_name
        user.description = description
        return user

    @parameterized.expand([
        ["valid_tuser1", "change_Me_1", "TestUserFirstName", "TestUserLastName", "test description"],
        ["valid_tuser2", "change_Me_2", "TestUserFirstName", "TestUserLastName", None],
    ])
    def test_add_valid_user(self, username, password, first_name, last_name, description):
        user = self._prepare_test_user_object(username, password, first_name, last_name, description)
        user.save()

        created_user = User.objects.get(username=username)
        self.assertEqual((created_user.username, created_user.password, created_user.first_name,
                          created_user.last_name, created_user.description),
                         (username, password, first_name, last_name, description),
                         "Saved user data doesn't match expected")

    @parameterized.expand([
        [None, "change_Me_1", "TestUserFirstName", "TestUserLastName", "test description"],
        ["invalid_tuser2", None, "TestUserFirstName", "TestUserLastName", None],
        ["invalid_tuser3", "change_Me_3", None, "TestUserLastName", None],
        ["invalid_tuser4", "change_Me_4", "TestUserFirstName", None, None],
    ])
    def test_add_valid_user(self, username, password, first_name, last_name, description):
        user = self._prepare_test_user_object(username, password, first_name, last_name, description)
        try:
            user.save()
        except Exception as e:
            self.assertIsInstance(e, IntegrityError, "User without required data was successfully saved")
        else:
            self.assertTrue(False, "User was saved or exception was not thrown")

    def test_remove_user(self):
        username = "user_to_remove"
        user = self._prepare_test_user_object(username, "", "", "", None)
        user.save()
        user.delete()
        try:
            User.objects.get(username=username)
        except Exception as e:
            self.assertIsInstance(e, ObjectDoesNotExist, "Found removed user row in DB")
        else:
            self.assertTrue(False, "User was found or exception was not thrown")

    def test_update_user(self):
        username = "user_to_update"
        user = self._prepare_test_user_object(username, "", "", "", None)
        user.save()
        prev_user_id = user.id
        new_properties = ("new_user_name", "new_first_name", "new_last_name", "description")
        user.username, user.first_name, user.last_name, user.description = new_properties
        user.save()
        user.refresh_from_db()
        self.assertEqual(user.id, prev_user_id, "User id was changed")
        self.assertEqual((user.username, user.first_name, user.last_name, user.description),
                         new_properties, "User was not updated properly")


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
        read_permission = Permission.objects.create(access='R', description="Read access")
        write_permission = Permission.objects.create(access='W', description="Write access")
        update_permission = Permission.objects.create(access='U', description="Update access")
        delete_permission = Permission.objects.create(access='D', description="Delete access")
        self.permissions.extend([read_permission, write_permission, update_permission, delete_permission])

        guest_1 = Guest.objects.create(first_name="Ichkebek", last_name="Tiger", passport='12345678',
                                       birthdate=datetime.date(1967, 02, 12))
        self.guests.append(guest_1)

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
