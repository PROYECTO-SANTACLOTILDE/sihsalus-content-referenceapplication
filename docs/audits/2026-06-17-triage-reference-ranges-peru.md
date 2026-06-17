# Auditoría de rangos de referencia de triaje

Fecha: 2026-06-17

## Fuente normativa peruana

La base normativa usada para signos vitales de triaje es la **NT 042-MINSA/DGSP-V.01, Norma Técnica de Salud de los Servicios de Emergencia**, aprobada por **R.M. N. 386-2006/MINSA**. La clasificación de prioridades define como Prioridad I los signos vitales anormales listados abajo.

Referencia operativa consultada:

- `https://www.sis.gob.pe/Portal/20140516_Prioridades.pdf`
- `http://bvs.minsa.gob.pe/local/dgsp/NT042emerg.pdf`

## Umbrales normativos aplicados

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

- Los umbrales de Prioridad I se modelan como límites `Critical low` / `Critical high`.
- `Absolute low` / `Absolute high` quedan como límites amplios de captura para no bloquear valores clínicamente posibles.
- La frecuencia respiratoria infantil se alinea a la norma separando `0 - <2 meses` y `2 meses - <1 año`.
- En gestantes se usan umbrales críticos compatibles con emergencia y riesgo obstétrico, pero la prioridad final debe calcularse en un formulario o módulo de triaje.
- Los criterios de gestante ahora comprueban que existan las observaciones previas de embarazo y edad gestacional antes de leer sus valores.

## Pendiente

Crear un formulario o flujo `TRIAJE-001` que calcule Prioridad I/II/III/IV usando la clasificación completa de la NT 042-MINSA/DGSP-V.01. Los rangos de referencia no deben reemplazar esa regla de negocio.
