# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Corregido
- Agrega `Get Concept Sources` al rol `Admision` para que FHIR pueda cargar los datos existentes al editar un
  paciente, evitando que la pantalla quede vacía por el error `HAPI-0389`.
- Agrega `Get Concepts` al rol `Admision` para cargar los conjuntos codificados de ocupación, idioma, religión,
  grado de instrucción y etnia durante el registro de pacientes, y valida que conserve `Add Patients`,
  `Edit Patients`, `Get Patient Identifiers` y `Edit Patient Identifiers`; ninguno de estos permisos otorga acceso
  de gestión de conceptos.

### Agregado
- Agrega validaciones clínicas de regresión para CRED-001, 009, 010, 011, 015, 026 y 027: exige edad/altitud en
  anemia, trazabilidad de instrumentos resumidos, antropometría escolar y decisiones de desarrollo por edad.
- Extiende la validación CI de OCL para rechazar mappings sin extremos, fuentes destino incompletas, referencias
  internas no bundleadas y colisiones de nombres que puedan dejar un concepto sin nombre `FULLY_SPECIFIED`.
- Publica los concepts de formulario que faltaban para inmunizaciones, referencias, acompañamiento, PPL/PRU, personal de parto, estado de ecografía y plan de parto; agrega las opciones de seguro SIS y particular sin reutilizar conceptos de otras preguntas.
- Extiende la validación CI de formularios para resolver conceptos contra todos los ZIP OCL, comprobar `Q-AND-A` entre sources, detectar respuestas repetidas o autorreferenciales, datatypes incompatibles, renderers no soportados, expresiones con IDs inexistentes y discordancias de encounter type.
- Agrega `CIEL 170800 - Procedure status` con UUIDs OpenMRS canónicos, ocho respuestas `Q-AND-A` ordenadas, localización clínica en español y mapping a SNOMED CT `416342005`; excluye explícitamente el set de estados de dispensación de medicamentos.
- Agrega `CRED-028-TPED`, con 12 líneas y 89 hitos estructurados, y validación CI de la cardinalidad de los mappings y formularios de desarrollo.
- Conserva los tags de ubicación `Queue Location` y `Appointment Location` en Initializer, y define tipos de servicio de cita para que agenda no quede sin duración.
- Agrega especialidades y servicios de cita para Medicina de Rehabilitacion, Hemodialisis y Nutricion y Dietetica, alineados con las colas y servicios facturables ya existentes.
- Documenta en formato de release la actualización de la anamnesis (`CE-ANAM-001-ANAMNESIS`, versión `1.0.3`) y la actualización de la configuración de colas, citas y UPSS de soporte según revisión funcional.
- Agrega tipos de procedimiento EMR API mediante el dominio Initializer `proceduretypes`, junto con los privilegios requeridos para leer y gestionar procedimientos en el módulo O3.
- Agrega privilegios de frontend para admision (`app:adt`), citas, colas, modulos operativos del home, vacunacion independiente (`app:immunization`, `app:immunization.edit`) y FUA (`Fua Privilege`, `Read Fua`, `Manage Fua`, `Update Fua`), junto con roles de navegacion operativa y roles de vacunacion de lectura y edicion.

### Cambiado
- Alinea los formularios CRED resumidos con NTS 238 y NTS 213/RM 429-2024: elimina umbrales fijos de anemia,
  identifica el instrumento de salud mental, retira clasificaciones nutricionales semánticamente ambiguas,
  corrige la pauta Huanca y hace auditables los resúmenes EDI y M-CHAT-R/F.
- Publica y bundlea `procedimientos`, `laboratorio`, `lenguas` y `geografia` `2026-07-10-02`, y `sihsalus`
  `2026-07-10-03`; restaura todos los extremos y fuentes destino requeridos por el importador OCL de OpenMRS y
  actualiza la suscripción principal a la nueva release.
