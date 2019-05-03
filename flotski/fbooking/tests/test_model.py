import datetime
import hashlib
from copy import copy

from django.db import IntegrityError, connection
from parameterized import parameterized
from django.test import TransactionTestCase
from fbooking.models import Room, Guest, Booking, GuestToBooking
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

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
        """
        Note: Room object should not be removed, room state should be changed insteadd
        :return:
        """
        beds, description = 2, "test room"
        room = self._prepare_room_object(beds, description)
        room.save()
        room.refresh_from_db()
        self.assertEqual(room.state, 1, "Created room is not in ACTIVE (1) state")
        room.state = 0
        room.save()
        room.refresh_from_db()
        self.assertEqual(room.state, 0, "Room state is not changed to INACTIVE (0)")

    def test_update_room(self):
        beds, description = 2, "test room"
        room = self._prepare_room_object(beds, description)
        room.save()
        prev_room, prev_room_beds, prev_room_description = room.id, room.beds, room.description
        new_room_beds, new_room_description = 5, "five-bed room"
        room.beds = new_room_beds
        room.description = new_room_description

        self.assertEqual(room.id, prev_room, "room id was changed")
        self.assertEqual((room.beds, room.description), (new_room_beds, new_room_description),
                         "Room wasn't updated properly")


class GuestModelTestCase(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create(username='tuser1', first_name='test', last_name='test',
                                          password=hashlib.sha256("change_Me1".encode('utf-8')).hexdigest())

    def _prepare_test_guest(self, first_name, last_name, passport, birth_date, user):
        guest = Guest()
        guest.first_name = first_name
        guest.last_name = last_name
        guest.passport = passport
        guest.birth_date = birth_date
        guest.user = user
        return guest

    def test_add_guest(self):
        first_name, last_name, passport, birth_date = "UserFirstName1", "UserLastName", "123425215", \
                                                      datetime.date(1992,12,12)
        guest = self._prepare_test_guest(first_name, last_name, passport, birth_date, self.user)
        guest.save()

        guest = Guest.objects.get(id=guest.id)
        self.assertEqual((guest.first_name, guest.last_name, guest.passport, guest.birth_date),
                         (first_name, last_name, passport, birth_date), "Guest was not added")

    @parameterized.expand([
        [None, "UserName", "123456", datetime.datetime(1992, 1, 23), True],
        ["FirstName", None, "123456", datetime.datetime(1992, 1, 23), True],
        ["FirstName", "UserName", None, datetime.datetime(1992, 1, 23), True],
        ["FirstName", "UserName", "123456", None, True],
        ["FirstName", "UserName", "123456", datetime.datetime(1992, 1, 23), False]
    ])
    def test_add_guest_without_required_properties(self, first_name, last_name, passport, birth_date, user):
        guest = self._prepare_test_guest(first_name, last_name, passport, birth_date, self.user if user else None)
        with self.assertRaises(IntegrityError):
            guest.save()

    def test_update_guest(self):
        first_name, last_name, passport, birth_date = "UserFirstName1", "UserLastName", "123425215", \
                                                     datetime.date(1992, 12, 12)
        guest = self._prepare_test_guest(first_name, last_name, passport, birth_date, self.user)
        guest.save()
        new_first_name, new_last_name, new_passport, new_birth_date = "NewUserFirstName1", "NewUserLastName", "177777777", \
                                                                     datetime.date(1990, 5, 2)
        guest.first_name = new_first_name
        guest.last_name = new_last_name
        guest.passport = new_passport
        guest.birth_date = new_birth_date
        guest.save()

    def test_add_guest_with_duplicate_passport(self):
        first_name, last_name, passport, birth_date = "UserFirstName1", "UserLastName", "123425215", \
                                                     datetime.date(1992, 12, 12)
        guest_1 = self._prepare_test_guest(first_name, last_name, passport, birth_date, self.user)
        guest_1.save()

        guest_2 = self._prepare_test_guest(first_name, last_name, passport, birth_date, self.user)
        with self.assertRaises(IntegrityError):
            guest_2.save()

    def test_remove_guest(self):
        guest = self._prepare_test_guest("test", "test", "123213", datetime.datetime(1987, 12, 12), self.user)
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
                                        password=hashlib.sha256("change_Me2".encode('utf-8')).hexdigest())

    def tearDown(self):
        self.activate_foreign_keys('OFF')

    def test_add_valid_booking(self):
        start_date, end_date, user, room = datetime.datetime(2019, 1, 1), datetime.datetime(2019, 1, 11), \
                                                 self.user, self.room
        booking = Booking()
        booking.start_date = start_date
        booking.end_date = end_date
        booking.user = user
        booking.room = room
        booking.save()
        self.assertEqual((booking.start_date, booking.end_date, user, room),
                         (start_date, end_date, user, room),
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
        booking.user = not_saved_user
        booking.room = not_saved_room

        with self.assertRaises(IntegrityError):
            booking.save()

    def test_remove_booking(self):
        start_date, end_date, user, room = datetime.datetime(2019, 1, 1), datetime.datetime(2019, 1, 11), \
                                                 self.user.id, self.room.id
        booking = Booking()
        booking.start_date = start_date
        booking.end_date = end_date
        booking.user = self.user
        booking.room = self.room
        booking.save()

        booking.delete()

        self.user.refresh_from_db()
        self.room.refresh_from_db()

class GuestToBookingModelTestCase(TransactionTestCase):
    def setUp(self):
        test_user = User.objects.create(username='tuser',
                                        first_name='Tuser',
                                        last_name='Tuser',
                                        password=hashlib.sha256("change_Me_1".encode('utf-8')).hexdigest())
        test_room = Room.objects.create(beds=2,
                                        description="")
        number_of_test_guests = 10
        self.guests = []
        for idx in range(number_of_test_guests):
            guest = Guest.objects.create(first_name="test_user_%d"%idx,
                                         last_name="test_user_%d"%idx,
                                         passport="12345667%d"%idx,
                                         birth_date=datetime.datetime(1990,12,12),
                                         user=test_user)
            self.guests.append(guest)

        number_of_test_booking = 10
        self.bookings = []
        for idx in range(number_of_test_booking):
            booking = Booking.objects.create(start_date=datetime.datetime(2018,12,24),
                                             end_date=datetime.datetime(2019, 1, 24),
                                             user=test_user,
                                             room=test_room)
            self.bookings.append(booking)

    def test_add_many_guests_to_one_booking(self):
        test_booking = self.bookings[0]
        for guest in self.guests:
            g_to_b = GuestToBooking()
            g_to_b.guest = guest
            g_to_b.booking = test_booking
            g_to_b.save()

    def test_add_one_guest_to_many_bookings(self):
        test_guest = self.guests[0]
        for booking in self.bookings:
            g_to_b = GuestToBooking()
            g_to_b.guest = test_guest
            g_to_b.booking = booking
            g_to_b.save()

    def test_add_duplicate_guest_to_booking(self):
        g_to_b = GuestToBooking()
        g_to_b.guest = self.guests[0]
        g_to_b.booking = self.bookings[0]
        g_to_b.save()

        g_to_b = GuestToBooking()
        g_to_b.guest = self.guests[0]
        g_to_b.booking = self.bookings[0]
        with self.assertRaises(IntegrityError):
            g_to_b.save()

    def remove_booking(self):
        test_guest = self.guests[0]
        test_booking = self.bookings[0]

        g_to_b = GuestToBooking()
        g_to_b.guest = test_guest
        g_to_b.booking = test_booking
        g_to_b.save()

        g_to_b.delete()

        with self.assertRaises(ObjectDoesNotExist):
            g_to_b.refresh_from_db()

        test_guest.refresh_from_db()
        test_booking.refresh_from_db()