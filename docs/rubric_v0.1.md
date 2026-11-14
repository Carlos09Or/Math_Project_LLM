# rubric_v0.1.md — Rúbrica de revisión humana (borrador)

**Versión:** `rubric_v0.1` · **Fecha:** 2026-11-14 · **Estado:** **borrador sin validación docente.** Fija criterios y ejemplos *antes* de revisar la muestra del piloto; no sustituye la aprobación del mentor ni la revisión de docentes.
**Fuente única:** `dataset/rubric/rubric_v0.1.json` (este documento y la página `rubrica.html` se generan de ahí).

## Qué es y qué no es
Una escala de 0 a 2, con ejemplos ancla, para que una persona puntúe lo que el corrector automático **no puede puntuar**: si un diagnóstico ubica bien el error, si una pista ayuda sin regalar el resultado, si no valida una respuesta falsa, si un niño de 3.er grado lo entendería. **No** puntúa la exactitud aritmética ni el veredicto «correcta/incorrecta»: eso lo hace el código.

## 1. Principios
1. **Criterios observables, escala 0–2 anclada.** Se reporta **por criterio**; no se suma un total entre criterios distintos.
2. **Los criterios son independientes aunque se solapen.** Una pista puede ser perfecta en H1 (no revela) y mala en H2 y H3; no se compensan.
3. **El código puntúa lo mecánico** (exactitud, veredicto, fuga del resultado, LaTeX, truncamiento); **la persona puntúa el resto.**
4. **No se usa un LLM como juez** de calidad pedagógica.
5. **Revisión ciega.** El evaluador no sabe qué modelo ni qué precisión produjo la respuesta. Sí ve el enunciado, la respuesta del estudiante, la respuesta correcta y el error observable del ítem.
6. **«NA» cuando no se puede juzgar.** No se rellena con 1.
7. **Todo se anota:** dudas, desacuerdos e incertidumbre se conservan; nada se descarta por incómodo.

## 2. Qué puntúa el código y qué la persona
| Medida | Quién | Cómo |
|---|---|---|
| Exactitud de la respuesta final (`solve`) | Código | Compara con la respuesta calculada |
| Veredicto «correcta/incorrecta» (`diagnose`) | Código | Compara con la verdad (sensibilidad y especificidad) |
| El resultado correcto aparece en la pista | Código | Detección de cifras; **la persona confirma** revelaciones implícitas (H1) |
| Uso de LaTeX, truncamiento, razonamiento visible | Código | Banderas |
| Todo lo demás (criterios de la sección 3) | **Persona** | Esta rúbrica |

## 3. Criterios y a qué respuestas se aplican
| Tarea | Criterios que se puntúan | Nº |
|---|---|---|
| `solve` | S1, X1, M1, E1 | 4 |
| `diagnose` con error | D1, D3, X1, M1, E1 | 5 |
| `diagnose` control (el estudiante acierta) | D2, D3, X1, M1, E1 | 5 |
| `hint` | H1, H2, H3, H4, X1, M1, E1 | 7 |

Resumen de los 11 criterios:

| Id | Criterio | Pregunta | Se aplica a |
|---|---|---|---|
| **S1** | Procedimiento correcto y mostrado | ¿La explicación plantea la operación correcta y muestra cómo se calcula? | resolver; todos los ítems |
| **X1** | Coherencia interna | ¿La respuesta se contradice a sí misma? | todas las tareas; todos los ítems |
| **M1** | Verdad matemática de lo que afirma | ¿Lo que afirma sobre cuentas, resultados y sobre la respuesta del estudiante es matemáticamente verdadero? | todas las tareas; todos los ítems |
| **E1** | Claridad apropiada a 3.er grado | ¿Un niño de 3.er grado podría leerlo y seguirlo? | todas las tareas; todos los ítems |
| **D1** | Localización del error | Cuando el estudiante se equivocó, ¿detecta el error y lo ubica? | diagnosticar; ítems con error |
| **D2** | Reconoce lo correcto sin inventar errores | Cuando el estudiante acertó, ¿lo reconoce sin inventar errores? | diagnosticar; controles (el estudiante acierta) |
| **D3** | No inventa la intención ni el razonamiento del estudiante | ¿Se limita a lo observable en la respuesta del estudiante? | diagnosticar; todos los ítems |
| **H1** | No revela el resultado | ¿La pista deja al estudiante el trabajo de llegar al resultado? | pista; todos los ítems |
| **H2** | Utilidad: orienta al lugar del error | ¿La pista ayuda a que el estudiante encuentre su error? | pista; todos los ítems |
| **H3** | No valida lo falso ni descalifica lo correcto | ¿La pista es honesta sobre la respuesta del estudiante? | pista; todos los ítems |
| **H4** | Una pista breve y graduada | ¿Es una pista, y no una lección? | pista; todos los ítems |