- Publica y bundlea `sihsalus`, `seguros` y `laboratorio` `2026-07-10-01`; alinea 111 formularios con 3 641 referencias conceptuales, unifica el par activo Sí/No usado por O3 y limpia value sets mezclados sin eliminar observaciones históricas.
- Corrige la lógica de CRED: M-CHAT-R/F, Huanca y Lista de Habilidades calculan resultados de solo lectura; `CRED-004` admite hasta 143 meses y puntajes EEDP acumulados; el formulario EEDP rotulado como 21 meses se documenta correctamente como acumulado hasta 24 meses.
- Corrige campos semánticamente cruzados en Consulta Externa, inmunizaciones, obstetricia y hospitalización; reemplaza conceptos `N/A` usados para guardar fechas o números y separa estados, personas y hallazgos en preguntas propias.
- Migra los campos calculados de `editable: false` a `readonly: true`, soportado por el form engine O3, y corrige renderers, etiquetas, encounter types, BMI y condiciones de visibilidad detectadas en la auditoría final.
- Evita la colisión de Initializer con `Queue Location` y `Appointment Location`: las filas sin UUID se resuelven por nombre contra los tags creados por sus módulos, sin recrearlos ni migrar la base de datos.
- Publica y bundlea `SIHSALUS/sihsalus` `2026-07-09-02` con 4 459 conceptos y 5 635 mappings: conecta las 12 líneas y 89 hitos TPED, convierte TPED, Huanca, Lista, EDI y M-CHAT-R/F en sets navegables, conserva EEDP, TEPSI y TPED habilitados, e incorpora la terminología requerida por procedimientos O3.
- Completa `CIEL 1732 - Duration units` como `CONCEPT-SET` de ocho miembros, corrige los UUIDs OpenMRS de sus unidades, fija el orden oficial y localiza el conjunto como `Unidades de duración`.
- Alinea `CRED-004`, `CRED-009`, `CRED-010`, `CRED-026` y `CRED-027` con los nombres y resultados normativos: EDI Verde/Amarillo/Rojo, M-CHAT-R/F de 0 a 20 puntos y Huanca con pauta de 30 a 36 meses.
- Publica y bundlea `SIHSALUS/ocupaciones` `2026-07-09-01` con los 436 grupos unitarios CIUO-08, nombres oficiales preferidos en español, nombres ISCO-08 en inglés y 436 mappings `CONCEPT-SET` hacia el agrupador de ocupaciones.
- Refresca los exports OCL bundleados desde las versiones publicadas vigentes en `SIHSALUS`, actualiza `openconceptlab.subscriptionUrl` a `SIHSALUS/sihsalus/2026-07-09-02` y documenta la auditoría de cobertura de formularios contra conceptos.
- Alinea ubicaciones UPSS con colas, citas y ADT: Central de Esterilizacion queda como soporte interno, Admission/Transfer se conserva para salas de hospitalizacion, y las UPSS de soporte programables quedan como ubicaciones de cita sin ADT.
- Retira Emergencia del dominio de citas programadas; se conserva como cola operativa y servicio facturable.
- Actualiza los exports OCL del bundle a sus versiones publicadas más recientes en la org SIHSALUS: `laboratorio` a `24-06-2026-2` (completo y `concepts-only`) y `prestacionales` a `2026-06-18-01`; el resto de sources se mantiene en su versión publicada vigente.
- Agrega al bundle OCL el source `prestacionales` (`v2026-06-17-openmrs-current`) con 65 códigos prestacionales y un agrupador `CONCEPT-SET`, reclasificando los códigos como `Misc/N/A` y el set como `ConvSet/N/A`.
- Reemplaza los conceptCodes CIEL de dispositions por conceptos locales ya cargados en SIHSALUS, evitando dependencia runtime de CIEL para admisión, alta, transferencia, fallecido y observación.
- Restringe `Application: Registers Patients` a privilegios explícitos de registro de pacientes para evitar que `Admision` reciba permisos clínicos por herencia de `Privilege Level: High`.
- Asigna al rol `Admision` solo los accesos de admision, citas y colas necesarios para registro, agenda y derivacion operativa.
- Agrega `Get Beds` y `Get Admission Locations` al rol `Admision` porque el validador de `bedmanagement` los requiere al crear visitas, incluso cuando la consulta no asigna cama.
- Define los roles operativos `Laboratorista` y `Farmacia` con los privilegios de frontend y backend requeridos para ver y operar laboratorio y dispensacion sin heredar accesos de admision.
- Agrega el atributo de visita `Procedencia` para registrar desde dónde procede el paciente en una atención.
- Actualiza los exports OCL del content package a la org `SIHSALUS`; los sources de dominio quedan en `v2026-06-16-openmrs-current`.
- Actualiza el export principal `sihsalus` a `v2026-06-16-education-mappings-fix`, moviendo las respuestas de nivel educativo desde `No (respuesta)` hacia `Highest education level` y enlazando `Nivel I-2` a `Nivel de Atención`.
- Actualiza el export principal `sihsalus` a `v2026-06-16-glasgow-vitals`, agregando los conceptos de Escala de Glasgow usados por el ESM de signos vitales (`glasgowEyeOpeningUuid`, `glasgowVerbalResponseUuid`, `glasgowMotorResponseUuid`, `glasgowTotalUuid`) y sus respuestas.
- Actualiza el export principal `sihsalus` a `v2026-06-16-pns-contact-metadata`, agregando conceptos y mappings para metadata de contactos PNS usada por flujos de ficha familiar, relaciones y notificación de contactos.
- Actualiza el export principal `sihsalus` a `v2026-06-16-languages`, agregando sets de lenguas del mundo y lenguas indígenas u originarias del Perú (BDPI), separados de conceptos de etnia, más `Otra lengua no codificada`.
- Actualiza el export principal `sihsalus` a `v2026-06-16-qanda-cleanup`, completando mappings `Q-AND-A` determinísticos para preguntas CRED, atributos de persona, educación, grupo sanguíneo, acreditación y formularios sin reabrir la duplicidad controlada de `Sí`/`No`.
- Actualiza el export principal `sihsalus` a `v2026-06-17-openmrs-order-fix`, retirando un mapping activo desde un concepto retirado y reordenando los ZIPs OCL para que los conceptos destino existan antes de importar mappings cross-source.
- Actualiza el export `laboratorio` a `16-06-2026-2`.
- Corrige la validacion SIHSALUS con Initializer 2.12: evaluator SQL de Patient Flags, estado `Fallecido` en workflows de programa y referencia activa del medicamento MINSA `47343`.
- Apunta `openconceptlab.subscriptionUrl` al source principal versionado `SIHSALUS/sihsalus/v2026-06-17-openmrs-order-fix`.
- Consolida la curación OCL: conceptos administrativos movidos fuera de `laboratorio`, normalización de conceptos de laboratorio, insumos de `medicamentos` clasificados como `Medical supply`, y códigos CIE-10 `U*` clasificados como `Misc`.
- Re-exporta OCL tras los fixes de import OpenMRS: `inmunizaciones#584` queda como `Vacuna antiamarílica` y las respuestas clínicas de aborto se rewirean a `diagnosis`.
- Migra la configuracion de Patient Flags desde Liquibase a dominios Initializer (`flagpriorities`, `flagtags`, `flags`) y corrige el evaluator SQL al nombre soportado por `patientflags`.
- Alinea rangos críticos de signos vitales de triaje con la NT 042-MINSA/DGSP-V.01 y amplía límites absolutos para no bloquear valores de Prioridad I.
- Documenta la auditoría de inmunizaciones contra la NTS 246-MINSA/DGIESP-2026 y marca las brechas de hexavalente, VRS, meningococo, VPH y SR antes de modificar calendario o formularios.
- Fortalece CI con validacion de anchos CSV, UUIDs unicos en formularios AMPATH y verificacion real de rangos de referencia contra los exports OCL bundleados.
- Excluye artefactos no ejecutables del ZIP final (`.DS_Store`, `.gitkeep`, `ampathforms/Readme` y formularios `_deprecated`).
- Normaliza IDs de preguntas AMPATH a ASCII camelCase, corrige botones `workspace-launcher` para que no se guarden como `obs` sin concepto, y agrega validacion CI para estructura basica de formularios.
- Retira/reclasifica procedimientos duplicados y mappings huerfanos de `SIHSALUS/sihsalus` para que CPMS (`SIHSALUS/procedimientos`) sea la fuente canonica de procedimientos, y actualiza formularios obstetricos a UUIDs CPMS para parto instrumentado y cesarea.
- Retira/reclasifica conceptos `Drug` de `SIHSALUS/sihsalus` para que `SIHSALUS/medicamentos` sea la fuente canonica de medicamentos, manteniendo en `sihsalus` solo campos clinicos y respuestas de formulario no ordenables.
- Agrega `UBIGEO de Nacimiento` como atributo de persona buscable y retira el atributo textual legado `Lugar de Nacimiento`.
- Ordena los exports OCL con prefijos numericos para cargar primero `sihsalus` y `procedimientos`, evitando mappings hacia conceptos destino aun no importados.

