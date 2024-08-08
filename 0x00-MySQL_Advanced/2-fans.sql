-- create table if not exists users
SELECT origin, fans as nb_fans FROM metal_bands ORDER BY nb_fans DESC;
