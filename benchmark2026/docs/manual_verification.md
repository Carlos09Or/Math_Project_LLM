# Verificación independiente de los errores estudiantiles

## El problema

El código que genera el trabajo incorrecto de un estudiante (`error_rules.py`) no debe ser el mismo que lo declara correcto. Antes, el validador reaplicaba la regla del generador: coincidir ahí no probaba nada independiente.

## Qué se hizo

1. **Módulo independiente.** `independent_check.py` no importa `error_rules.py`, `math_core.py` ni `constraints.py`. Reimplementa:
   - la solución de cada tipo de problema (con `Fraction`, división entera y comparación cruzada de fracciones);
   - el valor que escribe un estudiante con cada tipo de error, con fórmula cerrada (por ejemplo, omitir la primera llevada baja el total en 10^(k+1));
   - la categoría de cada tipo de error (tabla propia);
   - la verdad aritmética de cada igualdad que aparece en el trabajo del estudiante.
2. **Tres implementaciones de la respuesta correcta.** `math_core` (Python exacto), `compute_sympy` (SymPy, con otros algoritmos) y `independent_check.solve`. El validador exige que las tres coincidan.
3. **El validador usa solo lo independiente** para decidir si el error del estudiante es coherente: `validate_dataset.py` llama a `independent_check.audit_item` y no reaplica la regla del generador.
4. **Verdad aritmética del trabajo visible.** Cada igualdad del procedimiento tiene que ser aritméticamente verdadera (el error es conceptual, no un desliz de cálculo). Cada igualdad del enunciado final es falsa si el trabajo es incorrecto y verdadera si es correcto.
5. **Vectores calculados a mano.** `tests/golden_vectors.json` guarda 33 casos con su cálculo paso a paso. Las pruebas exigen que el generador y las fórmulas independientes coincidan con ellos.
6. **Pruebas aleatorias.** 3 000 entradas aleatorias comparan las reglas del generador con las fórmulas independientes.
7. **Mutaciones.** Seis pruebas corrompen un ítem (valor del estudiante, categoría, aritmética del procedimiento, respuesta guardada, control con valor equivocado, trabajo "incorrecto" que en realidad es correcto) y comprueban que la auditoría independiente lo detecta.

## Límites

- **Las tres implementaciones las escribió la misma persona (yo, Claude) con la misma comprensión.** Si esa comprensión tiene un error conceptual, las tres pueden compartirlo. La independencia es de código, no de criterio.
- Las **fórmulas y los vectores a mano** son mi cálculo. No los ha repasado una persona.
- La **clasificación de cada error** (por ejemplo, llamar "procedimental" a omitir una llevada) es una propuesta del benchmark. Ninguna comprobación automática puede validarla.

## Qué recomendamos que haga una persona (unos 30 minutos)

1. Repasar a mano los 33 vectores de `tests/golden_vectors.json` (cada uno trae su cálculo).
2. Elegir 20 ítems de diagnóstico al azar de `data/benchmark_v1.jsonl` y comprobar con lápiz que el error descrito es el que muestra el procedimiento.
3. Discutir con un docente si las categorías de error tienen sentido pedagógico.

## Cálculos a mano de ejemplo

| Regla | Entrada | Cálculo | Resultado del estudiante |
|---|---|---|---|
| Llevada omitida | 2 458 + 3 792 | 8+2=10 (0, llevo 1 y se pierde); 5+9=14 (4, llevo 1); 4+7+1=12 (2, llevo 1); 2+3+1=6 | 6 240 (lo correcto: 6 250) |
| Resta del menor al mayor | 5 117 − 2 256 | \|7−6\|=1; \|1−5\|=4; \|1−2\|=1; \|5−2\|=3 | 3 141 (lo correcto: 2 861) |
| Residuo mayor que el divisor | 47 ÷ 9 | 9×4=36; 47−36=11 (11 ≥ 9) | cociente 4, residuo 11 (correcto: 5 y 2) |
| Ceros de más o de menos | 34 × 100 | ×100 agrega 2 ceros; el estudiante agrega 1 | 340 (lo correcto: 3 400) |
| Denominadores sumados | 1/5 + 3/5 | 5+5=10 | 4/10 (lo correcto: 4/5) |
