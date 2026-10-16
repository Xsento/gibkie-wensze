# `1.`

```
Jako uczestnik wyjazdu grupowego chcę zaznaczać dni, w których jestem dostępny,
aby grupa mogła wybrać termin odpowiadający jak największej liczbie osób.
kryterium:
```

```
G: Użytkownik jest uczystnikiem wycieczki i ma dostęp do kalendarza
W: Użytkownik wybiera określony dzień w kalendarzu
T: System zapisuje jego dostępność i aktualizuje widok kalendarza, uwzględniając
przy tym dostępność pozostałych użytkowników
```

```
INVEST:
I: Niezależna – kalendarz działa bez głosowania, harmonogramu i kosztów.
N: Negocjowalna – sposób zaznaczania dni (klik, zakres) ustalamy z użytkownikiem.
V: Wartościowa – grupa widzi, kiedy może jechać najwięcej osób.
E: Szacowalna – jeden widok kalendarza i zapis dostępności.
S: Mała – mieści się w jednym sprincie.
T: Testowalna – sprawdzamy, czy po wybraniu dnia rośnie licznik dostępnych osób.
```

# `2.`

```
Jako uczestnik wyjazdu grupowego chcę głosować na propozycje noclegów i
atrakcji, aby grupa mogła wspólnie wybrać interesujące nas miejsca.
kryterium:
```

```
G: Użytkownik należy do grupy, a głosowanie na nocleg lub atrakcje jest otwarte.
W: Użytkownik wybiera propozycję noclegu/atrakcji i zatwierdza swój głos.
T: System zapisuje głos i aktualizuje liczbę głosów oddanych na wybraną
propozycję.
```

```
INVEST:
I: Niezależna – głosowanie nie wymaga kalendarza ani harmonogramu.
N: Negocjowalna – metodę głosowania (jeden głos, wiele głosów) można zmienić.
V: Wartościowa – grupa wspólnie wybiera nocleg i atrakcje.
E: Szacowalna – lista propozycji, przycisk głosu i licznik.
S: Mała – mieści się w jednym sprincie.
T: Testowalna – sprawdzamy, czy po oddaniu głosu licznik rośnie o 1.
```

# `3.`

```
Jako organizator wyjazdu grupowego chcę dodawać wydarzenia do harmonogramu, aby
uczestnicy znali plan dnia, godziny aktywności i miejsca spotkań.
kryterium:
```

```
G: Organizator ma dostęp do harmonogramu wyjazdu.
W: Organizator dodaje wydarzenie, podając jego nazwę, datę i godzinę.
T: System zapisuje wydarzenie i wyświetla je w harmonogramie we wskazanym
terminie.
```

```
INVEST:
I: Niezależna – harmonogram można dodać bez głosowania i kosztów.
N: Negocjowalna – dodatkowe pola (miejsce, opis) ustalamy z użytkownikiem.
V: Wartościowa – uczestnicy znają plan dnia i miejsca spotkań.
E: Szacowalna – formularz z nazwą, datą i godziną oraz lista wydarzeń.
S: Mała – mieści się w jednym sprincie.
T: Testowalna – sprawdzamy, czy dodane wydarzenie pojawia się we wskazanym terminie.
```

# `4.`

```
Jako uczestnik wyjazdu grupowego chcę sprawdzić szacunkowy koszt wycieczki na
podstawie planowanych wydatków, aby ocenić, czy wyjazd mieści się w moich
możliwościach finansowych.
kryterium:
```

```
G: W systemie zapisano przewidywane koszty noclegu, transportu, wyżywienia i
atrakcji.
W: Użytkownik otwiera sekcję szacunkowych kosztów wycieczki.
T: System wyświetla łączny szacunkowy koszt wyjazdu oraz przewidywany koszt
przypadający na jednego uczestnika.
```

```
INVEST:
I: Niezależna – koszty liczymy z zapisanych kwot, bez innych modułów.
N: Negocjowalna – kategorie kosztów i sposób zaokrąglania można zmienić.
V: Wartościowa – uczestnik ocenia, czy stać go na wyjazd.
E: Szacowalna – suma kosztów i dzielenie przez liczbę uczestników.
S: Mała – mieści się w jednym sprincie.
T: Testowalna – sprawdzamy sumę i koszt na osobę dla znanych kwot.
```

# `5.`

```
Jako użytkownik aplikacji TripForge chcę zalogować się na swoje konto, aby
uzyskać dostęp do swoich wyjazdów grupowych.
kryterium:
```

```
G: Użytkownik posiada konto w aplikacji i zna prawidłowe dane logowania.
W: Użytkownik wpisuje poprawny adres e-mail i hasło, a następnie wybiera opcję
„Zaloguj się”.
T: System weryfikuje dane logowania i przekierowuje użytkownika do jego widoku
aplikacji.
```

```
INVEST:
I: Niezależna – logowanie nie zależy od pozostałych funkcji.
N: Negocjowalna – np. logowanie przez Google można dodać później.
V: Wartościowa – użytkownik ma dostęp tylko do swoich wyjazdów.
E: Szacowalna – formularz logowania i weryfikacja hasła.
S: Mała – mieści się w jednym sprincie.
T: Testowalna – poprawne dane przekierowują do aplikacji, błędne dają komunikat błędu.
```
