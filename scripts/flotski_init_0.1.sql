/**:
    Flotski PostgreSQL initialization script
    Schema version: 0.1
**/

drop table if exists FLOTSKI_BOOKING CASCADE; 
drop table if exists FLOTSKI_GUEST CASCADE;
drop table if exists FLOTSKI_ROOM CASCADE;
drop table if exists FLOTSKI_USER CASCADE;
drop table if exists FLOTSKI_PERMISSION CASCADE;
drop table if exists FLOTSKI_PERMISSION_TO_USER CASCADE;



create table FLOTSKI_ROOM (
    ID           serial     PRIMARY KEY,
    DESCRIPTION  varchar(255)          ,
    BEDS         integer       not null
);

create table FLOTSKI_PERMISSION (
    ID           serial  PRIMARY KEY,
    ACCESS       char(1) UNIQUE not null,
    DESCRIPTION  varchar(255)
);

create table FLOTSKI_USER (
    ID           serial     PRIMARY KEY,
    USERNAME     varchar(15)  not null,
    FIRST_NAME   varchar(15)  not null,
    LAST_NAME    varchar(15)  not null,
    PASSWORD     text   not null,
    DESCRIPTION  varchar(255)
);

create table FLOTSKI_BOOKING (
    ID          serial      PRIMARY KEY,
    START_DATE  date         not null,
    END_DATE    date         not null,
    USER_ID     integer  REFERENCES FLOTSKI_USER(ID),
    ROOM_ID     integer  REFERENCES FLOTSKI_ROOM(ID),
    CREATION_DATE  date      not null
    
);

create table FLOTSKI_GUEST (
    ID         serial      PRIMARY KEY,
    FIRST_NAME varchar(255) not null,
    LAST_NAME  varchar(255) not null,
    PASSPORT   varchar(255) not null,
    BIRTH_DATE date         not null,
    BOOKING_ID integer REFERENCES FLOTSKI_BOOKING(ID)
);

create table FLOTSKI_PERMISSION_TO_USER (
    ID SERIAL PRIMARY KEY,
    USER_ID         integer,
    PERMISSION_ID   integer,
    CONSTRAINT "FK_USER_ID" FOREIGN KEY (USER_ID) REFERENCES FLOTSKI_USER(ID),
    CONSTRAINT "FK_PERMISSION_ID" FOREIGN KEY (PERMISSION_ID) REFERENCES FLOTSKI_PERMISSION(ID)

);

CREATE UNIQUE INDEX UI_USER_TO_PERMISSION_PERMISSION_TO_USER ON FLOTSKI_PERMISSION_TO_USER USING btree(PERMISSION_ID, USER_ID);