## [1.11.0] - 2026-06-09

### Agregado
- Privilegios granulares del modulo CRED (`app:cred.antecedentes`, `app:cred.cursoVida`, `app:cred.earlyStim`, `app:cred.immunization`, `app:cred.neonatal`, `app:cred.nutrition`, `app:cred.wellChild` y sus variantes `.edit`) en `privileges_core-demo.csv`.
- Roles `CRED lectura` y `CRED lectura y edicion` en `roles-core.csv`, agrupando los privilegios de lectura y de edicion del modulo CRED.

## [1.9.6] - 2026-06-04

### Corregido
- Migra referencias de formularios a conceptos SIHSALUS V4 cargados en QLTY, incluyendo respuestas Si/No, Otro, Normal, Ninguno, diagnostico, laboratorio y opciones no binarias que habian quedado apuntando a UUIDs CIEL antiguos.
- Agrega conceptos internos `SIH.SALUS - ...` para campos de formulario que no tienen equivalente directo en SIHSALUS V4, evitando colisiones de nombres durante Initializer.

## [1.9.4] - 2026-06-04

### Corregido
- Alinea las opciones de formularios `ODONT-003`, `PSIC-001`, `PSIC-002` y `PSIC-004` con UUIDs canonicos ya importados por la terminologia para evitar referencias a conceptos no cargados.
- Agrega la estructura de conceptos y mappings `CIEL` requeridos por FHIR2 `Immunization`, incluyendo el set `CIEL:984` con vacunas MINSA para `INMU-001`.
- Elimina filas de conceptos locales duplicados que fallaban en Initializer por nombres existentes en locale `es`.

