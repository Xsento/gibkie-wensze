# ✈️ TripForge

> Wspólne planowanie wyjazdu w grupie, w jednym miejscu: **kiedy**, **dokąd**, **co robimy** i **ile to kosztuje**.

Dziś grupa planuje wyjazd w kilku narzędziach naraz: ustalenia giną na WhatsAppie, dostępność zbiera się w Doodle, a koszty liczy się w arkuszu. TripForge łączy to w jednej prostej aplikacji webowej.

Projekt powstał na zajęcia z **Inżynierii Oprogramowania**. Zespół liczy 3 osoby.

---

## ✨ Funkcje

|     | Funkcja                                                | Historia |
| --- | ------------------------------------------------------ | -------- |
| 🔐  | Logowanie e-mailem i hasłem                            | US-5     |
| 📅  | Kalendarz dostępności z liczbą chętnych na każdy dzień | US-1     |
| 🗳️  | Głosowanie na noclegi i atrakcje                       | US-2     |
| 🗓️  | Harmonogram wydarzeń (dodaje organizator)              | US-3     |
| 💰  | Szacunkowy koszt wyjazdu, łącznie i na osobę           | US-4     |

## 🗂️ Artefakty projektu

| Artefakt                  | Gdzie                                                                  | Opis                                                          |
| ------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------- |
| Historie użytkownika      | [`use_case.md`](use_case.md)                                           | 5 historii w standardzie INVEST z kryteriami Given-When-Then  |
| Diagram przypadków użycia | [`docs/diagrams/use-case.puml`](docs/diagrams/use-case.puml)           | Aktorzy, przypadki użycia, relacje «include» i «extend»       |
| Diagram wymagań           | [`docs/diagrams/requirements.puml`](docs/diagrams/requirements.puml)   | 5 FR i 6 NFR z kategoriami SQuaRE i metrykami                 |
| Diagram klas              | [`docs/diagrams/classes.puml`](docs/diagrams/classes.puml)             | Model dziedziny ze specyfikacji: 6 encji, relacje i krotności |
| Diagram komunikacji       | [`docs/diagrams/communication.puml`](docs/diagrams/communication.puml) | US-1 zaznaczanie dostępności według założeń                   |
| Diagram sekwencji         | [`docs/diagrams/sequence.puml`](docs/diagrams/sequence.puml)           | US-1 zaznaczanie dostępności według założeń                   |
| Specyfikacja SDD          | [`.specify/spec.md`](.specify/spec.md)                                 | Jedno źródło prawdy o wymaganiach                             |

Wszystkie artefakty używają tych samych identyfikatorów (US-1…US-5, FR-1…FR-5, NFR-1…NFR-6), więc od historii można przejść do wymagania i diagramu.

## 🛠️ Technologie

![Python](https://img.shields.io/badge/Python-3.15-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3-000000?logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)

## 📐 Diagramy

Wszystkie diagramy leżą w [`docs/diagrams/`](docs/diagrams) i są zapisane w PlantUML.

| Diagram           | Plik                                                     | Co pokazuje                                                                     |
| ----------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Przypadki użycia  | [`use-case.puml`](docs/diagrams/use-case.puml)           | Aktorzy (Użytkownik, Uczestnik, Organizator) i 5 historii                       |
| Wymagania (SysML) | [`requirements.puml`](docs/diagrams/requirements.puml)   | FR-1…FR-5 i NFR z metrykami                                                     |
| Klasy (UML)       | [`classes.puml`](docs/diagrams/classes.puml)             | `User`, `Availability`, `Proposal`, `Vote` (klasa asocjacyjna), `Event`, `Cost` |
| Komunikacja (UML) | [`communication.puml`](docs/diagrams/communication.puml) | US-1: zalogowany uczestnik zaznacza albo odznacza dzień                         |
| Sekwencja (UML)   | [`sequence.puml`](docs/diagrams/sequence.puml)           | Ten sam scenariusz US-1 w kolejności czasowej                                   |

**Renderowanie:** w VS Code rozszerzeniem **PlantUML** (Alt+D). W ustawieniach rozszerzenia trzeba wybrać `Plantuml: Render` = `Local`, co wymaga zainstalowanej Javy. Diagramy klas, komponentów i komunikacji potrzebują też **Graphviza**. Bez niego dopisz pod `@startuml` linię `!pragma layout smetana`.

## 👥 Zespół

| Osoba               |
| ------------------- |
| _Tomasz Wiczyński_  |
| _Arkadiusz Woźniak_ |
| _Paweł Wołkowicz_   |

![alt text](image.png)
