# smoke_test_report.md — Prueba de humo (Hito 1): Qwen3-0.6B Q4_K_M

**Fecha:** 2026-11-14 (UTC) · **Estado:** **6 de 6 criterios cumplidos** (la ejecución sin red la hizo el investigador con `scripts/smoke_offline.ps1`; yo verifiqué los archivos generados).
**Qué es y qué no es:** una comprobación de que el *pipeline* funciona. Una pasada, sin calentamiento, 9 ítems sintéticos sin validación docente. **No es evidencia de calidad pedagógica, de latencia ni de cuantización.**

## Condiciones
| Elemento | Valor |
|---|---|
| Código | `starter_v0.2` (`runner-v0.2`, `prompt-v0.2`), copia corregida del starter v0.1 |
| Modelo | `qwen3:0.6b-q4_K_M`, digest `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435` (coincide con el registro) |
| Servidor | Ollama 0.40.16 en `127.0.0.1:11435`, modelos en `D:\canada_work\ollama-models` |
| Parámetros | `temperature 0`, `seed 42`, `num_ctx 2048`, `num_predict 256`, `think:false` |
| Equipo | RTX 3060 Laptop 6144 MiB (driver 581.42), i7-12700H, Windows 11 (10.0.26300), Python 3.12.6; conectado a corriente; ningún otro modelo cargado al iniciar |
| Dataset | `data/pilot_examples.jsonl` (v0.2, con tildes), SHA-256 `f6c7b3d6ec55e136…` |
| Red | Wi-Fi **activo** en las corridas de 3 y de 9 ítems; **apagado** en la corrida sin red (abajo) |

## Archivos (en `starter_v0.2/runs/`, conservados sin modificar)
> **Nota sobre la copia publicada (`runner/runs/` del repositorio):** los `.jsonl` y el archivo de evidencia de red son idénticos a los originales. En los `.manifest.json` se **redactaron las rutas locales** antes de publicar, por lo que su SHA-256 difiere del que figura abajo (que corresponde a los originales, conservados en el equipo del investigador).

| Corrida | Archivo | SHA-256 (16 primeros) |
|---|---|---|
| 3 ítems (prueba previa) | `20261114T001607Z_…_0ecde386.jsonl` / `.manifest.json` | `9d00eb275d0b9259` / `6c37430d24f05410` |
| **9 ítems (smoke test, con red)** | `20261114T001721Z_…_735deb4b.jsonl` / `.manifest.json` | `5c0add249b956193` / `5dd012c37e8633b1` |
| **9 ítems, SIN RED** | `20261114T002333Z_…_375a10ec.jsonl` / `.manifest.json` | `522d5771a6ac7d85` / `356fb7bf718f7c7c` |
| Evidencia de red | `20261114T002340Z_network_state.json` | `a34bf790dcf13627` |

## Criterios de aceptación (`experimental_protocol_v0.2.md` §9)
| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| 1 | Digest local coincide con `7df6b6e09427…` | **Cumplido** | `ollama.model_digest` en ambos manifiestos |
| 2 | 9 registros válidos, 0 errores, sin truncamiento | **Cumplido** | `counts = {items: 9, errors: 0, truncated: 0}`; `done_reason = stop` en los 9; máximo `eval_count` = 122 de 256 |
| 3 | `think:false` verificado | **Cumplido** | `reasoning` vacío y sin `<think>` en las 12 respuestas (3 + 9) |
| 4 | Manifiesto con hardware, versiones y modo de offload | **Cumplido** | `offload_first/last = gpu_only` (693 423 308 bytes en VRAM de 693 423 308); GPU y temperatura antes/después |
| 5 | Ejecución sin red demostrada | **Cumplido** | Wi-Fi `Disconnected` antes y después; pruebas de conexión a 1.1.1.1:443 y 8.8.8.8:53 fallidas antes y después; `offline_before` y `offline_after` verdaderos; 9 ítems, 0 errores, 0 truncadas, `gpu_only`, digest correcto (`runner_exit_code` 0). Limitación: la prueba de red es una sonda TCP a dos direcciones, no una captura de tráfico; el adaptador virtual de VirtualBox (solo anfitrión) seguía activo |
| 6 | Registro crudo conservado sin sobrescribir | **Cumplido** | Dos archivos distintos; el modo `'x'` impide sobrescribir |

## Observaciones (n = 9, una pasada: **no son conclusiones**)
1. **Arranque en frío:** el primer ítem de la primera corrida tardó 45 s (`prompt_eval` 36,8 s, `load` 7,3 s). Con el modelo ya cargado, los 9 ítems tardaron entre 0,23 y 0,69 s. Confirma que una pasada de calentamiento es obligatoria antes de medir tiempos (E-01).
2. **Repetibilidad con T=0 y semilla fija:** comparando las tres corridas, **la corrida de 9 ítems con red difirió en 001-R y 001-D** de las otras dos; las otras dos (la de 3 ítems y la de 9 sin red) coincidieron entre sí en esos dos ítems, y **los 9 ítems con red y sin red coinciden en 7 de 9**. Patrón observado: las dos corridas que empezaron con el modelo **recién cargado** (arranque en frío) produjeron las mismas respuestas; la que empezó con el modelo **ya cargado** por la corrida anterior difirió, y solo en los dos primeros ítems. **Hipótesis no probada** (3 corridas): el estado de caché o de carga cambia el resultado de los primeros ítems. No se puede atribuir la diferencia a la red. Conclusión práctica: **comprobar la repetibilidad y fijar un procedimiento de arranque** (descargar el modelo o hacer calentamiento) antes de comparar precisiones.
3. **`solve`:** los 3 ítems dieron la respuesta numérica correcta (24, 6, 87), comprobada a mano. Cuatro respuestas usan formato LaTeX (`$$ … $$`), poco apropiado para 3.er grado.
4. **`hint`:** en los 3 ítems la respuesta contiene `gold_answer` (detección con expresión regular sobre los dígitos). Es decir, el modelo reveló el resultado en las 3 pistas. Es una observación sobre 3 ítems con este modelo y este prompt, no una conclusión.
5. **`diagnose`:** respuestas incoherentes en 2 de 3 ítems (p. ej., afirma que «la respuesta correcta es 5» y luego calcula 6; en 003 lee la resta como suma). Sin rúbrica ni revisión humana: observación informal.
6. **GPU:** memoria usada 295 → 1097 MiB; temperatura 48 → 53 °C (corrida de 3) y 47 → 56 °C (corrida de 9).

## Consecuencias para las siguientes fases
- Calentamiento y repeticiones antes de cualquier medición de tiempo (F3).
- Verificación de repetibilidad como paso previo al análisis de calidad.
- Detector determinista de fugas en `hint` (M-06), pues el modelo suele revelar el resultado.
- `num_predict = 256` es suficiente para estos ítems (máximo 122 tokens); revisarlo al ampliar el dataset.
- El prompt de `hint` y el formato LaTeX son parte de lo que se debe decidir en el diseño del benchmark, no de la cuantización.

## Cierre del Hito 1
Los seis criterios están cumplidos. El Hito 1 demuestra que el *pipeline* corre en local, en GPU pura y sin internet, y deja registro crudo con manifiesto. **No demuestra calidad, latencia ni efecto de la cuantización.** Queda pendiente la aprobación del mentor y las decisiones D-01 a D-07 (`audit.md`).
