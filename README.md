# SIHSALUS Content Package

SIHSALUS Content Package para OpenMRS, con la versión actual **1.13.2**.

The contents of a typical Content Package are:
* **Configuration**
    * This folder holds [Initializer compatible configuration metadata]([url](https://github.com/mekomsolutions/openmrs-module-initializer/blob/main/README.md)) that make up the content package. For example, in the /config directory, this includes:
        * **Forms** (in /ampathforms)
        * **Concepts** (in [/ocl]([url](https://github.com/mekomsolutions/openmrs-module-initializer/blob/main/README.md#:~:text=Open%20Concept%20Lab%20(ZIP%20Files))), [/concepts]([url](https://github.com/mekomsolutions/openmrs-module-initializer/blob/main/readme/concepts.md)))
        * **Programmatic Metadata** such as:
            * Programs (in [/programs]([url](https://github.com/mekomsolutions/openmrs-module-initializer/blob/main/readme/prog.md)))
            * Encounter types (in [/encountertypes]([url](https://github.com/mekomsolutions/openmrs-module-initializer/blob/main/readme/et.md)))
            * Workflows (in [/programworkflows]([url](https://github.com/mekomsolutions/openmrs-module-initializer/blob/main/readme/prog.md)))
            * Identifiers and other metadata
* **content.properties File**
    * Contents: This file specifies the required ESMs and OMODs (frontend modules and backend modules) that make up the Content Package.
    * Importance:
        * The content.properties file is important because when Implementers add this Content Package to their distribution, the content.properties file will automatically be read and compared with their existing distro.properties file.
        * An automatic distro Build Helper Tool then fetches the content package's information and extracts the content into the Implementation's distro.properties file.
        * **Dependencies** are especially important here, as the Build Helper Tool will add any dependencies from the Content Package into an Implementation's distro.properties file.

Running Spotless
----------------
This project uses Spotless for code formatting. Spotless is embedded in the build process, so when you run `mvn clean package`, Spotless will automatically format your code according to the project's style guidelines.

If you want to run Spotless separately, you can use the following Maven commands:

To apply the formatting:

    mvn spotless:apply

This will automatically format your code according to the project's style guidelines. It's recommended to run this command before committing your changes.

To check if your code adheres to the style guidelines without making any changes, you can run:

    mvn spotless:check

If this command reports any violations, you can then run `mvn spotless:apply` to fix them.

Remember, in most cases, you don't need to run these commands separately as Spotless will run automatically during the build process with `mvn clean package`.

Versión del paquete: **1.13.2**.

## Cobertura MINSA (Categoría II)

Este paquete ya incluye formularios para consulta externa, obstetricia, salud mental, laboratorio básico de resultados, vacunación, odontología y hospitalización básica. Varios procesos de MINSA pueden quedar cubiertos por módulos nativos de OpenMRS (por ejemplo, triaje/laboratorios/medicación según configuración), pero se dejó esta lista para identificar brechas de documentación clínica en formularios SIH-SALUS.

Cobertura estimada (categoría II-1 / II-2):

1. Cubierto en el paquete de formularios
   - Atención ambulatoria y consulta externa: `CE-*`, `PSIC-*`
   - Urgencia: en tipos de encuentro existe en `encountertypes`, pero no hay formulario específico de triaje y atención en `/ampathforms`
   - Obstetricia y neonatal: `OBST-*`, partograma, RN y puerperio
   - Hospitalización: `HOSP-001`, `HOSP-004`, `HOSP-008`, `HOSP-009`, `HOSP-012`, `FormularioEpicrisisMédica`
   - Referencia/contrarreferencia: `CE-REF-*`
   - CRED y programas de continuidad: `CRED-*`, incluyendo Huanca Test adaptado (`CRED-026`) y lista de habilidades/conductas esperadas (`CRED-027`)
   - Salud mental: `PSIC-001` a `PSIC-004`
   - Odontología: `ODONT-*`
   - Inmunizaciones: `INMU-001`

1. Parcial o soportado por OpenMRS nativo (requiere validación local)
   - Prescripción médica: formulario de prescripción + módulos de med list/order
   - Laboratorio: resultados presentes; revisar si el flujo de solicitud/muestra está cubierto nativamente
   - Farmacia: prescripción cubre parte del proceso; validar dispensación y conciliación con flujo nativo
   - Radiología/imagen y patología: validar módulos instalados antes de crear formularios
   - UCI y cirugía/electiva: revisar visittypes y módulos de urgencia/cirugía habilitados

1. Pendientes prioritarios para documentación MINSA por categoría II
   - Formularios de urgencia (triaje, atención inicial, observación/evolución, reanimación)
   - Formularios quirúrgicos y anestésicos (pre-operatorio, consentimiento, nota operatoria, anestesia, recuperación)
   - Solicitud de laboratorio + toma y trazabilidad de muestra
   - Solicitud e informe de imagen diagnóstica
   - Solicitud/compatibilidad/administración transfusional
   - Interconsulta y admisión hospitalaria no obstétrica (si aplica)
   - Nutrición clínica y plan hospitalario
   - Farmacia: dispensación y seguimiento farmacéutico en hospitalización
   - Documentos de esterilización de material/central de esterilización
   - II-2: ingreso y monitorización UCI, y soporte crítico (si aplica)

Referencias mínimas
- NTS 021-MINSA/DGSP-V.03 (categorías de establecimientos): https://spij.minjus.gob.pe/Graficos/Peru/2011/Julio/16/RM-546-2011-MINSA.pdf
- NTS 139-MINSA/2018/DGAIN (gestión de historia clínica): https://spij.minjus.gob.pe/Graficos/Peru/2018/Marzo/15/RM-214-2018-MINSA.pdf
- NTS 238-MINSA/DGIESP-2025 (control de crecimiento y desarrollo del niño): https://www.gob.pe/institucion/minsa/informes-publicaciones/7857089-norma-tecnica-de-salud-para-el-control-de-crecimiento-y-desarrollo-del-nino-nts-n-238-minsa-dgiesp-2025
- Guía de Vigilancia del Neurodesarrollo - Huanca Payehuanca (manual de aplicación): https://repositorio.essalud.gob.pe/handle/20.500.12959/5846
