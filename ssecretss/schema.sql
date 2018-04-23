drop table if exists secrets;
create table secrets (
    id integer primary key autoincrement,
    secret_guid text not null,
    secret_text text not null,
    expire_at text not null,
    views_left int not null
);
