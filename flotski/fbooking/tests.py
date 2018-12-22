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
        user = User.objects.get(username=username)
        user.delete()
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            raise e
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


class PermissionModelTestCase(TestCase):

    def _prepare_permission_object(self, access, description):
        permission = Permission()
        permission.access = access
        permission.description = description
        return permission

    @parameterized.expand([
        ['w', 'write access'],
        ['r', 'read access'],
        ['u', 'update access'],
        ['d', 'delete access']
    ])
    def test_add_permission(self, access, description):
        permission = self._prepare_permission_object(access,description)
        permission.save()
        permission.refresh_from_db()
        self.assertEqual((permission.access, permission.description), (access, description),
                         "Specified permission was not saved properly")


    @parameterized.expand([
        ['w', None],
        [None, 'delete access']
    ])
    def test_add_invalid_permission(self, access, description):
        permission = self._prepare_permission_object(access, description)
        try:
            permission.save()
        except IntegrityError:
            pass
        except Exception as e:
            raise e
        else:
            self.assertTrue(False, "Invalid permission was saved or exception was not thrown")

    def test_add_duplicate_permission(self):
        write_permission_1 = self._prepare_permission_object("w", "write access 1")
        write_permission_2 = self._prepare_permission_object("w", "write access 2")
        write_permission_1.save()
        try:
            write_permission_2.save()
        except IntegrityError:
            pass
        except Exception as e:
            raise e
        else:
            self.assertTrue(False,"Duplicated permission was added or exception wasn't thrown")

    def test_remove_permission(self):
        access, description = "s", "test permission"
        permission = self._prepare_permission_object(access,description)
        permission.save()
        permission = Permission.objects.get(access=access)
        permission.delete()
        try:
            Permission.objects.get(access=access)
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            raise e
        else:
            self.assertEqual(False, "Removed permission was found or exception wasn't thrown")

    def test_update_permission(self):
        permission = self._prepare_permission_object('u', "update permission")
        permission.save()
        prev_permission_id, prev_permission_access, prev_permission_desc = (permission.id, permission.access, permission.description)
        new_access, new_description = "X", "execute permission"
        permission.access = new_access
        permission.description = new_description
        permission.save()
        permission.refresh_from_db()
        self.assertEqual(prev_permission_id, permission.id, "Permission id was updated")
        self.assertEqual((permission.access, permission.description), (new_access, new_description),
                         "Permission was not updated properly")

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
