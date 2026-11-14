# Rúbrica pedagógica v0.1 (borrador)

Identificador: `RUBRIC-PED-v0.1`. Estado: **propuesta del equipo, sin validación docente ni de MEDUCA**. Debe revisarse con docentes de tercer grado antes de usarse para sacar conclusiones.

## 1. Para qué sirve

Puntúa la calidad pedagógica de las respuestas de un modelo en las tareas B (diagnóstico de errores) y C (pistas). La tarea A (resolución) se puntúa solo con el verificador matemático (`score_math.py`); la exactitud matemática y la calidad pedagógica se reportan por separado y no se suman.

## 2. Qué dimensiones aplican en cada tarea

| Dimensión | Tarea A (resolver) | Tarea B (diagnosticar) | Tarea C (pista) |
|---|---|---|---|
| D1 Corrección matemática | Automática | Sí | Sí |
| D2 Diagnóstico | No aplica | Sí | Sí |
| D3 Claridad | No aplica | Sí | Sí |
| D4 Utilidad pedagógica | No aplica | Sí | Sí |
| D5 Orientación al aprendizaje | No aplica | No aplica | Sí |
| Máximo | n/a | 8 | 10 |

Regla: **no se penaliza revelar el resultado en la tarea A ni en la B**, porque esas tareas lo requieren. La restricción de no revelar la respuesta solo rige en la tarea C. Para comparar tareas se usa el porcentaje del máximo aplicable.

## 3. Descriptores (0, 1, 2)

### D1. Corrección matemática
Ausencia de errores numéricos o conceptuales en lo que dice el modelo.

- **0**: afirma algo matemáticamente falso que cambia la ayuda (por ejemplo, da por correcto un resultado erróneo, o corrige con un cálculo equivocado).
- **1**: un error menor que no altera el mensaje central (por ejemplo, un cálculo intermedio mal escrito que luego no se usa).
- **2**: todo lo que afirma es matemáticamente correcto.

### D2. Diagnóstico
Identifica el error o la dificultad observable del estudiante.

- **0**: no menciona el error, señala otro error distinto, o inventa un error en un trabajo correcto (en la tarea B de control).
- **1**: señala la zona general (la operación o el paso) pero no el punto exacto, o mezcla el error real con uno inventado.
- **2**: señala el punto exacto que se ve en el trabajo del estudiante, sin atribuirle razonamientos que no se pueden inferir. En el trabajo correcto, confirma que es correcto sin inventar errores.

### D3. Claridad
Lenguaje comprensible para tercer grado.

- **0**: vocabulario técnico o frases largas que un niño de 8 a 9 años no seguiría (por ejemplo, "minuendo", "algoritmo de reagrupación"), o mensaje confuso.
- **1**: se entiende, pero con alguna palabra difícil, demasiado texto o pasos desordenados.
- **2**: frases cortas, palabras de uso cotidiano, un solo mensaje principal.

### D4. Utilidad pedagógica
Da una ayuda concreta para que el estudiante avance.

- **0**: genérica ("piénsalo otra vez", "revisa tu trabajo") o no ayuda a avanzar.
- **1**: apunta a lo que hay que mirar, pero sin una acción concreta, o propone una acción poco adecuada.
- **2**: propone una acción concreta y adecuada al error (rehacer una columna, dibujar partes iguales, contar de 11 en 11).

### D5. Orientación al aprendizaje (solo tarea C)
Favorece que el estudiante razone y respeta la instrucción de no revelar la respuesta.

- **0**: revela el resultado final, o resuelve todo el problema paso a paso.
- **1**: no da el resultado final, pero da casi todo el trabajo (por ejemplo, el cálculo intermedio que decide el resultado) o ordena qué escribir sin pedir razonamiento.
- **2**: no revela el resultado, deja el último paso al estudiante y lo invita a pensar (pregunta, dibujo, comparación).

## 4. Decisiones difíciles

| Caso | Decisión |
|---|---|
| La pista dice "el resultado no es 6 240" | D5 = 1: descarta un valor pero no revela la respuesta. |
| La pista incluye el resultado entre paréntesis | D5 = 0. |
| La pista da un cálculo intermedio que ya contiene la respuesta | D5 = 0 si el estudiante solo tiene que copiar; D5 = 1 si aún debe razonar un paso. |
| La pista es una pregunta correcta pero muy genérica | D4 = 0 o 1 según si dirige la atención a una zona concreta. |
| El modelo confirma que un trabajo incorrecto está bien | D1 = 0 y D2 = 0. |
| El modelo dice que un trabajo correcto tiene un error | D1 = 0 y D2 = 0 (error inventado). |
| El modelo nombra bien el error, pero lo explica con una causa que el trabajo no muestra | D2 = 1: no se puede inferir esa causa del procedimiento visible. |
| Varias pistas distintas, todas correctas | Se puntúa la combinación; no hay una única respuesta válida. La respuesta de referencia es solo un ejemplo. |
| El modelo da dos pistas y una revela la respuesta | D5 = 0. |
| Respuesta correcta pero en inglés o con jerga de otro país | D3 = 0 o 1. Se anota "no es español de Panamá" en observaciones. |
| La pista usa reagrupar, que el programa no menciona explícitamente | No se penaliza el procedimiento por no estar en el programa; se anota para revisión docente. |

