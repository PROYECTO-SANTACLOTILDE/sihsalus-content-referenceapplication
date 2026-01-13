# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.1.0] - 2026-01-12

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
