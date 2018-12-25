import datetime
import hashlib
from copy import copy

from django.db import IntegrityError, connection
from parameterized import parameterized
from django.test import TransactionTestCase
from models import User, Room, Permission, PermissionToUser, Guest, Booking, GuestToBooking
from django.core.exceptions import ObjectDoesNotExist


class UserModelTestCase(TransactionTestCase):
    def _prepare_test_user_object(self, username, password, first_name, last_name, description=None):
        user = User()
        user.username = username
        user.password = password
        user.first_name = first_name
        user.last_name = last_name
        user.description = description
        return user

    @parameterized.expand([
        ["valid_tuser1", hashlib.sha256("change_Me_1").hexdigest(), "TestUserFirstName", "TestUserLastName", "test description"],
        ["valid_tuser2", hashlib.sha256("change_Me_2").hexdigest(), "TestUserFirstName", "TestUserLastName", None],
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
        [None, hashlib.sha256("change_Me_1").hexdigest(), "TestUserFirstName", "TestUserLastName", "test description"],
        ["invalid_tuser2", None, "TestUserFirstName", "TestUserLastName", None],
        ["invalid_tuser3", hashlib.sha256("change_Me_3").hexdigest(), None, "TestUserLastName", None],
        ["invalid_tuser4", hashlib.sha256("change_Me_4").hexdigest(), "TestUserFirstName", None, None],
    ])
    def test_add_valid_user(self, username, password, first_name, last_name, description):
        user = self._prepare_test_user_object(username, password, first_name, last_name, description)
        with self.assertRaises(IntegrityError):
            user.save()

    def test_remove_user(self):
        username = "user_to_remove"
        user = self._prepare_test_user_object(username, "", "", "", None)
        user.save()
        user = User.objects.get(username=username)
        user.delete()
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(username=username)

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


class PermissionModelTestCase(TransactionTestCase):
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
        permission = self._prepare_permission_object(access, description)
        permission.save()
        self.assertEqual((permission.access, permission.description), (access, description),
                         "Specified permission was not saved properly")

    @parameterized.expand([
        ['w', None],
        [None, 'delete access']
    ])
    def test_add_invalid_permission(self, access, description):
        permission = self._prepare_permission_object(access, description)
        with self.assertRaises(IntegrityError):
            permission.save()

    def test_add_duplicate_permission(self):
        write_permission_1 = self._prepare_permission_object("w", "write access 1")
        write_permission_2 = self._prepare_permission_object("w", "write access 2")
        write_permission_1.save()
        with self.assertRaises(IntegrityError):
            write_permission_2.save()

    def test_remove_permission(self):
        access, description = "s", "test permission"
        permission = self._prepare_permission_object(access, description)
        permission.save()
        permission = Permission.objects.get(access=access)
        permission.delete()
        with self.assertRaises(ObjectDoesNotExist):
            Permission.objects.get(access=access)

    def test_update_permission(self):
        permission = self._prepare_permission_object('u', "update permission")
        permission.save()
        prev_permission_id, prev_permission_access, prev_permission_desc = (
        permission.id, permission.access, permission.description)
        new_access, new_description = "X", "execute permission"
        permission.access = new_access
        permission.description = new_description
        permission.save()
        self.assertEqual(prev_permission_id, permission.id, "Permission id was updated")
        self.assertEqual((permission.access, permission.description), (new_access, new_description),
                         "Permission was not updated properly")


class RoomModelTestCase(TransactionTestCase):
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
        with self.assertRaises(IntegrityError):
            room.save()

    def test_remove_room(self):
        beds, description = 2, "test room"
        room = self._prepare_room_object(beds, description)
        room.save()
        room = Room.objects.get(id=room.id)
        room.delete()
        with self.assertRaises(ObjectDoesNotExist):
            Room.objects.get(id=room.id)

    def test_update_room(self):
        beds, description = 2, "test room"
        room = self._prepare_room_object(beds, description)
        room.save()
        prev_room_id, prev_room_beds, prev_room_description = room.id, room.beds, room.description
        new_room_beds, new_room_description = 5, "five-bed room"
        room.beds = new_room_beds
        room.description = new_room_description

        self.assertEqual(room.id, prev_room_id, "room id was changed")
        self.assertEqual((room.beds, room.description), (new_room_beds, new_room_description),
                         "Room wasn't updated properly")


