# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Agregado
- Agrega tipos de procedimiento EMR API mediante el dominio Initializer `proceduretypes`, junto con los privilegios requeridos para leer y gestionar procedimientos en el módulo O3.
- Agrega privilegios de frontend para admision (`app:adt`), citas, colas, modulos operativos del home, vacunacion independiente (`app:immunization`, `app:immunization.edit`) y FUA (`Fua Privilege`, `Read Fua`, `Manage Fua`, `Update Fua`), junto con roles de navegacion operativa y roles de vacunacion de lectura y edicion.

### Cambiado
- Reemplaza los conceptCodes CIEL de dispositions por conceptos locales ya cargados en SIHSALUS, evitando dependencia runtime de CIEL para admisión, alta, transferencia, fallecido y observación.
- Restringe `Application: Registers Patients` a privilegios explícitos de registro de pacientes para evitar que `Admision` reciba permisos clínicos por herencia de `Privilege Level: High`.
- Asigna al rol `Admision` solo los accesos de admision, citas y colas necesarios para registro, agenda y derivacion operativa.
- Define los roles operativos `Laboratorista` y `Farmacia` con los privilegios de frontend y backend requeridos para ver y operar laboratorio y dispensacion sin heredar accesos de admision.
- Agrega el atributo de visita `Procedencia` para registrar desde dónde procede el paciente en una atención.
- Actualiza los exports OCL del content package a la org `SIHSALUS`; los sources de dominio quedan en `v2026-06-16-openmrs-current`.
- Actualiza el export principal `sihsalus` a `v2026-06-16-education-mappings-fix`, moviendo las respuestas de nivel educativo desde `No (respuesta)` hacia `Highest education level` y enlazando `Nivel I-2` a `Nivel de Atención`.
- Actualiza el export principal `sihsalus` a `v2026-06-16-glasgow-vitals`, agregando los conceptos de Escala de Glasgow usados por el ESM de signos vitales (`glasgowEyeOpeningUuid`, `glasgowVerbalResponseUuid`, `glasgowMotorResponseUuid`, `glasgowTotalUuid`) y sus respuestas.
- Actualiza el export principal `sihsalus` a `v2026-06-16-pns-contact-metadata`, agregando conceptos y mappings para metadata de contactos PNS usada por flujos de ficha familiar, relaciones y notificación de contactos.
- Actualiza el export principal `sihsalus` a `v2026-06-16-languages`, agregando sets de lenguas del mundo y lenguas indígenas u originarias del Perú (BDPI), separados de conceptos de etnia, más `Otra lengua no codificada`.
- Actualiza el export principal `sihsalus` a `v2026-06-16-qanda-cleanup`, completando mappings `Q-AND-A` determinísticos para preguntas CRED, atributos de persona, educación, grupo sanguíneo, acreditación y formularios sin reabrir la duplicidad controlada de `Sí`/`No`.
- Actualiza el export `laboratorio` a `16-06-2026-2`.
- Corrige la validacion SIHSALUS con Initializer 2.12: evaluator SQL de Patient Flags, estado `Fallecido` en workflows de programa y referencia activa del medicamento MINSA `47343`.
- Apunta `openconceptlab.subscriptionUrl` al source principal versionado `SIHSALUS/sihsalus/v2026-06-16-qanda-cleanup`.
- Consolida la curación OCL: conceptos administrativos movidos fuera de `laboratorio`, normalización de conceptos de laboratorio, insumos de `medicamentos` clasificados como `Medical supply`, y códigos CIE-10 `U*` clasificados como `Misc`.
- Re-exporta OCL tras los fixes de import OpenMRS: `inmunizaciones#584` queda como `Vacuna antiamarílica` y las respuestas clínicas de aborto se rewirean a `diagnosis`.
- Migra la configuracion de Patient Flags desde Liquibase a dominios Initializer (`flagpriorities`, `flagtags`, `flags`) y corrige el evaluator SQL al nombre soportado por `patientflags`.
- Alinea rangos críticos de signos vitales de triaje con la NT 042-MINSA/DGSP-V.01 y amplía límites absolutos para no bloquear valores de Prioridad I.
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