## [1.8.32] - 2026-05-28

### Agregado
- Formulario `ODONT-003-ATENCIÓN ODONTOLÓGICA` para el registro clínico de la atención odontológica (motivo de consulta, índices CPO-D/ceo-d e IHOS, riesgo estomatológico, diagnóstico CIE-10, actividades preventivas y recuperativas, plan de tratamiento y disposición), usando el encounter type existente `Atención de Odontología`. Complementa el odontograma, que registra los hallazgos por pieza.
- Conceptos de odontología en `concepts-odontology.csv` para la atención clínica: tipo de atención, antecedentes estomatológicos, índices CPO-D/ceo-d, IHOS, riesgo estomatológico, actividades preventivas, procedimientos recuperativos, detalle de procedimientos, piezas tratadas y disposición.

---

## [1.8.31] - 2026-05-13

### Corregido
- Agrega membresias `conceptsets` para los conceptos de colas (`Tipo de Servicio`, `Estado de la Cola` y `Prioridad`) antes del dominio `queues`.
- Corrige el rechazo de las 16 colas por no tener sus servicios como miembros de `queue.serviceConceptSetName`.

---

## [1.8.30] - 2026-05-12

### Cambiado
- Actualiza el export OCL SIHSALUS-v4 a la version `12-05-2026-1`.
- Alinea el programa Tuberculosis para usar el concepto OCL `Programa de Tuberculosis` de clase `Program`.

---

## [1.8.29] - 2026-05-12

### Corregido
- Corrige filas mal escapadas en rangos de referencia de laboratorio que rompian el dominio `conceptreferencerange`.

---

## [1.8.28] - 2026-05-12

### Corregido
- Alinea el export OCL SIHSALUS-v4 con los servicios de Queue consumidos por el content package.
- Reemplaza codigos numericos OCL por UUIDs OpenMRS estables en queues y propiedades globales.
- Espera publicacion completa en Maven Central antes de considerar exitoso el deploy.

---

## [1.8.27] - 2026-05-12

### Corregido
- Nueva publicacion requerida porque `1.8.25` y `1.8.26` ya existen en Maven Central con configuracion de Queue no reproducible.
- Mantiene las colas y propiedades globales de Queue alineadas con UUIDs estables importados desde OCL.

---

## [1.8.25] - 2026-05-12

### Corregido
- Alineadas las colas de atencion con los conceptos importados desde OCL para evitar errores de Initializer en el dominio `queues`.

---

## [1.8.24] - 2026-05-11

### Cambiado
- Publicacion estable con carga controlada de conceptos SIH.SALUS en OCL y alineacion de configuracion frontend/CI.

---

## [1.8.20] - 2026-04-30

### Cambiado
- Publicacion del content package con las correcciones recientes de metadata y limpieza de configuracion frontend obsoleta.

### Agregado
- Workflow de GitHub Actions para validar el content package contra la distro SIHSALUS y exigir 0 errores de CSV/Initializer.

---

## [1.6.0] - 2026-02-11