## 4. Descriptores y ejemplos ancla
Cada ejemplo es **real** (respuesta textual del modelo en la partición `dev`) o **sintético** (escrito a mano). Puntuación = nivel del criterio; el motivo explica por qué.

### **S1** · Procedimiento correcto y mostrado
*Aplica a:* resolver; todos los ítems. *Pregunta:* ¿La explicación plantea la operación correcta y muestra cómo se calcula?
*Lo automático:* La exactitud de la respuesta final la puntúa el código (no esta rúbrica).

| Nivel | Descriptor |
|---|---|
| **2** | Plantea la operación correcta y muestra un cálculo (pasos o resultado intermedio) correcto y coherente con la respuesta final. |
| **1** | Plantea la operación correcta pero no muestra cómo se calcula, o muestra el cálculo con un error menor que no cambia la respuesta final. |
| **0** | El procedimiento es incorrecto, no tiene relación con el problema o contradice la respuesta final. |

*Nota:* Si la respuesta final es incorrecta, S1 no puede ser 2.

| Ancla | Nivel | Procedencia | Respuesta | Por qué |
|---|---|---|---|---|
| A-S1-2 | 2 | real (dev) | Se reparten 87 pegatinas entre 4 estudiantes igualmente. Para resolver, dividimos 87 entre 4. El resultado es 21 pegatinas por estudiante. Al restar, 87 - 4*21 = 87 - 84 = 3. Por lo tanto, cada estudiante recibe 21 pegatinas y 3 sobran. /  / Respuesta final: cociente <21>, residuo <3> /no_think. | Muestra la división, el producto 4 × 21 = 84 y el residuo 87 − 84 = 3: cálculo correcto y coherente. |
| A-S1-1 | 1 | real (dev) | Una caja tiene 13 crayones. Para encontrar cuántos crayones hay en 6 cajas, multiplicamos 13 por 6. El procedimiento es multiplicar el número de crayones por el número de cajas. Respuesta final: 78 /no_think | Plantea la operación correcta (13 por 6) pero no muestra cómo se calcula. |
| A-S1-0 | 0 | real (dev) | Procedimiento:   / Primero, dividimos el número de crayones en una caja por 6. Luego, multiplicamos el resultado por 6.   /  / Respuesta final: 72 /no_think | El procedimiento es incorrecto (dividir y luego multiplicar) y da 72. |

### **X1** · Coherencia interna
*Aplica a:* todas las tareas; todos los ítems. *Pregunta:* ¿La respuesta se contradice a sí misma?

| Nivel | Descriptor |
|---|---|
| **2** | Todo lo que dice es compatible entre sí. |
| **1** | Tiene una inconsistencia menor o una frase confusa, pero lo esencial no se contradice. |
| **0** | Se contradice en lo esencial (p. ej., el veredicto dice «correcta» pero el texto dice que es incorrecta; el procedimiento da un resultado y la respuesta final otro). |

*Nota:* Se juzga la coherencia, no la verdad: una respuesta puede ser coherente y falsa.

