# Auditoria OCL - 2026-07-09

## Alcance

Se revisaron las versiones publicadas de los sources OCL de la organizacion `SIHSALUS` usadas por el content package y se regeneraron los ZIPs bundleados desde los exports vigentes. El repositorio mantiene los exports separados por orden de carga: primero conceptos (`00` a `14`) y luego mappings (`50` a `64`).

## Versiones publicadas vigentes

| Source | Version | Conceptos | Mappings |
| --- | --- | ---: | ---: |
| `medicamentos` | `2026-06-30` | 1001 | 17 |
| `procedimientos` | `2026-06-30` | 12311 | 12331 |
| `diagnosis` | `2026-06-30` | 13484 | 0 |
| `laboratorio` | `2026-06-30` | 212 | 1044 |
| `inmunizaciones` | `2026-06-30` | 22 | 60 |
| `prestacionales` | `2026-06-30` | 66 | 65 |
| `geografia` | `2026-06-30` | 196 | 364 |
| `etnias` | `2026-06-30` | 62 | 64 |
| `seguros` | `2026-06-30` | 14 | 20 |
| `religiones` | `2026-06-30` | 12 | 24 |
| `sihsalus` | `2026-06-30-02` | 4441 | 5458 |
| `lenguas` | `2026-06-30-02` | 63 | 121 |
| `ocupaciones` | `2026-06-30-02` | 12 | 11 |
| `estado-civil` | `2026-06-30` | 6 | 8 |
| `educacion` | `2026-06-30` | 12 | 13 |

Total bundleado: 31914 conceptos OCL.

## ZIPs refrescados

Solo se reemplazaron los ZIPs con diferencias reales de contenido, ignorando cambios triviales de `export_time`:

- `01_SIHSALUS_procedimientos_concepts_2026-06-30.zip`
- `51_SIHSALUS_procedimientos_mappings_2026-06-30.zip`
- `03_SIHSALUS_laboratorio_concepts_2026-06-30.zip`
- `53_SIHSALUS_laboratorio_mappings_2026-06-30.zip`
- `56_SIHSALUS_geografia_mappings_2026-06-30.zip`
- `60_SIHSALUS_sihsalus_mappings_2026-06-30-02.zip`
- `61_SIHSALUS_lenguas_mappings_2026-06-30-02.zip`
- `12_SIHSALUS_ocupaciones_concepts_2026-06-30-02.zip`
- `62_SIHSALUS_ocupaciones_mappings_2026-06-30-02.zip`

Nota operativa: el source `ocupaciones` publicado actualmente por OCL contiene 12 conceptos y 11 mappings. El ZIP previamente bundleado en este repo contenia 448 conceptos bajo el mismo version ID `2026-06-30-02`; esos conceptos granulares CIUO-08 tenian nombres en ingles como parte del rotulo. El refresh deja el content package alineado con el estado publicado actual de OCL, pero el equipo debe validar si el catalogo funcional de ocupacion requiere reintroducir niveles granulares ya traducidos.

## Cobertura de formularios

Se cruzaron 110 formularios AMPATH contra los conceptos bundleados en OCL:

- Referencias unicas de conceptos en formularios: 1713.
- Referencias sin concepto bundleado: 0.

## Cobertura de nombres en espanol

Conceptos activos revisados: 31912.

Brecha encontrada:

| Source | ID OCL | UUID OpenMRS (`external_id`) | Nombre actual | Observacion |
| --- | --- | --- | --- | --- |
| `sihsalus` | `4306` | `30de01cb-1457-50dc-80c1-5a88a7a2e9b7` | `Fetal lie` | No tiene nombre activo en locale `es`; debe corregirse en OCL como `Situacion fetal` o el termino clinico aprobado por el equipo. |

No se modifica OCL remoto desde este repo; la correccion debe publicarse como nueva version del source OCL y luego re-exportarse.
