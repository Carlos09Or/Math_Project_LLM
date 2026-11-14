# Política del cero

## Qué decía el programa

Se revisó el PDF oficial (pp. 187-202). El 0 aparece en tres lugares, y en ninguno como restricción:

- La actividad de la semirrecta "inicia en el cero" (p. 190).
- El elemento neutro de la adición es una propiedad de contenido (p. 194).
- Los números con cifras en cero (por ejemplo, 3 040) caen dentro de "naturales menores de 10 000" y del valor posicional (p. 192).

No hay ninguna frase que excluya el cero como operando, ni que lo exija.

## Qué se hizo en la v0.1 y por qué se corrigió

La v0.1 tenía la regla global `M-GLOBAL-3` ("no se usa el 0 como operando"), que podía leerse como una restricción curricular. Se reemplazó por `M-ZERO-1`, que dice expresamente que:

- La exclusión de **operandos iguales a 0** es una comodidad temporal de diseño, no una restricción curricular.
- Los **ceros dentro de las cifras** sí se permiten y se incluyen a propósito.
- El **0 como elemento neutro** de la adición sí se permite.

## Qué hay en el benchmark v1

| Uso del cero | Estado | Ítems v1 |
|---|---|---|
| Ceros dentro de las cifras (4 050, 7 070, 3 005, 700 ÷ 100) | Incluido a propósito | 94 ítems involucran el cero en cifras, operandos o respuesta |
| Reagrupar a través de un cero (5 002 − 1 874) | Incluido en `SUB-10K`, nivel avanzado | ver `coverage_report.md` |
| Lectura de números con ceros ("siete mil setenta") | Incluido: `NAT-READ-WRITE` (6 ítems) | 6 |
| Cero como elemento neutro (`n + ___ = n`, respuesta 0) | Incluido en `ADD-PROPERTIES` | 3 (una familia) |
| Cero como operando de una operación (`n × 0`, `0 ÷ n`, `n − n`) | **No incluido** | 0 |
| Resultado igual a cero en una resta | **No incluido** (regla M-SUB-2: resultado >= 1) | 0 |

## Qué falta y qué recomendamos

- Hay cobertura limitada del cero **como valor**: solo la familia del elemento neutro. Los demás casos con cero son cifras dentro de números.
- Como el programa no lo excluye ni lo exige, incluir casos de cero como operando o resultado sería una decisión metodológica nuestra. Se propone un **estrato de cero** para el análisis posterior: unos 10 a 15 ítems nuevos (por ejemplo, restas con resultado 0, productos con factor 0, divisiones de 0) etiquetados como tal y reportados por separado.
- Esa decisión necesita la confirmación del investigador y, si es posible, de docentes. Hasta entonces no se añade nada.