## 5. Respuestas no evaluables (NE)

Se marca `NE` y se excluye del promedio. Se reporta el recuento aparte.

- Vacía o solo espacios.
- Truncada antes de completar una idea que permita puntuar.
- No está en español.
- No trata el problema (se niega, cambia de tema, solo repite el enunciado).
- Contiene varias respuestas incompatibles entre sí sin indicar cuál vale.

Una respuesta con formato incorrecto (por ejemplo, sin la línea `VEREDICTO:`) pero con contenido evaluable **sí** se puntúa; el error de formato se reporta aparte.

## 6. Procedimiento de revisión humana

1. **Preparación**: se arman las hojas de revisión con la respuesta del modelo, el ítem y la rúbrica. Se ocultan el modelo, la cuantización y los parámetros. El orden es aleatorio, con semilla registrada.
2. **Calibración**: dos revisores puntúan 10 respuestas que no pertenecen a la muestra final, discuten y ajustan la interpretación de los descriptores. Los ajustes se anotan en este documento como una nueva versión.
3. **Doble anotación**: cada respuesta de la muestra la puntúan dos revisores de forma independiente. Un tercero resuelve los desacuerdos de 2 puntos o más en una dimensión, con una nota de motivo.
4. **Acuerdo**: se calcula el kappa ponderado cuadrático por dimensión y se reporta. No se fija un umbral de aceptación sin consultar a quienes asesoran el estudio; si el acuerdo es bajo, se revisan los descriptores en lugar de promediar.
5. **Automático como apoyo**: `leak_check` marca fugas posibles. Si marca `leak`, el revisor confirma D5 = 0 o lo cambia con una nota escrita. Los verificadores automáticos nunca reemplazan al revisor en D2-D5.
6. **Juez de lenguaje**: no se usa un único modelo como juez final. Un modelo puede servir como apoyo para priorizar casos, pero ninguna puntuación final depende solo de él.
7. **Registro**: cada hoja guarda `item_id`, `response_id`, `reviewer_id`, puntajes por dimensión, `NE` y observaciones. No se registran datos personales de estudiantes.
8. **Muestra**: en el piloto se revisan todas las respuestas. En v1 se propone una muestra estratificada por tarea, modelo y cuantización; el tamaño se decide después de ver la variabilidad del piloto.

## 6 bis. Dos precisiones de esta versión

1. **Equivalencia de fracciones (piloto independiente).** El indicador oficial dice "argumenta con ejemplos la equivalencia" (p. 201). El verificador automático solo comprueba la respuesta cerrada (sí/no o el numerador que falta). El argumento, si el modelo lo escribe, se puntúa solo con revisión humana: D1 (corrección), D3 (claridad) y D4 (utilidad). Hasta definir esa evaluación, ningún ítem de equivalencia entra al benchmark principal.
2. **Categoría del error (tarea B).** El prompt ofrece una lista cerrada de categorías (propuesta del benchmark, no de MEDUCA). La coincidencia de categoría es un indicador automático auxiliar. La descripción del error la puntúa el revisor en D2: un modelo puede acertar la categoría y describir mal el error, o al revés.

## 7. Qué viene de MathTutorBench y qué es propuesta nuestra

Fuente consultada: la página del proyecto, el README del repositorio y parte del artículo (Macina et al., EMNLP 2025). No se leyeron los apéndices.

**Lo que reporta MathTutorBench**
- Mide tres grupos de habilidades: experiencia matemática (resolver problemas, preguntas socráticas), comprensión del estudiante (corrección de la solución, ubicación y corrección del error) y capacidad pedagógica (generar andamiaje y seguir instrucciones pedagógicas).
- La capacidad pedagógica se puntúa con un modelo de recompensa que compara la respuesta con una de un docente humano. Ese modelo se entrenó con preferencias; el artículo describe cuatro principios (corrección, andamiaje en lugar de dar la respuesta, favorecer la autocorrección, no sobrecargar al estudiante) y toma criterios de MRBench como identificación y localización del error, orientación, capacidad de actuar, si revela la respuesta, coherencia, tono y naturalidad.
- Trata revelar la respuesta como algo indeseable.

**Lo que es propuesta de este benchmark**
- Las cinco dimensiones, la escala 0 a 2, los descriptores, los casos difíciles y el procedimiento de doble anotación.
- La adaptación a vocabulario de tercer grado de Panamá y la separación por tarea (no penalizar revelar en A y B).
- La puntuación manual: MathTutorBench usa un modelo de recompensa automático; aquí la fuente principal es la revisión humana.
- La correspondencia conceptual aproximada (D1 con corrección, D2 con identificación y localización del error, D4 con capacidad de actuar, D5 con orientación y revelar la respuesta) es una lectura nuestra, no una adopción de sus escalas.

Este documento no afirma que la rúbrica esté validada ni que sea equivalente a la de MathTutorBench.

## 8. Limitaciones

- No se ha probado con docentes ni con niños.
- Los descriptores de D3 asumen vocabulario típico de 8 a 9 años y deben calibrarse con docentes de Panamá.
- Los ejemplos de la §4 son decisiones nuestras, no un estándar.
- La rúbrica mide una respuesta aislada, no el diálogo completo; el proyecto de investigación contempla evaluar diálogos más largos en una fase posterior.
