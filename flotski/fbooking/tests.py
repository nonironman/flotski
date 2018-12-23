import datetime
from copy import copy

from django.db import IntegrityError, connection, transaction
from parameterized import parameterized
from django.test import TestCase
from models import User, Room, Permission, PermissionToUser, Guest, Booking
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
            raise AssertionError("Invalid permission was saved or exception was not thrown")

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
            raise AssertionError("Duplicated permission was added or exception wasn't thrown")

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
            raise AssertionError("Removed permission was found or exception wasn't thrown")

    def test_update_permission(self):
        permission = self._prepare_permission_object('u', "update permission")
        permission.save()
        prev_permission_id, prev_permission_access, prev_permission_desc = (permission.id, permission.access, permission.description)
        new_access, new_description = "X", "execute permission"
        permission.access = new_access
        permission.description = new_description
        permission.save()
        self.assertEqual(prev_permission_id, permission.id, "Permission id was updated")
        self.assertEqual((permission.access, permission.description), (new_access, new_description),
                         "Permission was not updated properly")

class RoomModelTestCase(TestCase):
    def _prepare_room_object(self, beds, description):
        room = Room()
        room.beds = beds
        room.description = description
        return room

    @parameterized.expand([
        [1, "one-bed room"],
        [2, "two-bed room"],
        [2, "two-bed room"],
        [3, None]
    ])
    def test_add_room(self, beds, description):
        room = self._prepare_room_object(beds, description)
        room.save()
        self.assertEqual((room.beds, room.description), (beds, description), "Room was not created")

    def test_add_room_without_beds(self):
        room = self._prepare_room_object(None, "Room without beds")
        try:
            room.save()
        except IntegrityError as e:
            pass
        except Exception as e:
            raise e
        else:
            raise  AssertionError("Room without beds was added or exception wasn't thrown")

    def test_remove_room(self):
        beds, description = 2, "test room"
        room = self._prepare_room_object(beds,description)
        room.save()
        room = Room.objects.get(id=room.id)
        room.delete()
        try:
            Room.objects.get(id=room.id)
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            raise e
        else:
            raise AssertionError("Room was not removed properly or exception wasn't thrown")

    def test_update_room(self):
        beds, description = 2, "test room"
        room = self._prepare_room_object(beds, description)
        room.save()
        prev_room_id, prev_room_beds, prev_room_description = room.id, room.beds, room.description
        new_room_beds, new_room_description = 5, "five-bed room"
        room.beds = new_room_beds
        room.description = new_room_description

        self.assertEqual(room.id, prev_room_id, "room id was changed")
        self.assertEqual((room.beds,room.description), (new_room_beds,new_room_description),
                         "Room wasn't updated properly")

class GuestModelTestCase(TestCase):
    def _prepare_test_guest(self,first_name,last_name,passport,birthdate):
        guest = Guest()
        guest.first_name = first_name
        guest.last_name = last_name
        guest.passport = passport
        guest.birthdate = birthdate
        return guest

    def test_add_guest(self):
        first_name, last_name, passport, birthdate = "UserFirstName1","UserLastName","123425215",datetime.date(1992,12,12)
        guest = self._prepare_test_guest(first_name,last_name,passport,birthdate)
        guest.save()

        guest = Guest.objects.get(id=guest.id)
        self.assertEqual((guest.first_name,guest.last_name,guest.passport,guest.birthdate),
                         (first_name, last_name, passport, birthdate), "Guest was not added")

    @parameterized.expand([
        [None,"UserName","123456",datetime.datetime(1992,1,23)],
        ["FirstName",None,"123456",datetime.datetime(1992,1,23)],
        ["FirstName","UserName",None,datetime.datetime(1992,1,23)],
        ["FirstName","UserName","123456",None],
    ])
    def test_add_guest_without_required_properties(self, first_name, last_name, passport, birthdate ):
        guest = self._prepare_test_guest(first_name, last_name, passport, birthdate)
        try:
            guest.save()
        except IntegrityError:
            pass
        except Exception as e:
            raise e
        else:
            raise AssertionError("Guest with incomplete info was added or exception wasn't thrown")

    def test_update_guest(self):
        first_name, last_name, passport, birthdate = "UserFirstName1", "UserLastName", "123425215", \
                                                     datetime.date(1992,12,12)
        guest = self._prepare_test_guest(first_name, last_name, passport, birthdate)
        guest.save()
        new_first_name, new_last_name, new_passport, new_birthdate = "NewUserFirstName1", "NewUserLastName", "177777777", \
                                                     datetime.date(1990, 5, 2)
        guest.first_name = new_first_name
        guest.last_name = new_last_name
        guest.passport = new_passport
        guest.birthdate = new_birthdate
        guest.save()

    def test_remove_guest(self):
        guest = self._prepare_test_guest("test", "test", "123213", datetime.datetime(1987, 12, 12))
        guest.save()
        guest.delete()
        try:
            guest.refresh_from_db()
        except ObjectDoesNotExist:
            pass
        else:
            raise AssertionError("Guest object was not removed")

class BookingModelTestCase(TestCase):
    def setUp(self):
        self.room = Room.objects.create(beds=2,description="test room")
        self.user = User.objects.create(username="tuser", first_name='tuser First Name', last_name='tuser Last Name',
                                   password='change_me2',description=None)



    def test_add_valid_booking(self):
        start_date, end_date, user_id, room_id = datetime.datetime(2019, 1, 1), datetime.datetime(2019, 1, 11), \
                                                 self.user, self.room
        booking = Booking()
        booking.start_date = start_date
        booking.end_date = end_date
        booking.user_id = user_id
        booking.room_id = room_id
        booking.save()
        self.assertEqual((booking.start_date,booking.end_date,user_id,room_id),(start_date, end_date, user_id, room_id),
                         "Booking was not added")

    def test_add_invalid_booking(self):
        def get_next_available_id(model_class):
            with connection.cursor() as cursor:
                cursor.execute( "select nextval('%s_id_seq')" % model_class._meta.db_table)
                result = cursor.fetchone()
                next_id_from_seq = result[0]
            return next_id_from_seq

        not_saved_user = copy(self.user)
        not_saved_user.id = get_next_available_id(User)
        not_saved_room = copy(self.room)
        not_saved_room.id = get_next_available_id(Room)

        start_date = datetime.datetime(2019,12,12)
        end_date = datetime.datetime(2019,12,22)

        booking = Booking()
        booking.start_date = start_date
        booking.end_date = end_date
        booking.user_id = not_saved_user
        booking.room_id = not_saved_room

        try:
            booking.save()
            with connection.cursor() as cursor:
                cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
                cursor.execute("SET CONSTRAINTS ALL DEFERRED")
        except IntegrityError:
            pass
        except Exception as e:
            raise e
        else:
            raise AssertionError("Invalid booking was added or exception wasn't thrown")


    def test_remove_booking(self):
        start_date, end_date, user_id, room_id = datetime.datetime(2019, 1, 1), datetime.datetime(2019, 1, 11), \
                                                 self.user.id, self.room.id
        booking = Booking()
        booking.start_date = start_date
        booking.end_date = end_date
        booking.user_id = self.user
        booking.room_id = self.room
        booking.save()

        booking.delete()

        try:
            self.user.refresh_from_db()
            self.room.refresh_from_db()
        except ObjectDoesNotExist:
            raise AssertionError("related User or Room object was removed")

class PermissionToUserModelTestCase():
    pass

class GuestToBookingModelTestCase():
    pass