| Ancla | Nivel | Procedencia | Respuesta | Por qué |
|---|---|---|---|---|
| A-X1-2 | 2 | real (dev) | Veredicto: incorrecta. El error es que no se multiplicó 13 por 6, sino que se multiplicó 13 por 68. | Veredicto y texto coinciden. Es coherente aunque su detalle sea falso (eso lo juzga M1 y D1, no X1). |
| A-X1-1 | 1 | sintético | Veredicto: incorrecta. El resultado de 13 × 6 es 78 y tú escribiste 68, que es casi igual y casi correcto. | Lo esencial (es incorrecta) no se contradice, pero «casi correcto» es una frase confusa. |
| A-X1-0 | 0 | real (dev) | Veredicto: correcta.   / Don Julio tenía 725 naranjas en su puesto del mercado. Vendió 348 naranjas.   / El número de naranjas que le quedan es 725 - 348 = 377.   / El estudiante calculó 423, lo que es incorrecto. El error es que no se realizó la resta correctamente. | El veredicto dice «correcta» y el texto dice que 423 «es incorrecto»: se contradice en lo esencial. |

### **M1** · Verdad matemática de lo que afirma
*Aplica a:* todas las tareas; todos los ítems. *Pregunta:* ¿Lo que afirma sobre cuentas, resultados y sobre la respuesta del estudiante es matemáticamente verdadero?
*Lo automático:* Parte (resultado final, veredicto) la detecta el código; aquí se juzga todo lo demás que afirma.

| Nivel | Descriptor |
|---|---|
| **2** | Todo lo que afirma es matemáticamente verdadero. |
| **1** | Afirma algo falso pero secundario o impreciso, sin afectar lo central. |
| **0** | Afirma como cierto algo matemáticamente falso y relevante (un cálculo falso, «es divisible» cuando no lo es, un resultado decimal inventado, dar por correcta una respuesta incorrecta). |

*Nota:* Se juzga lo afirmado, no el estilo.

| Ancla | Nivel | Procedencia | Respuesta | Por qué |
|---|---|---|---|---|
| A-M1-2 | 2 | real (dev) | Se reparten 87 pegatinas entre 4 estudiantes igualmente. Para resolver, dividimos 87 entre 4. El resultado es 21 pegatinas por estudiante. Al restar, 87 - 4*21 = 87 - 84 = 3. Por lo tanto, cada estudiante recibe 21 pegatinas y 3 sobran. /  / Respuesta final: cociente <21>, residuo <3> /no_think. | Todas las cuentas que muestra son verdaderas. |
| A-M1-1 | 1 | sintético | Multiplicamos 13 por 6. Como 13 es un número par, el resultado también es par. Respuesta final: 78 | El resultado es verdadero pero afirma algo falso secundario: 13 no es par. |
| A-M1-0 | 0 | real (dev) | Se reparten 87 pegatinas por igual entre 4 estudiantes. Para encontrar cuántas pegatinas recibe cada estudiante, dividimos 87 entre 4. El resultado es 21.5. No hay resto, ya que 87 es divisible por 4.  /  / Respuesta final: 21 <87>, 0 /no_think | Afirma «21.5» y «87 es divisible por 4», ambas falsas y centrales. |

### **E1** · Claridad apropiada a 3.er grado
*Aplica a:* todas las tareas; todos los ítems. *Pregunta:* ¿Un niño de 3.er grado podría leerlo y seguirlo?
*Lo automático:* El código solo registra si usa LaTeX o si está truncada.

| Nivel | Descriptor |
|---|---|
| **2** | Frases cortas y vocabulario y notación del programa de 3.er grado. |
| **1** | Comprensible con esfuerzo: algo de notación técnica aislada (p. ej. «$ … $»), frases largas o un término poco apropiado. |
| **0** | Notación o vocabulario inadecuados para 3.er grado (LaTeX o «$$», símbolos o términos fuera del programa) o un texto confuso o largo que un niño no seguiría. |

*Nota:* Los términos del programa (minuendo, sustraendo, cociente, residuo…) son apropiados. Restos como «/no_think» se anotan como artefacto y no bajan la puntuación salvo que impidan entender.

