# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.2.0] - 2026-02-10

### Agregado
- **Encounter Type**: Sesión de Psicoprofilaxis (RM 361-2011)
- **Formularios AMPATH**: 5 nuevos formularios clínicos para CRED y Madre Gestante
- **Concept Sources**: Nuevos códigos y descripciones en `conceptsources.csv`

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
