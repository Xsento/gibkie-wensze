-- UC: dostępność uczestników w kalendarzu
-- Projekt tworzy schemat przez db.create_all() / `flask init-db`.
-- Nowa baza: wystarczy `flask --app run init-db` (tworzy tabele razem z ograniczeniem).
-- Istniejąca baza PostgreSQL (bez kasowania danych): uruchom ten skrypt jeden raz.

-- 1. Sprawdź, czy nie ma zdublowanych uczestników (ten sam użytkownik 2x w jednym wyjeździe).
--    Jeśli zapytanie coś zwróci, usuń nadmiarowe wiersze przed krokiem 2.
SELECT trip_id, user_id, COUNT(*) FROM trip_members GROUP BY trip_id, user_id HAVING COUNT(*) > 1;

-- 2. Jeden użytkownik = jeden uczestnik danego wyjazdu.
ALTER TABLE trip_members ADD CONSTRAINT uq_trip_user UNIQUE (trip_id, user_id);