class GuestModelTestCase(TransactionTestCase):
    def _prepare_test_guest(self, first_name, last_name, passport, birthdate):
        guest = Guest()
        guest.first_name = first_name
        guest.last_name = last_name
        guest.passport = passport
        guest.birthdate = birthdate
        return guest

    def test_add_guest(self):
        first_name, last_name, passport, birthdate = "UserFirstName1", "UserLastName", "123425215", datetime.date(1992,
                                                                                                                  12,
                                                                                                                  12)
        guest = self._prepare_test_guest(first_name, last_name, passport, birthdate)
        guest.save()

        guest = Guest.objects.get(id=guest.id)
        self.assertEqual((guest.first_name, guest.last_name, guest.passport, guest.birthdate),
                         (first_name, last_name, passport, birthdate), "Guest was not added")

    @parameterized.expand([
        [None, "UserName", "123456", datetime.datetime(1992, 1, 23)],
        ["FirstName", None, "123456", datetime.datetime(1992, 1, 23)],
        ["FirstName", "UserName", None, datetime.datetime(1992, 1, 23)],
        ["FirstName", "UserName", "123456", None],
    ])
    def test_add_guest_without_required_properties(self, first_name, last_name, passport, birthdate):
        guest = self._prepare_test_guest(first_name, last_name, passport, birthdate)
        with self.assertRaises(IntegrityError):
            guest.save()

    def test_update_guest(self):
        first_name, last_name, passport, birthdate = "UserFirstName1", "UserLastName", "123425215", \
                                                     datetime.date(1992, 12, 12)
        guest = self._prepare_test_guest(first_name, last_name, passport, birthdate)
        guest.save()
        new_first_name, new_last_name, new_passport, new_birthdate = "NewUserFirstName1", "NewUserLastName", "177777777", \
                                                                     datetime.date(1990, 5, 2)
        guest.first_name = new_first_name
        guest.last_name = new_last_name
        guest.passport = new_passport
        guest.birthdate = new_birthdate
        guest.save()

    def test_add_guest_with_duplicate_passport(self):
        first_name, last_name, passport, birthdate = "UserFirstName1", "UserLastName", "123425215", \
                                                     datetime.date(1992, 12, 12)
        guest_1 = self._prepare_test_guest(first_name, last_name, passport, birthdate)
        guest_1.save()

        guest_2 = self._prepare_test_guest(first_name, last_name, passport, birthdate)
        with self.assertRaises(IntegrityError):
            guest_2.save()

    def test_remove_guest(self):
        guest = self._prepare_test_guest("test", "test", "123213", datetime.datetime(1987, 12, 12))
        guest.save()
        guest.delete()
        with self.assertRaises(ObjectDoesNotExist):
            guest.refresh_from_db()


class BookingModelTestCase(TransactionTestCase):
    def activate_foreign_keys(self, state='ON'):
        if connection.vendor == 'sqlite':
            with connection.cursor() as cursor:
                cursor.execute('PRAGMA foreign_keys = %s;'%state)

    def setUp(self):
        self.activate_foreign_keys()
        self.room = Room.objects.create(beds=2, description="test room")
        self.user = User.objects.create(username="tuser", first_name='tuser First Name', last_name='tuser Last Name',
                                        password=hashlib.sha256("change_Me2").hexdigest(), description=None)

    def tearDown(self):
        self.activate_foreign_keys('OFF')

    def test_add_valid_booking(self):
        start_date, end_date, user_id, room_id = datetime.datetime(2019, 1, 1), datetime.datetime(2019, 1, 11), \
                                                 self.user, self.room
        booking = Booking()
        booking.start_date = start_date
        booking.end_date = end_date
        booking.user_id = user_id
        booking.room_id = room_id
        booking.save()
        self.assertEqual((booking.start_date, booking.end_date, user_id, room_id),
                         (start_date, end_date, user_id, room_id),
                         "Booking was not added")

    def test_add_invalid_booking(self):
        def get_next_available_id(model_class):
            with connection.cursor() as cursor:
                cursor.execute("select max(id) from %s" % model_class._meta.db_table)
                result = cursor.fetchone()
                next_id_from_seq = result[0] + 1
            return next_id_from_seq

        not_saved_user = copy(self.user)
        not_saved_user.id = get_next_available_id(User)
        not_saved_room = copy(self.room)
        not_saved_room.id = get_next_available_id(Room)

        start_date = datetime.datetime(2019, 12, 12)
        end_date = datetime.datetime(2019, 12, 22)

        booking = Booking()
        booking.start_date = start_date
        booking.end_date = end_date
        booking.user_id = not_saved_user
        booking.room_id = not_saved_room

        with self.assertRaises(IntegrityError):
            booking.save()

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

        self.user.refresh_from_db()
        self.room.refresh_from_db()


