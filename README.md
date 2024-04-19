# NiDUC 2 - Projekt
- Autorzy:
    - [Mateusz Głuchowski](https://github.com/hue1337)
    - [Marek Tutka](https://github.com/tuthino)

- Prowadzący:
    - dr inż. Dominik Żelazny

## Krótki opis projektu
Transmisja w systemie ARQ (Automatic Repeat Request). Zaimplementujemy system transmisji ARQ, z przynajmniej 2-ma róznymi kodami detekcyjnymi:
bit przystości, kody Hamminga, CRC8, CRC16. 
Stworzymy architekturę client-server, a do połączenia między nimi wykorzystamy protokół UDP,Wpływ parametrów sieci takich jak latency, drops, jitter postaramy się zasymulować wykorzystując emulator GNS3 lub CML.
Jeśli to się nie powiedzie, zaimplementujemy algorytm który będzie powodował dropy pakietów.

### Harmonogram:
- 2024-04-09 - Oddanie RNG 
- 2024-04-23 - Stworzenie MVP klienta oraz servera, działająca komunikacja pomiędzy nimi oparta na UDP
- 2024-05-07 - Stworzenie kodów detekcyjnych, ew. dodatkowych parametrów do symulacji
- 2024-05-21 - Działający system ARQ, wstępna symulacja oraz opis
- 2024-06-04 - Poprawienie błędów w aplikacji oraz sprawozdaniu
- 2024-06-18 - Przedstawienie wyników.

. 


## [LCG (Linear congruential generator)](https://github.com/Hue1337/NIDUC-2/blob/main/src/RandomNumberGenerator.py):
- Matematyczny wzór używany do generowania liczb _pseudolosowych_.

- Każda nastepna liczba _pseudolosowa_ jest zależna od poprzedniej.


    $$for\:i = 0, 1, 2,...$$
    $$R_{i+1} = (aR_i + C)\mod m$$


- Gdzie:
    - $a$ - stały mnożnik
    - $c$ - przyrost
    - $m$ - modulus, dodatnia liczba całkowita, która określa zakres liczb
    - $R_i$ - stały przyrost
    - $R_0$ - początkowa wartość,`seed` generowany na podstawie daty.

- Dodatkowe warunki:
    $$a > 0$$
    $$c \geq 0$$
    $$m > c$$
    $$m > R_0$$
    $$m-1 \geq R_i > 0$$

- Aby obliczyć odpowiadającą pseudolosową liczbę jednostajną, używamy nastpującego wzoru:

$$U_i = \frac{R_i}{m-1} $$