### Corregido
- **UUIDs**: Regenerados 43 UUIDs inválidos (contenían caracteres no-hexadecimales) en encounter types, encounter roles, service definitions, visit types, programs, person attribute types, order frequencies y metadata term mappings
- **Formularios AMPATH**: Actualizados 33 formularios JSON con los nuevos UUIDs de encounter types
- **Cascading fixes**: Actualizadas colas de atención y metadata term mappings con los nuevos UUIDs referenciados
- **HOSP-010**: Corregido `encounterType` vacío en Epicrisis Obstétrico-Postparto (ahora apunta a Epicrisis Médica HSC)
- **Attribute Types**: Corregido UUID duplicado entre Profesión y Colegio Médico en provider attributes
- **Global Properties**: Reemplazado UUID placeholder (RFC 4122 example) en Fast Data Entry por UUID real de Consulta Ambulatoria

---

## [1.5.0] - 2026-02-11

### Agregado
- **Message Properties**: Traducciones i18n al español (`messages_es.properties`) con terminología MINSA
- **Cash Points**: 3 puntos de caja (Admisión, Farmacia, Emergencia) para módulo de billing
- **Billable Services**: 14 servicios facturables alineados con las UPSS del hospital (consultas, laboratorio, ecografía, cirugía, hemodiálisis, etc.)
- **Cohort Attribute Types**: 3 atributos para listas de pacientes (descripción, ubicación, programa asociado)

---

## [1.4.0] - 2026-02-11

### Agregado
- **FHIR Patient Identifier Systems**: URLs FHIR para todos los identificadores peruanos (DNI/RENIEC, CE, Pasaporte, CNV, Historia Clínica) - Requerido para interoperabilidad RENHICE (Ley 30024)
- **Dispositions**: Configuración de disposiciones clínicas (Admitir, Alta, Transferir, Fallecido, Observación) para flujo hospitalario O3

### Nota
Las dispositions requieren conceptos CIEL que deben agregarse a la colección OCL: 164180 (Disposition set), 1654 (Admit), 1655 (Transfer), 1656 (Died), 1657 (Discharge), 159791 (Admission Location), 160473 (Transfer Location)

---

## [1.3.0] - 2026-02-11

### Agregado
- **Encounter Type**: Sesión de Psicoprofilaxis (RM 361-2011)
- **Formularios AMPATH**: 5 nuevos formularios clínicos para CRED y Madre Gestante
- **Concept Sources**: Nuevos códigos y descripciones en `conceptsources.csv`

### Programas clínicos obligatorios (normativa MINSA)
- **Tuberculosis** (NTS 200-MINSA/DGIESP-2023, RM 339-2023)
- **VIH/SIDA** (NTS 169-MINSA/2020, RM 1024-2020)
- **Adulto Mayor** (NTS 207-MINSA/DGIESP-2023, RM 789-2023)
- **Planificación Familiar** (NTS 124-MINSA/2016, RM 652-2016)
- **Enfermedades No Transmisibles** (PP 0018, PP 0024)
- **Enfermedades Metaxénicas y Zoonosis** (PP 0017)

### Encounter types obligatorios (normativa MINSA)
- **Diagnóstico y Seguimiento de Tuberculosis** (NTS 200)
- **Tamizaje de VIH** (NTS 169)
- **Manejo de Terapia Antirretroviral - TARGA** (NTS 169)
- **Valoración Clínica del Adulto Mayor - VACAM** (NTS 207)
- **Consejería en Planificación Familiar** (NTS 124)
- **Tamizaje de Cáncer Cervical - PAP/IVAA** (PP 0024)
- **Atención de Enfermedades Metaxénicas** (PP 0017)
- **Atención Integral del Adolescente** (NTS 157)

### Corregido
- **GitHub Actions**: Workflow CI ahora apunta a las ramas `main` y `pre-release`

### Metadata alineada con referenceapplication
- **Cohort Types**: Agregado `cohorttypes/cohorttypes.csv` con System List y My List (faltaba completamente)
- **Global Properties**: Agregadas 4 propiedades core: `concept.true`, `concept.false`, `visits.assignmentHandler`, `visits.allowOverlappingVisits`
- **Privilegios**: Agregado privilegio `O3 Implementer Tools` (requerido para herramientas de implementador O3)

---

## [1.1.1] - 2026-01-13

### 🔴 HOTFIX - Corregido

**Problema Crítico:** Los archivos `programworkflows.csv` y `programworkflowstates.csv` agregados en v1.1.0 causaban errores de inicialización porque los conceptos referenciados no existen en la base de datos.