| Ancla | Nivel | Procedencia | Respuesta | Por qué |
|---|---|---|---|---|
| A-E1-2 | 2 | real (dev) | Don Julio tenía 725 naranjas en su puesto del mercado. Vendió 348 naranjas. Para encontrar cuántas le quedaron, restamos las naranjas vendidas de las naranjas iniciales:   / 725 - 348 = 377.   /  / Respuesta final: <377> | Frases cortas y la operación escrita en forma simple. |
| A-E1-1 | 1 | real (dev) | Don Julio tenía 725 naranjas en su puesto del mercado. Vendió 348 naranjas. Le quedan $ 725 - 348 = 377 $ naranjas. /  / Respuesta final: <377> | Comprensible, pero con notación técnica aislada («$ 725 - 348 = 377 $»). |
| A-E1-0 | 0 | real (dev) | Para resolver este problema, debes seguir estos pasos: /  / 1. **Divide 87 pegatinas entre 4 estudiantes**.   /    $$ /    87 \div 4 = 20 \text{ (cociente)} /    $$ /  / 2. **Resta el cociente al total de pegatinas**.   /    $$ /    87 - 20 \times 4 = 87 - 80 = 7 /    $$ /  / 3. **El cociente representa cómo se reparten las pegatinas**, y el residuo representa cómo se sobran.   /    $$ /    \text{Cociente: } 20, \quad \text{Residuo: } 7 /    $$ /  / **Respuesta final:**   / Cada estudiante recibe $20$ pegatinas y $7$ sobran. | Usa LaTeX («$$», «\div», «\text») y una lista de pasos que un niño de 3.er grado no seguiría. |

### **D1** · Localización del error
*Aplica a:* diagnosticar; ítems con error. *Pregunta:* Cuando el estudiante se equivocó, ¿detecta el error y lo ubica?
*Lo automático:* El código puntúa solo el veredicto «correcta/incorrecta».

| Nivel | Descriptor |
|---|---|
| **2** | Detecta el error y lo ubica con precisión: coincide en lo esencial con el error observable del ítem. |
| **1** | Detecta que hay un error pero no lo ubica, o lo describe de forma imprecisa o con un detalle incorrecto. |
| **0** | No detecta el error (dice que está bien), o señala un error que no existe, o culpa a una operación equivocada. |

*Nota:* Se compara con el «error observable» del ítem. Un veredicto «correcta» ante una respuesta errónea es siempre 0.

| Ancla | Nivel | Procedencia | Respuesta | Por qué |
|---|---|---|---|---|
| A-D1-2 | 2 | sintético | Veredicto: incorrecta. En 13 × 6, 3 × 6 = 18: se escribió el 8 pero no se sumó el 1 que se lleva a las decenas. | Detecta el error y lo ubica exactamente donde está. |
| A-D1-1 | 1 | real (dev) | Veredicto: incorrecta.   / El error es que no multiplica 13 por 6, sino que sumaba 13 en cada caja. La respuesta correcta sería 13 multiplicado por 6, lo que es 78. | Detecta que hay un error, pero lo describe mal («sumaba 13 en cada caja»): no coincide con el error observable (se omitió la llevada). |
| A-D1-0 | 0 | real (dev) | Veredicto: correcta.   / Don Julio le quedó 423 naranjas. | Dice «correcta» ante una respuesta errónea: no detecta el error. |

### **D2** · Reconoce lo correcto sin inventar errores
*Aplica a:* diagnosticar; controles (el estudiante acierta). *Pregunta:* Cuando el estudiante acertó, ¿lo reconoce sin inventar errores?
*Lo automático:* El código puntúa solo el veredicto.

| Nivel | Descriptor |
|---|---|
| **2** | Reconoce que es correcta sin inventar errores ni reservas infundadas. |
| **1** | Reconoce que es correcta pero añade dudas, correcciones o «errores» infundados. |
| **0** | Afirma que hay un error, o inventa uno, aunque el estudiante acertó. |

*Nota:* Solo se aplica a los controles (respuesta del estudiante correcta).

| Ancla | Nivel | Procedencia | Respuesta | Por qué |
|---|---|---|---|---|
| A-D2-2 | 2 | sintético | Veredicto: correcta. 13 × 6 = 78. | Reconoce lo correcto sin inventar errores. |
| A-D2-1 | 1 | sintético | Veredicto: correcta. Aunque quizás deberías revisar las decenas por si acaso, porque a veces hay errores ahí. | Reconoce que es correcta pero añade una duda infundada. |
| A-D2-0 | 0 | sintético | Veredicto: incorrecta. El error es que no se sumó el 1 que se lleva. | Inventa un error aunque la respuesta (78) es correcta. |

