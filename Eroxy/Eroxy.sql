create table proxy(
ip char(15) primary key not null,
port char(5) not null,
delay int,
protocal varchar(255),
type varchar(255),
location varchar(255),
inTime datetime,
life varchar(255),
alive tinyint
);