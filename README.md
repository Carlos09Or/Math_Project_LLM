# Tutoría matemática offline con modelos de lenguaje pequeños

Investigación sobre cómo cambian la exactitud, el diagnóstico de errores y la calidad de las pistas cuando se comprime un modelo pequeño, y qué recursos exige ejecutarlo localmente, para **matemáticas de 3.er grado en Panamá**. Derivada de la propuesta AAAI-27 Undergraduate Consortium #52.

> **Estado: borrador de trabajo, sin resultados científicos.** Un piloto técnico (9 ítems sintéticos, un modelo, una sola pasada) comprobó que el *pipeline* funciona. Nada está validado por docentes ni aprobado por el mentor, y no se afirma alineación con el currículo vigente de MEDUCA.

## Contenido

| Carpeta | Qué hay |
|---|---|
| `index.html`, `*.html`, `assets/` | Sitio web estático del proyecto (sin dependencias ni compilación) |
| `docs/` | Documentos de trabajo: trazabilidad, auditoría, fuentes verificadas, diseño del dataset, protocolo v0.2, hoja de ruta, informe de la prueba de humo |
| `dataset/` | Borrador del dataset: 90 ítems (30 problemas base × resolver, diagnosticar y dar una pista), generador, validador y pruebas |
| `runner/` | Runner v0.2 contra Ollama local: código, pruebas, y las corridas del piloto técnico |
| `tools/` | `build_site_data.py`: genera los datos del sitio a partir de los archivos reales |

## Ver el sitio en local
Abre `index.html` con doble clic: los datos se cargan desde archivos `.js`, por lo que no hace falta servidor. Para regenerar los datos del sitio tras cambiar el dataset o las corridas:

```powershell
python tools/build_site_data.py
```

## Pruebas
```powershell
cd dataset ; python -I -m unittest discover -s tests -v
cd ../runner ; python -I -m unittest discover -s tests -v
python -I dataset/src/validate_dataset.py dataset/data/items.jsonl
```
Las pruebas del runner usan un Ollama simulado: verifican el código, no ningún modelo.

## Reproducir el piloto técnico
Requiere Ollama, el modelo `qwen3:0.6b-q4_K_M` y una GPU NVIDIA (opcional; también corre en CPU). Ver `runner/README.md`.

## Límites
- Dataset sintético, sin rúbrica ni revisión docente.
- Laboratorio en un portátil con GPU NVIDIA: **no valida dispositivos móviles**.
- La licencia de MathTutorBench no está resuelta; no se copian sus datos ni su código.
- Las licencias de Gemma y Llama 3.2 están sin leer.

## Licencia
Pendiente de definir por la autoría. Hasta entonces, todos los derechos reservados.
