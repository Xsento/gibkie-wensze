    # Specyfikacja: TripForge (prototyp)

## 1. Cel

TripForge to prosta aplikacja webowa do planowania wspólnego wyjazdu w grupie. Uczestnicy zaznaczają dostępność, głosują na nocleg i atrakcje, widzą harmonogram i szacunkowy koszt wyjazdu.

**Zakres prototypu:** dokładnie 5 historii użytkownika poniżej. Wszystko inne (finanse po wyjeździe, powiadomienia, zaproszenia linkiem) jest poza zakresem.

## 2. Historie użytkownika (INVEST) i kryteria akceptacji (Given-When-Then)

### US-1 Zaznaczanie dostępności

Jako **uczestnik wyjazdu grupowego** chcę **zaznaczać dni, w których jestem dostępny**, aby **grupa mogła wybrać termin odpowiadający jak największej liczbie osób**.

- **Given:** użytkownik jest uczestnikiem wycieczki i ma dostęp do kalendarza
- **When:** użytkownik wybiera określony dzień w kalendarzu
- **Then:** system zapisuje jego dostępność i aktualizuje widok kalendarza, uwzględniając dostępność pozostałych uczestników

### US-2 Głosowanie na propozycje

Jako **uczestnik wyjazdu grupowego** chcę **głosować na propozycje noclegów i atrakcji**, aby **grupa mogła wspólnie wybrać interesujące nas miejsca**.

- **Given:** użytkownik należy do grupy, a głosowanie na nocleg lub atrakcje jest otwarte
- **When:** użytkownik wybiera propozycję noclegu/atrakcji i zatwierdza swój głos
- **Then:** system zapisuje głos i aktualizuje liczbę głosów oddanych na wybraną propozycję

### US-3 Harmonogram

Jako **organizator wyjazdu grupowego** chcę **dodawać wydarzenia do harmonogramu**, aby **uczestnicy znali plan dnia, godziny aktywności i miejsca spotkań**.

- **Given:** organizator ma dostęp do harmonogramu wyjazdu
- **When:** organizator dodaje wydarzenie, podając jego nazwę, datę i godzinę
- **Then:** system zapisuje wydarzenie i wyświetla je w harmonogramie we wskazanym terminie

### US-4 Szacunkowy koszt

Jako **uczestnik wyjazdu grupowego** chcę **sprawdzić szacunkowy koszt wycieczki na podstawie planowanych wydatków**, aby **ocenić, czy wyjazd mieści się w moich możliwościach finansowych**.

- **Given:** w systemie zapisano przewidywane koszty noclegu, transportu, wyżywienia i atrakcji
- **When:** użytkownik otwiera sekcję szacunkowych kosztów wycieczki
- **Then:** system wyświetla łączny szacunkowy koszt wyjazdu oraz koszt przypadający na jednego uczestnika

### US-5 Logowanie

Jako **użytkownik aplikacji TripForge** chcę **zalogować się na swoje konto**, aby **uzyskać dostęp do swoich wyjazdów grupowych**.

- **Given:** użytkownik posiada konto i zna prawidłowe dane logowania
- **When:** użytkownik wpisuje poprawny e-mail i hasło i wybiera „Zaloguj się”
- **Then:** system weryfikuje dane i przekierowuje użytkownika do jego widoku aplikacji

## 3. Wymagania funkcjonalne

| ID   | Wymaganie                                                                                                     | Historia |
| ---- | ------------------------------------------------------------------------------------------------------------- | -------- |
| FR-1 | Uczestnik zaznacza/odznacza dzień dostępności; kalendarz pokazuje, ile osób jest dostępnych w danym dniu      | US-1     |
| FR-2 | Uczestnik oddaje głos na propozycję (1 głos na propozycję); system pokazuje liczbę głosów                     | US-2     |
| FR-3 | Organizator dodaje wydarzenie (nazwa, data, godzina, miejsce); harmonogram jest posortowany wg daty i godziny | US-3     |
| FR-4 | System liczy sumę planowanych kosztów i koszt na osobę (suma / liczba uczestników)                            | US-4     |
| FR-5 | Logowanie e-mailem i hasłem; błędne dane dają komunikat błędu                                                 | US-5     |

## 4. Wymagania niefunkcjonalne (ISO/IEC 25010, seria SQuaRE)

| ID    | Charakterystyka        | Wymaganie                     | Metryka                                        |
| ----- | ---------------------- | ----------------------------- | ---------------------------------------------- |
| NFR-1 | Functional Suitability | Poprawne obliczenia kosztów   | RoundingError = 0 gr                           |
| NFR-2 | Performance Efficiency | Szybkie odpowiedzi stron      | ResponseTime p95 < 500 ms                      |
| NFR-3 | Reliability            | Dostępność usługi             | Availability ≥ 99,5%, MTTR < 4 h, MTBF > 720 h |
| NFR-4 | Security               | Hasła przechowywane jako hash | 0 haseł jawnym tekstem                         |
| NFR-5 | Usability              | Prosta obsługa                | TimeToFirstVote < 60 s                         |
| NFR-6 | Maintainability        | Kod testowalny                | TestCoverage ≥ 70%                             |

## 5. Technologie

- Python 3.12, Flask, Flask-SQLAlchemy, Jinja2
- PostgreSQL (produkcja); w prototypie domyślnie SQLite, zmiana przez zmienną `DATABASE_URL`
- GitHub (repozytorium)

## 6. Model danych

User(id, email, password_hash, name, is_organizer) · Availability(user_id, day) · Proposal(id, kind, title) · Vote(user_id, proposal_id) · Event(id, name, date, time, place) · Cost(id, category, amount_gr)