class PermissionToUserModelTestCase(TransactionTestCase):
    def setUp(self):
        self.read_access = Permission.objects.create(access='R', description='Read permission')
        self.write_access = Permission.objects.create(access='W', description='Write permission')
        self.delete_access = Permission.objects.create(access='D', description='Write permission')

        self.user_1 = User.objects.create(username='tuser1', first_name='test', last_name='test',
                                          password='qwerty', description="desc")
        self.user_2 = User.objects.create(username='tuser2', first_name='test', last_name='test',
                                          password='qwerty', description="desc")

    def test_add_permission_to_user(self):
        for access in self.read_access, self.write_access, self.delete_access:
            p_to_u = PermissionToUser()
            p_to_u.user_id = self.user_1
            p_to_u.permission_id = access
            p_to_u.save()

        p_to_u1 = PermissionToUser.objects.filter(user_id=self.user_1)
        permissions = [p_to_u.permission_id for p_to_u in p_to_u1]
        self.assertListEqual([self.read_access, self.write_access, self.delete_access],
                             permissions, "Permission list is not matching with expected")

        p_to_u = PermissionToUser()
        p_to_u.user_id = self.user_2
        p_to_u.permission_id = self.read_access
        p_to_u.save()

        p_to_u2 = PermissionToUser.objects.filter(user_id=self.user_2)
        permissions = [p_to_u.permission_id for p_to_u in p_to_u2]
        self.assertListEqual([self.read_access],
                             permissions, "Permission list is not matching with expected")

    def test_add_duplicate_permission_to_user(self):
        PermissionToUser.objects.create(user_id=self.user_1, permission_id=self.read_access)
        with self.assertRaises(IntegrityError):
            PermissionToUser.objects.create(user_id=self.user_1, permission_id=self.read_access)


class GuestToBookingModelTestCase(TransactionTestCase):
    def setUp(self):
        test_user = User.objects.create(username='tuser',
                                        first_name='Tuser',
                                        last_name='Tuser',
                                        password=hashlib.sha256("change_Me_1").hexdigest(),
                                        description="")
        test_room = Room.objects.create(beds=2,
                                        description="")
        number_of_test_guests = 10
        self.guests = []
        for idx in xrange(number_of_test_guests):
            guest = Guest.objects.create(first_name="test_user_%d"%idx,
                                         last_name="test_user_%d"%idx,
                                         passport="12345667%d"%idx,
                                         birthdate=datetime.datetime(1990,12,12))
            self.guests.append(guest)

        number_of_test_booking = 10
        self.bookings = []
        for idx in xrange(number_of_test_booking):
            booking = Booking.objects.create(start_date=datetime.datetime(2018,12,24),
                                             end_date=datetime.datetime(2019, 1, 24),
                                             user_id=test_user,
                                             room_id=test_room)
            self.bookings.append(booking)

    def test_add_many_guests_to_one_booking(self):
        test_booking = self.bookings[0]
        for guest in self.guests:
            g_to_b = GuestToBooking()
            g_to_b.guest_id = guest
            g_to_b.booking_id = test_booking
            g_to_b.save()

    def test_add_one_guest_to_many_bookings(self):
        test_guest = self.guests[0]
        for booking in self.bookings:
            g_to_b = GuestToBooking()
            g_to_b.guest_id = test_guest
            g_to_b.booking_id = booking
            g_to_b.save()

    def test_add_duplicate_guest_to_booking(self):
        g_to_b = GuestToBooking()
        g_to_b.guest_id = self.guests[0]
        g_to_b.booking_id = self.bookings[0]
        g_to_b.save()

        g_to_b = GuestToBooking()
        g_to_b.guest_id = self.guests[0]
        g_to_b.booking_id = self.bookings[0]
        with self.assertRaises(IntegrityError):
            g_to_b.save()

    def remove_booking(self):
        test_guest = self.guests[0]
        test_booking = self.bookings[0]

        g_to_b = GuestToBooking()
        g_to_b.guest_id = test_guest
        g_to_b.booking_id = test_booking
        g_to_b.save()

        g_to_b.delete()

        with self.assertRaises(ObjectDoesNotExist):
            g_to_b.refresh_from_db()

        test_guest.refresh_from_db()
        test_booking.refresh_from_db()