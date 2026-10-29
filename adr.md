# Title

Autoryzacja i warunkowe renderowanie akcji zatwierdzania terminu na podstawie wartości w tabeli TRIP_MEMBERS

## Status

Zaakceptowany

## Context

Interfejs aplikacji zawiera sekcję "Zatwierdź termin" z przyciskiem "Zatwierdź". Dostęp do tej akcji powinien być ograniczony wyłącznie do osoby pełniącej rolę organizatora danej wycieczki. Model bazy danych w tabeli TRIP_MEMBERS przechowuje przypisanie członków do wycieczek wraz z flagą is_organizer

## Decision

Wprowadzamy warunkowe renderowanie części interfejsu strony: Przycisk "Zatwierdź" oraz pola formularza wyboru dat zostaną wyrenderowane w szablonie tylko wtedy, gdy flaga is_organizer dla danego użytkownika wynosi TRUE. Zwykli uczestnicy nie zobaczą tej opcji w kalendarzu


## Consequences

+ Zyskujemy pewność, że nieuprawniony uczestnik nie zatwierdzi terminu nawet przy próbie ominięcia warstwy wizualnej
+ Wykorzystujemy istniejącą strukturę tabeli TRIP_MEMBERS bez konieczności modyfikacji schematu bazy danych.
+ Precyzyjne rozdzielenie odpowiedzialności w interfejsie użytkownika zapobiega pomyłkowym próbom zatwierdzania terminów przez uczestników.




# Title

Interaktywny wybór przedziału dat na siatce kalendarza

## Status

Zaakceptowany

## Context

W widoku planowania wycieczki wymagane jest precyzyjne wskazanie dat w których jest się dostępnym. Ręczne wpisywanie wartości w pola tekstowe dd/mm/yyyy jest podatne na błędy składniowe oraz uciążliwe na urządzeniach mobilnych.

## Decision

Interakcja: Kliknięcie komórki przełącza (włącza/wyłącza) deklarację dostępności użytkownika dla danego dnia.
Wizualizacja: Wybrane terminy wyróżniają się na siatce, informując resztę grupy o dyspozycyjności.
Dynamika barw: Nasycenie koloru pola zależy od łącznej liczby osób, które zaznaczyły dany dzień.


## Consequences

+ Bardzo płynna i szybka obsługa interfejsu dla uczestników zaznaczających wiele dni z rzędu.
+ Zapewnienie, że dane przekazywane do backendu we Flasku zawsze posiadają poprawny format i mieszczą się w dozwolonych granicach kalendarza.
- Konieczność utworzenia nowej tabeli w PostgreSQL.
- Baza danych PostgreSQL będzie obsługiwać więcej drobnych zapytań zapisu/usuwania.




# Title

Wybór stosu technologicznego do obsługi backendu i bazy danych

## Status

Zaakceptowany

## Context

Aplikacja do planowania wycieczek wymaga stabilnego, bezpiecznego i prostego w utrzymaniu systemu. System musi efektywnie obsługiwać relacje wielokrotne, przechowywać złożone dane o dostępności w kalendarzu, sprawnie walidować współbieżny zapis terminów oraz umożliwiać elastyczne dostarczanie danych do interfejsu użytkownika.

## Decision

Zdecydujemy się na wybór następującego stosu technologicznego po stronie serwera i bazy danych:
- Język programowania — Python:
Zapewnia wysoką czytelność kodu, łatwość utrzymania oraz bogaty ekosystem bibliotek do przetwarzania dat, struktur danych i integracji zewnętrznych.
- Framework webowy — Flask:
Lekki mikro-framework, który daje pełną kontrolę nad strukturą projektu i routingiem. Pozwala na bezproblemową budowę elastycznych endpointów REST API lub serwowanie tradycyjnych szablonów HTML.   
- System zarządzania bazą danych — PostgreSQL:
Zaawansowana, relacyjna baza danych zapewniająca pełną spójność transakcyjną. PostgreSQL oferuje natywne typy zakresowe oraz mechanizmy wykluczeń, co wprost rozwiązuje problem nakładania się rezerwowanych terminów i gwarantuje spójność tabel relacyjnych.


## Consequences

+ Połączenie Pythona i Flaska umożliwia błyskawiczne prototypowanie i wprowadzanie poprawek w logice.
+ Wykorzystanie zaawansowanych funkcji PostgreSQL gwarantuje spójność uprawnień.
+ Brak narzuconej przez framework struktury pozwala na swobodną integrację z ORM.
- Flask wymaga ręcznego doboru i skonfigurowania modułów odpowiedzialnych za autoryzację, walidację formularzy czy zabezpieczenia.