### **D3** · No inventa la intención ni el razonamiento del estudiante
*Aplica a:* diagnosticar; todos los ítems. *Pregunta:* ¿Se limita a lo observable en la respuesta del estudiante?

| Nivel | Descriptor |
|---|---|
| **2** | Describe solo lo observable (qué cifra o paso difiere) sin atribuir intención. |
| **1** | Atribuye al estudiante un proceso no observable (con o sin cautela), aunque sea plausible. |
| **0** | Atribuye con certeza al estudiante un razonamiento o proceso que no se puede observar y que además es falso o contradictorio. |

*Nota:* Principio de la propuesta: no inventar la intención del niño.

| Ancla | Nivel | Procedencia | Respuesta | Por qué |
|---|---|---|---|---|
| A-D3-2 | 2 | sintético | Veredicto: incorrecta. 68 y 78 se parecen, pero en las decenas hay un 6 en lugar de un 7: falta 1 decena. | Describe solo lo que se ve en la respuesta, sin atribuir intención. |
| A-D3-1 | 1 | sintético | Veredicto: incorrecta. Parece que se olvidó de sumar el 1 que se lleva. | Atribuye un proceso no observable (aunque con cautela y plausible). |
| A-D3-0 | 0 | real (dev) | Veredicto: incorrecta.   / El error es que no multiplica 13 por 6, sino que sumaba 13 en cada caja. La respuesta correcta sería 13 multiplicado por 6, lo que es 78. | Atribuye con certeza un proceso («sumaba 13 en cada caja») que no se observa y es contradictorio con el resultado. |

### **H1** · No revela el resultado
*Aplica a:* pista; todos los ítems. *Pregunta:* ¿La pista deja al estudiante el trabajo de llegar al resultado?
*Lo automático:* El código detecta si aparece el resultado correcto (el cociente en las divisiones); aquí se confirman revelaciones implícitas.

| Nivel | Descriptor |
|---|---|
| **2** | No revela el resultado ni lo hace trivial. |
| **1** | No lo escribe, pero lo hace casi inmediato (da el resultado de un paso que equivale a la respuesta, o una cifra de ella). |
| **0** | Incluye el resultado correcto, o resuelve el problema paso a paso hasta darlo. |

*Nota:* En un control, repetir la respuesta correcta del estudiante cuenta como revelar.

| Ancla | Nivel | Procedencia | Respuesta | Por qué |
|---|---|---|---|---|
| A-H1-2 | 2 | real (dev) | La respuesta correcta es 423 naranjas. | No escribe el resultado correcto (377). Obsérvese que esta pista es mala por otras razones (H2 y H3): los criterios son independientes. |
| A-H1-1 | 1 | sintético | Piensa en 13 + 13 + 13 + 13 + 13 + 13. El resultado termina en 8. | No escribe el resultado pero da su última cifra y la suma completa: casi lo revela. |
| A-H1-0 | 0 | real (dev) | La caja tiene 13 crayones. Para encontrar cuántos hay en 6 cajas, debes multiplicar 13 por 6. La respuesta correcta es 78. | Escribe «La respuesta correcta es 78». |

### **H2** · Utilidad: orienta al lugar del error
*Aplica a:* pista; todos los ítems. *Pregunta:* ¿La pista ayuda a que el estudiante encuentre su error?

| Nivel | Descriptor |
|---|---|
| **2** | Orienta al paso o concepto donde está el error (o, si el estudiante acertó, invita a verificar de forma significativa) sin hacer el trabajo. |
| **1** | Es relevante pero genérica («revisa tu operación»): no ubica dónde mirar. |
| **0** | No ayuda: es incorrecta, irrelevante, o repite una respuesta errónea. |

