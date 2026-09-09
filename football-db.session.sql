create user football_ro with password 'football_ro';
grant connect on database football_db to football_ro;
grant usage on schema public to football_ro;
grant select on all tables in schema public to football_ro;
alter default privileges in schema public grant select on tables to football_ro;
