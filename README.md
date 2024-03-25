# NiDUC 2 - Projekt
- Autorzy:
    - [Mateusz Głuchowski](https://github.com/hue1337)
    - [Marek Tutka](https://github.com/tuthino)

- Prowadzący:
    - dr inż. Dominik Żelazny

## [LCG (Linear congruential generator)](https://github.com/Hue1337/NIDUC-2/blob/main/src/RandomNumberGenerator.py):
- Rekurencyjny algorytm do generowania liczb pseudolowych.

- Każda nastepna liczba _pseudolosowa_ jest zależna od poprzedniej.


    $$for\:i = 0, 1, 2,...$$
    $$R_{i+1} = (aR_i + C)\:mod\:m$$


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