| Ancla | Nivel | Procedencia | Respuesta | Por qué |
|---|---|---|---|---|
| A-H2-2 | 2 | sintético | Mira las decenas: 2 − 4 no se puede. ¿Qué puedes hacer cuando el número de arriba es menor? | Ubica el paso donde está el error sin hacer el trabajo. |
| A-H2-1 | 1 | sintético | Revisa tu resta columna por columna. | Relevante pero genérica: no ubica dónde mirar. |
| A-H2-0 | 0 | real (dev) | La respuesta correcta es 423 naranjas. | No ayuda: repite la respuesta errónea del estudiante. |

### **H3** · No valida lo falso ni descalifica lo correcto
*Aplica a:* pista; todos los ítems. *Pregunta:* ¿La pista es honesta sobre la respuesta del estudiante?
*Lo automático:* El código NO detecta esto: es un fallo observado en los datos.

| Nivel | Descriptor |
|---|---|
| **2** | No valida lo falso ni descalifica lo correcto. |
| **1** | Es ambigua sobre la respuesta del estudiante: puede leerse como una validación. |
| **0** | Da por correcta una respuesta errónea (o por errónea una correcta). |

| Ancla | Nivel | Procedencia | Respuesta | Por qué |
|---|---|---|---|---|
| A-H3-2 | 2 | sintético | Mira el residuo: ¿puede sobrar 7 cuando estás repartiendo entre 4? | No valida ni descalifica; orienta. |
| A-H3-1 | 1 | sintético | Tu respuesta se ve bien; solo revisa los números una vez más. | Ambigua: puede leerse como una validación de una respuesta errónea. |
| A-H3-0 | 0 | real (dev) | La respuesta correcta es: **cociente 20, residuo 7**. | Da por correcta «cociente 20, residuo 7», que es errónea (el residuo es mayor que el divisor). |

### **H4** · Una pista breve y graduada
*Aplica a:* pista; todos los ítems. *Pregunta:* ¿Es una pista, y no una lección?
*Lo automático:* El código solo registra la longitud.

| Nivel | Descriptor |
|---|---|
| **2** | Una pista breve (idealmente una o dos frases) que deja trabajo al estudiante. |
| **1** | Varias indicaciones a la vez, o más larga de lo necesario para una pista. |
| **0** | No es una pista: resuelve el problema completo o da una lista larga de pasos. |

| Ancla | Nivel | Procedencia | Respuesta | Por qué |
|---|---|---|---|---|
| A-H4-2 | 2 | sintético | Mira las decenas: ¿se puede hacer 2 − 4? | Una sola indicación, breve, que deja trabajo al estudiante. |
| A-H4-1 | 1 | sintético | Revisa las unidades. Luego revisa las decenas. Después mira si pediste prestado. Por último suma para comprobar. | Varias indicaciones a la vez: más que una pista. |
| A-H4-0 | 0 | real (dev) | Para resolver este problema, debes seguir estos pasos: /  / 1. **Divide 87 pegatinas entre 4 estudiantes**.   /    $$ /    87 \div 4 = 20 \text{ (cociente)} /    $$ /  / 2. **Resta el cociente al total de pegatinas**.   /    $$ /    87 - 20 \times 4 = 87 - 80 = 7 /    $$ /  / 3. **El cociente representa cómo se reparten las pegatinas**, y el residuo representa cómo se sobran.   /    $$ /    \text{Cociente: } 20, \quad \text{Residuo: } 7 /    $$ /  / **Respuesta final:**   / Cada estudiante recibe $20$ pegatinas y $7$ sobran. | Resuelve el problema completo en tres pasos, con cuentas y notación larga: no es una pista. |


## 5. Casos difíciles
- **Respuesta truncada:** se puntúa lo que se ve y se marca «truncada»; si impide juzgar, **NA**.
- **Respuesta vacía:** no se puntúa (NA) y se anota.
- **Otro idioma:** E1 = 0 y se anota.
- **Artefactos** como `/no_think` o `<377>`: se anotan; no puntúan salvo que impidan entender.
- **Repeticiones distintas:** se revisa la repetición 1 y se anota si las otras difieren.
- **Duda entre dos niveles:** se elige el **menor** y se anota la duda; si no se puede decidir, **NA**.
- **Posible error del ítem** (el enunciado, la respuesta del estudiante o la respuesta correcta parecen mal): no se puntúa, se anota «posible error del ítem» y se informa para corregir el dataset.

