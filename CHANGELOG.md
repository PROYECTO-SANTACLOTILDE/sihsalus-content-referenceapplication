# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

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
- **GitHub Actions**: Workflow CI ahora apunta a branch `master` en lugar de `main`

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
- Vaciados los archivos `programworkflows/peruHCE-programworkflows.csv` (solo headers)
- Vaciados los archivos `programworkflowstates/peruHCE-programworkflowstates.csv` (solo headers)
- Los 8 programas clínicos funcionan sin workflows hasta que se creen los conceptos necesarios en OCL

### Archivos Modificados
- `configuration/backend_configuration/programworkflows/peruHCE-programworkflows.csv` (revertido a solo headers)
- `configuration/backend_configuration/programworkflowstates/peruHCE-programworkflowstates.csv` (revertido a solo headers)

### Nota Importante
Los workflows y estados agregados en v1.1.0 serán reimplementados en una versión futura una vez que se creen los conceptos apropiados en OpenConceptLab (OCL).

---

## [1.1.0] - 2026-01-12

**⚠️ ADVERTENCIA:** Esta versión contiene errores críticos. Use v1.1.1 en su lugar.

### Corregido
- **Colas de Atención (peruHCE-queues.csv)**: Corregidos 16 registros de colas que generaban errores de duplicados
  - Generados nuevos UUIDs únicos para cada cola
  - Vinculadas correctamente a servicios existentes en `appointmentservicedefinitions`
  - Eliminados errores "Queue with UUID already exists" en la inicialización

### Agregado
- **Program Workflows (peruHCE-programworkflows.csv)**: Agregados 3 workflows para programas clínicos activos
  - Workflow "Estado de Control CRED" para programa Control de Niño Sano
  - Workflow "Estado de Gestación" para programa Madre Gestante
  - Workflow "Estado de Vacunación Infantil" para programa de Vacunación Infantil

- **Program Workflow States (peruHCE-programworkflowstates.csv)**: Agregados 11 estados de workflow
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
- `configuration/backend_configuration/queues/peruHCE-queues.csv`
- `configuration/backend_configuration/programworkflows/peruHCE-programworkflows.csv`
- `configuration/backend_configuration/programworkflowstates/peruHCE-programworkflowstates.csv`

---

## [1.0.0] - 2025-XX-XX

### Agregado
- Configuración inicial del content package para SIH SALUS PeruHCE
- 38 módulos de configuración OpenMRS
- 56 formularios clínicos (Ampath Forms)
- Base de datos geográfica de Perú (94,924 registros)
- 495 medicamentos del petitorio nacional
- 6 paquetes OCL de terminología médica (~12.7 MB)
- Configuración FHIR con fuentes estándar (CIEL, LOINC, SNOMED CT)
- 17 ubicaciones hospitalarias
- 30 tipos de visita
- 8 programas clínicos
