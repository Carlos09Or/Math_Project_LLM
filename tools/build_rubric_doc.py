"""Genera docs/rubric_v0.1.md a partir de dataset/rubric/rubric_v0.1.json (fuente única de criterios y ejemplos ancla).

Así el documento y la página web no pueden divergir. El procedimiento y las reglas están en este script (PROCEDIMIENTO).
No sobrescribe: borra docs/rubric_v0.1.md si quieres regenerarlo.
Uso:  python tools/build_rubric_doc.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / 'dataset' / 'rubric' / 'rubric_v0.1.json'
OUT = ROOT / 'docs' / 'rubric_v0.1.md'
TASK = {'solve': 'resolver', 'diagnose': 'diagnosticar', 'hint': 'pista', 'todas': 'todas las tareas'}
APPLIES = {'todos': 'todos los ítems', 'con_error': 'ítems con error', 'control': 'controles (el estudiante acierta)'}


def esc(s):
    return str(s).replace('\n', ' / ').replace('|', '\\|')


HEAD = """# rubric_v0.1.md — Rúbrica de revisión humana (borrador)

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
"""

PROCEDIMIENTO = """
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
"""


def main():
    r = json.loads(SRC.read_text(encoding='utf-8'))
    L = [HEAD.rstrip('\n')]
    for c in r['criteria']:
        L.append(f"| **{c['id']}** | {c['name']} | {c['question']} | {TASK[c['task']]}; {APPLIES[c['applies_to']]} |")
    L.append('\n## 4. Descriptores y ejemplos ancla')
    L.append('Cada ejemplo es **real** (respuesta textual del modelo en la partición `dev`) o **sintético** (escrito a mano). Puntuación = nivel del criterio; el motivo explica por qué.\n')
    for c in r['criteria']:
        L.append(f"### **{c['id']}** · {c['name']}")
        L.append(f"*Aplica a:* {TASK[c['task']]}; {APPLIES[c['applies_to']]}. *Pregunta:* {c['question']}")
        if c.get('automated'):
            L.append(f"*Lo automático:* {c['automated']}")
        L.append('\n| Nivel | Descriptor |\n|---|---|')
        for lv in '210':
            L.append(f"| **{lv}** | {c['levels'][lv]} |")
        if c.get('notes'):
            L.append(f"\n*Nota:* {c['notes']}")
        L.append('\n| Ancla | Nivel | Procedencia | Respuesta | Por qué |\n|---|---|---|---|---|')
        for a in sorted((x for x in r['anchors'] if x['criterion'] == c['id']), key=lambda x: -x['level']):
            prov = 'real (dev)' if a['provenance'] == 'real' else 'sintético'
            L.append(f"| {a['id']} | {a['level']} | {prov} | {esc(a['response'])} | {esc(a['rationale'])} |")
        L.append('')
    L.append(PROCEDIMIENTO)
    if OUT.exists():
        raise SystemExit(f'Ya existe {OUT}; bórralo para regenerarlo.')
    OUT.write_text('\n'.join(L) + '\n', encoding='utf-8', newline='\n')
    print('generado', OUT.name, '-', len(r['criteria']), 'criterios,', len(r['anchors']), 'anclas')
    return 0


if __name__ == '__main__':
    sys.exit(main())