## 6. Procedimiento de revisión
**6.1 Calibración (antes de tocar el piloto).** El evaluador puntúa, sin mirar los ejemplos ancla, las **27 respuestas reales de la partición `dev`** (`results/scorer_validation_dev/`: 3 problemas × 3 precisiones × 3 tareas). Se compara con los anclas aplicables. Si la coincidencia exacta es menor del **80 % por criterio**, se discute y se ajusta la rúbrica (versión `v0.2`). Las respuestas de calibración **no** entran en el análisis.

**6.2 Muestra (propuesta; tamaño pendiente del mentor, D-03).** *Núcleo:* **9 problemas** del piloto (por operación: 2 con error y 1 control), elegidos con semilla fija, × 3 tareas × 3 precisiones = **81 respuestas** (repetición 1). Se revisan los **mismos problemas en las tres precisiones**, para comparar de forma emparejada. *Completa:* las 243 respuestas de la repetición 1. Tiempo estimado (a confirmar en la calibración): ~2 min por `solve`, ~2,5 por `diagnose` y ~3,5 por `hint`: **≈ 3,6 h** el núcleo y ≈ 11 h la muestra completa.

**6.3 Hoja de revisión ciega.** Una fila por respuesta, en **orden aleatorio**, con identificador opaco; sin modelo ni precisión. Campos: `review_id`, `task`, enunciado, respuesta del estudiante, respuesta correcta, error observable, respuesta a puntuar, una columna por criterio aplicable (0, 1, 2 o NA), `duda`, `posible_error_del_item`, `nota`, `evaluador`. La clave que enlaza cada `review_id` con su modelo se guarda **aparte** y no se abre hasta terminar.

**6.4 Doble anotación.** Un segundo evaluador (**docente de primaria, idealmente**) puntúa **al menos un tercio** de la muestra (27 respuestas del núcleo), sin ver las notas del primero. Se reporta, por criterio: % de acuerdo exacto, % dentro de ±1 y kappa ponderado cuadrático (con la advertencia de que con ~27 respuestas es inestable), más la tabla de desacuerdos.

**6.5 Resolución.** Se discuten los desacuerdos. La puntuación original se **conserva** y se añade la consensuada; la incertidumbre (NA, dudas) se reporta.

**6.6 Análisis.** Por criterio y por tarea; comparación **emparejada por ítem** entre precisiones, con los mismos intervalos por problema base que el piloto (`pilot_run_plan.md`). **No se suman criterios** ni se declara una precisión «mejor» sin intervalos.

**6.7 Congelación.** La rúbrica se congela **antes** de revisar la muestra. Cualquier cambio posterior es una versión nueva y se reportan ambas.

## 7. Qué debe validar un docente
- Que los 11 criterios sean los que importan a un maestro de 3.er grado, y que los descriptores de 0/1/2 sean claros.
- Los ejemplos ancla **sintéticos** (los escribió el autor, no son respuestas de un modelo).
- El vocabulario de E1: qué términos y notación son apropiados para 3.er grado.
- Qué perfiles de docentes participan (pregunta abierta al mentor): idealmente al menos dos docentes de primaria con experiencia en matemática de 3.er grado.

## 8. Limitaciones
- **Borrador sin validación docente.** Los ejemplos sintéticos no son respuestas de modelos.
- Los anclas **reales** provienen de **3 problemas de `dev`** con el prompt `prompt-v0.3` (no el congelado): ilustran calidad, no formato. **No hay anclas reales de controles** (en `dev` no hay controles); los de D2 son sintéticos.
- **11 criterios es mucho** y varios se solapan (M1, H3 y D1 coinciden en «dar por correcta una respuesta errónea»). Tras la calibración puede ser razonable fusionar algunos; por eso se puntúan por separado y se analizan con cuidado.
- No mide si una pista **funciona de verdad con un niño**: eso exigiría estudios con estudiantes, fuera de alcance (y requeriría consentimiento y evaluación ética).

