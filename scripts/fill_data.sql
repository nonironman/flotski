---users data
insert into FLOTSKI_USER(USERNAME,FIRST_NAME,LAST_NAME,PASSWORD) VALUES('maskim','','',crypt('DummyPass1',gen_salt('bf')));
insert into FLOTSKI_USER(USERNAME,FIRST_NAME,LAST_NAME,PASSWORD) VALUES('yana','','',crypt('DummyPass2',gen_salt('bf')));
insert into FLOTSKI_USER(USERNAME,FIRST_NAME,LAST_NAME,PASSWORD) VALUES('sveta','','',crypt('DummyPass3',gen_salt('bf')));
insert into FLOTSKI_USER(USERNAME,FIRST_NAME,LAST_NAME,PASSWORD) VALUES('egor','','',crypt('DummyPass4',gen_salt('bf')));
insert into FLOTSKI_USER(USERNAME,FIRST_NAME,LAST_NAME,PASSWORD) VALUES('artyom','','',crypt('DummyPass5',gen_salt('bf')));
insert into FLOTSKI_USER(USERNAME,FIRST_NAME,LAST_NAME,PASSWORD) VALUES('nastya','','',crypt('DummyPass6',gen_salt('bf')));

---rooms data
insert into FLOTSKI_ROOM(DESCRIPTION,BEDS) values('One-bed room', 1);
insert into FLOTSKI_ROOM(DESCRIPTION,BEDS) values('two-bed room', 2);
insert into FLOTSKI_ROOM(DESCRIPTION,BEDS) values('three-bed room', 3);
insert into FLOTSKI_ROOM(DESCRIPTION,BEDS) values('four-bed room', 4);
insert into FLOTSKI_ROOM(DESCRIPTION,BEDS) values('five-bed room', 5);
insert into FLOTSKI_ROOM(DESCRIPTION,BEDS) values('six-bed room', 6);

---permissions
insert into FLOTSKI_PERMISSION(ACCESS,DESCRIPTION) values('R','Read');
insert into FLOTSKI_PERMISSION(ACCESS,DESCRIPTION) values('W','Write');
insert into FLOTSKI_PERMISSION(ACCESS,DESCRIPTION) values('X','Execute');
insert into FLOTSKI_PERMISSION(ACCESS,DESCRIPTION) values('U','Update');
insert into FLOTSKI_PERMISSION(ACCESS,DESCRIPTION) values('D','Delete');

---user-permission
insert into FLOTSKI_PERMISSION_TO_USER(USER_ID,PERMISSION_ID) VALUES(1,1);

---booking
insert into FLOTSKI_BOOKING(START_DATE,END_DATE,USER_ID,ROOM_ID,CREATION_DATE) VALUES('21/10/2018','25/10/2018',1,1,'21/10/2018');

---guests
insert into FLOTSKI_GUEST(FIRST_NAME,LAST_NAME,PASSPORT,BIRTH_DATE,BOOKING_ID) VALUES('Ichkebek','Razulovich','85 43 12342','25/12/1997',1);

