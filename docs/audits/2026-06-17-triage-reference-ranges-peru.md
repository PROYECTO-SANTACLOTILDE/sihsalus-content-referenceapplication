# Auditoría de rangos de referencia de triaje

Fecha: 2026-06-17
Actualización de operadores y límites técnicos: 2026-07-16

## Fuente normativa peruana

La **NT 042-MINSA/DGSP-V.01, Norma Técnica de Salud de los Servicios de Emergencia**,
aprobada por **R.M. N. 386-2006/MINSA**, sustenta únicamente los umbrales `Critical`
de emergencia enumerados abajo. No es la fuente de los rangos `Normal`, la antropometría ni el
registro longitudinal de signos vitales del chart.

Referencias consultadas:

- `https://www.gob.pe/institucion/minsa/informes-publicaciones/353462-norma-tecnica-de-salud-de-los-servicios-de-emergencia-nt-n-042-minsa-dgsp-v-01`
- `https://cdn.www.gob.pe/uploads/document/file/417851/117933904798456740620191106-32001-yhk5it.pdf?v=1573077740`
- `https://www.sis.gob.pe/Portal/20140516_Prioridades.pdf`
- `http://bvs.minsa.gob.pe/local/dgsp/NT042emerg.pdf`

## Umbrales normativos de referencia

Adulto:

- Frecuencia cardiaca `< 50/min` o `> 150/min`.
- Presión arterial sistólica `< 90 mmHg` o `> 220 mmHg`.
- Presión arterial diastólica `> 110 mmHg` o `30 mmHg` sobre basal.
- Frecuencia respiratoria `< 10/min` o `> 35/min`.

Pediátrico lactante:

- Frecuencia cardiaca `<= 60/min` o `>= 200/min`.
- Presión arterial sistólica `< 60 mmHg`.
- Frecuencia respiratoria `>= 60/min` hasta 2 meses.
- Frecuencia respiratoria `>= 50/min` desde 2 meses hasta 1 año.
- Saturación de oxígeno `<= 85%`.

Pediátrico preescolar:

- Frecuencia cardiaca `<= 60/min` o `>= 180/min`.
- Presión arterial sistólica `< 80 mmHg`.
- Frecuencia respiratoria `> 40/min` sin fiebre.
- Saturación de oxígeno `<= 85%`.

## Decisión de implementación

`conceptreferencerange` no calcula prioridad de triaje completa. Solo marca rangos para conceptos numéricos. Por eso:

- Los umbrales numéricos de Prioridad I se modelan como alertas `Critical low` / `Critical high`;
  no se afirma equivalencia con la clasificación completa.
- Los consumidores SIHSALUS comparan estos campos de forma inclusiva (`<=` y `>=`). Como los
  conceptos de frecuencia, presión y saturación se capturan como enteros, los operadores estrictos
  de la norma se codifican desplazando una unidad la frontera almacenada:

  | Regla de la NT 042 | Campo inclusivo almacenado |
  | --- | --- |
  | Adulto: FC `<50` / `>150` | `Critical low=49` / `Critical high=151` |
  | Adulto: PAS `<90` / `>220` | `Critical low=89` / `Critical high=221` |
  | Adulto: PAD `>110` | `Critical high=111` |
  | Adulto: FR `<10` / `>35` | `Critical low=9` / `Critical high=36` |
  | Lactante: PAS `<60` | `Critical low=59` |
  | Preescolar: PAS `<80` | `Critical low=79` |
  | Preescolar: FR `>40` | `Critical high=41` |

  Los límites que la norma expresa con `<=` o `>=` conservan el mismo número: FC pediátrica,
  FR del lactante y SpO2 pediátrica.
- `Absolute low` / `Absolute high` replican, lado por lado, los límites técnicos del
  `ConceptNumeric` incluido en el export OCL. Quedan vacíos cuando el concepto no define ese lado;
  no se derivan de los intervalos normales ni de la NT 042.
- La frecuencia respiratoria infantil se alinea a la norma separando `0 - <2 meses` y `2 meses - <1 año`.
- Las 26 filas rotuladas como `gestante` **no están operativas**. Sus criterios llaman
  `getValueBoolean()` sobre `Actualmente embarazada` (`abaf7d91-...`), pero el export OCL lo
  publica como datatype `N/A`; OpenMRS Core devuelve `null` para esa llamada. Es una deuda
  preexistente en `main`, descubierta por esta auditoría, no una regresión introducida por este PR.
- Esas mismas filas consultan `Edad gestacional` (`0f053bc0-...`), concepto que no escribe ningún
  formulario bundleado. Siete formularios obstétricos escriben en cambio
  `Edad gestacional (semanas actuales)` (`1e35f0dd-...`). Ambos conceptos tienen mapping
  `SAME-AS` a SNOMED CT `57036006`, pero OpenMRS no los trata como la misma pregunta.
- El rango no representa la alternativa de PAD `30 mmHg` sobre el basal ni la condición
  “sin fiebre” de la FR preescolar; el módulo de emergencia debe evaluar esos contextos y el resto
  de criterios de Prioridad I de forma explícita.
- OpenMRS Core 2.8.7 combinaría campo por campo los límites más estrictos si coincidieran el rango
  por edad y uno obstétrico. Hoy no sucede porque los 26 criterios obstétricos son inertes. Antes de
  activarlos también se debe resolver `Critical low == Normal low == 90` en las tres bandas de PAS:
  Core clasifica `90` como `NORMAL` por orden de evaluación, mientras los helpers actuales del
  frontend prueban crítico primero.
- Cada llamada a `$fn.getLatestObs` ejecuta una consulta de observaciones. Si solo se sustituyeran
  los conceptos sin rediseñar el criterio, las tres bandas de cada uno de los seis signos vitales
  comunes pueden producir hasta 84 búsquedas de Obs por resolución; hace falta un contrato de
  episodio o contexto calculado una vez por request.

## Pendiente

Implementar en el módulo embebido de emergencia un flujo que calcule Prioridad I/II/III/IV usando
la clasificación completa de la NT 042-MINSA/DGSP-V.01. No se agregará un formulario JSON al
content package para este flujo. Los rangos de referencia no deben reemplazar esa regla de negocio.

Antes de considerar definitivo el catálogo, corregir y republicar la terminología de embarazo,
unificar el concepto productor/consumidor de edad gestacional, decidir el borde PAS `90`, hacer
conscientes de fecha las bandas etarias y definir el inicio/cierre del episodio obstétrico. Un
registro retrospectivo o un embarazo sin cierre explícito no debe seleccionar rangos del contexto
equivocado.

Este candidato estrecha `Absolute high` en 60 filas para alinearlo con los `ConceptNumeric` actuales
(PAS `250`, PAD `150`, FR `99`, FC `230`, temperatura `47`). Antes de desplegar sobre una base con
datos se debe contar observaciones históricas por encima de esos límites. No se borran al importar
metadata, pero una edición o revalidación posterior podría rechazarlas.