**Errores generados:**
```
java.lang.IllegalArgumentException: Unable to find concept: Estado de Control CRED
java.lang.IllegalArgumentException: Unable to find concept: Estado de Gestación
```

**Solución aplicada:**
- Vaciados los archivos `programworkflows/sihsalus-programworkflows.csv` (solo headers)
- Vaciados los archivos `programworkflowstates/sihsalus-programworkflowstates.csv` (solo headers)
- Los 8 programas clínicos funcionan sin workflows hasta que se creen los conceptos necesarios en OCL

### Archivos Modificados
- `configuration/backend_configuration/programworkflows/sihsalus-programworkflows.csv` (revertido a solo headers)
- `configuration/backend_configuration/programworkflowstates/sihsalus-programworkflowstates.csv` (revertido a solo headers)

### Nota Importante
Los workflows y estados agregados en v1.1.0 serán reimplementados en una versión futura una vez que se creen los conceptos apropiados en OpenConceptLab (OCL).

---

## [1.1.0] - 2026-01-12

**⚠️ ADVERTENCIA:** Esta versión contiene errores críticos. Use v1.1.1 en su lugar.

### Corregido
- **Colas de Atención (sihsalus-queues.csv)**: Corregidos 16 registros de colas que generaban errores de duplicados
  - Generados nuevos UUIDs únicos para cada cola
  - Vinculadas correctamente a servicios existentes en `appointmentservicedefinitions`
  - Eliminados errores "Queue with UUID already exists" en la inicialización

### Agregado
- **Program Workflows (sihsalus-programworkflows.csv)**: Agregados 3 workflows para programas clínicos activos
  - Workflow "Estado de Control CRED" para programa Control de Niño Sano
  - Workflow "Estado de Gestación" para programa Madre Gestante
  - Workflow "Estado de Vacunación Infantil" para programa de Vacunación Infantil

- **Program Workflow States (sihsalus-programworkflowstates.csv)**: Agregados 11 estados de workflow
  - **Control CRED**: Activo, Completado, Abandonado
  - **Gestación**: Primer Trimestre, Segundo Trimestre, Tercer Trimestre, Parto, Post-Parto
  - **Vacunación Infantil**: En Proceso, Completo, Incompleto

### Mapeo de Colas a Servicios

| Cola | Servicio Asignado |
|------|-------------------|
| Cola de Admisión Hospital | Consulta ambulatoria por médico general |
| Cola de Admisión Casita Azul | Consulta ambulatoria por médico general |
| Cola de Triaje | Atención ambulatoria por enfermera(o) |
| Cola de Consulta Externa | Consulta ambulatoria por médico general |
| Cola de Farmacia | Atención en farmacia clínica |
| Cola de Laboratorio | Procedimientos de Laboratorio Clínico Tipo II-1 |
| Cola de Hospitalización | Hospitalización de Cirugía General |
| Cola de Emergencia | Atención de urgencias y emergencias |
| Cola de Centro Obstétrico | Atención ambulatoria por obstetra |
| Cola de Centro Quirúrgico | Hospitalización de Cirugía General |
| Cola de Diagnóstico por Imágenes | Ecografía general y Doppler |
| Cola de Anatomía Patológica | Consulta ambulatoria por médico general |
| Cola de Central de Esterilización | Atención ambulatoria por enfermera(o) |
| Cola de Medicina de Rehabilitación | Atención ambulatoria por enfermera(o) |
| Cola de Hemodiálisis | Consulta ambulatoria por médico general |
| Cola de Nutrición y Dietética | Atención ambulatoria por enfermera(o) |

### Archivos Modificados
- `configuration/backend_configuration/queues/sihsalus-queues.csv`
- `configuration/backend_configuration/programworkflows/sihsalus-programworkflows.csv`
- `configuration/backend_configuration/programworkflowstates/sihsalus-programworkflowstates.csv`

---

## [1.0.0] - 2025-XX-XX

### Agregado
- Configuración inicial del content package para SIHSALUS
- 38 módulos de configuración OpenMRS
- 56 formularios clínicos (Ampath Forms)
- Base de datos geográfica de Perú (94,924 registros)
- 495 medicamentos del petitorio nacional
- 6 paquetes OCL de terminología médica (~12.7 MB)
- Configuración FHIR con fuentes estándar (CIEL, LOINC, SNOMED CT)
- 17 ubicaciones hospitalarias
- 30 tipos de visita
- 8 programas clínicos
