# SIHSALUS Content Package

SIHSALUS Content Package para OpenMRS, con la versión actual **1.25.1**.

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

## Catálogos territoriales locales

Los barrios de Santa Clotilde se modelan como un atributo codificado de persona, separado de la
jerarquía RENHICE. El tipo de atributo `Barrio` se define en `personattributetypes`; las opciones y la
pertenencia al catálogo activo se administran exclusivamente en la fuente OCL independiente
`SIHSALUS/barrios-santa-clotilde`. La release bundleada `2026-08-22-01` contiene los conceptos
`SCL-01` a `SCL-10`, el set `SCL-BARRIOS` y exactamente diez mappings `CONCEPT-SET`.

Los exports oficiales deben ubicarse como
`15_SIHSALUS_barrios-santa-clotilde_concepts_2026-08-22-01.zip` y
`65_SIHSALUS_barrios-santa-clotilde_mappings_2026-08-22-01.zip`. El validador rechaza archivos
faltantes, contenido adicional o una versión/source diferente. El source principal `SIHSALUS/sihsalus`
y su suscripción permanecen en `2026-07-16-02`; no se actualizan para incorporar este catálogo local.
OCL conserva los registros retirados en el HEAD de `sihsalus` porque un administrador de la organización
no puede purgar mappings. No se debe publicar ni bundlear una release futura de `sihsalus` que incluya
esos UUIDs retirados hasta que soporte OCL los purgue o el proceso de export los excluya explícitamente.

Este paquete distribuye únicamente la metadata backend y los exports OCL. La configuración efectiva de
registro, búsqueda y banner se mantiene en `sihsalus-frontend/config/frontend.json`; no se empaqueta una
copia desde este repositorio. OCL conserva `ui_color` y `ui_tag_type` solo como metadata descriptiva y no
clínica; no se persisten como valor del atributo ni garantizan su renderizado. El frontend actual no
consume esa metadata. El selector obtiene sus opciones exclusivamente desde `answerConceptSetUuid`, sin
duplicar el catálogo en la configuración.
`ADDRESS_3/Barrio` se retira en este cambio porque se confirmó que no existen datos reales que deban
migrarse. El contrato está documentado en `docs/contracts/santa-clotilde-neighborhoods.md`.

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

Versión del paquete: **1.25.1**.

## Contrato de diagnósticos de Consulta Externa

`CE-001-CONSULTA EXTERNA` no captura diagnósticos. El diagnóstico CIE-10 debe registrarse
exclusivamente mediante **Visit Notes**, que lo persiste como diagnóstico nativo del encuentro para
que aparezca en el historial clínico y pueda ser consumido por los flujos dependientes. No se deben
agregar a CE-001 observaciones de texto, certeza u ocurrencia que simulen un diagnóstico.

El esquema corregido usa la versión `1.0.2`. Initializer deriva la identidad persistida del nombre y
la versión: al actualizar desde `1.0.1`, retira el formulario anterior y conserva intactos su recurso
JSON y los encuentros históricos; luego crea `1.0.2` como única versión activa. El `uuid` incluido en
el JSON de AMPATH no es la identidad persistida y no debe usarse como contrato de integración.

Visit Notes además requiere el `Form` canónico `c75f120a-04ec-11e3-8780-2b40bef9a44b` (`Visit Note`
`1.0`) y el tipo de encuentro `d7151f82-c1f3-4152-a605-2f9ea7414a79`. Initializer 2.12 no ofrece un
dominio CSV genérico para `Form`, por lo que Liquibase crea la fila solo cuando falta y completa solo
una asociación de tipo de encuentro nula. Como Liquibase corre antes que `ENCOUNTER_TYPES` y el
archivo completo puede omitirse por checksum en arranques posteriores, el mismo changelog crea
primero el tipo canónico cuando falta y deja el Form asociado en una sola ejecución. El CSV posterior
lo reconcilia por UUID. Un `Form` existente nunca se renombra, publica, retira ni reasocia
silenciosamente. El contrato y los datatypes consumidos por el frontend están fijados en
`docs/contracts/visit-note-content-contract.json`.

Para rollback no se debe volver a publicar el JSON `1.0.1`, porque sobrescribiría su recurso histórico.
Se revierte el frontend coordinadamente y se conserva `1.0.2` retirado si ya fue usado; las filas de
formularios y encuentros clínicos no se eliminan.

## Cobertura MINSA (Categoría II)

Este paquete ya incluye formularios para consulta externa, obstetricia, salud mental, laboratorio básico de resultados, vacunación, odontología y hospitalización básica. Varios procesos de MINSA pueden quedar cubiertos por módulos nativos de OpenMRS (por ejemplo, triaje/laboratorios/medicación según configuración), pero se dejó esta lista para identificar brechas de documentación clínica en formularios SIH-SALUS.

Cobertura estimada (categoría II-1 / II-2):

1. Cubierto por formularios o metadata de este paquete
   - Atención ambulatoria y consulta externa: `CE-*`, `PSIC-*`
   - Signos vitales y urgencia: metadata y contrato separados para el registro longitudinal del
     chart, el triaje de emergencia y la atención posterior. La captura debe implementarse en el
     frontend como módulo embebido; este paquete no agrega un formulario JSON en `/ampathforms`.
   - Obstetricia y neonatal: `OBST-*`, partograma, RN y puerperio
   - Hospitalización: `HOSP-001`, `HOSP-004`, `HOSP-008`, `HOSP-009`, `HOSP-012`, `FormularioEpicrisisMédica`
   - Referencia/contrarreferencia: `CE-REF-*`
   - CRED y programas de continuidad: `CRED-*`, incluyendo Huanca Test adaptado (`CRED-026`) y lista de habilidades/conductas esperadas (`CRED-027`)
   - Salud mental: `PSIC-001` a `PSIC-004`
   - Odontología: `ODONT-*`
   - Inmunizaciones: `INMU-001` y `INMU-002`; pendiente alinear el set de vacunas/productos contra la NTS 246-MINSA/DGIESP-2026.

1. Parcial o soportado por OpenMRS nativo (requiere validación local)
   - Prescripción médica: formulario de prescripción + módulos de med list/order
   - Laboratorio: resultados presentes; revisar si el flujo de solicitud/muestra está cubierto nativamente
   - Farmacia: prescripción cubre parte del proceso; validar dispensación y conciliación con flujo nativo
   - Radiología/imagen y patología: validar módulos instalados antes de crear formularios
   - UCI y cirugía/electiva: revisar visittypes y módulos de urgencia/cirugía habilitados

1. Pendientes prioritarios para documentación MINSA por categoría II
   - Documentación completa de urgencia más allá de la metadata de triaje: atención inicial,
     observación/evolución y reanimación
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
- NTS 246-MINSA/DGIESP-2026 (esquema nacional de inmunizaciones): https://www.gob.pe/institucion/minsa/normas-legales/8265031-561-2026-minsa
- Guía de Vigilancia del Neurodesarrollo - Huanca Payehuanca (manual de aplicación): https://repositorio.essalud.gob.pe/handle/20.500.12959/5846

Antes de crear o modificar formularios clínicos, revisar la norma técnica vigente en fuentes oficiales MINSA/gob.pe. No asumir que una NTS anterior sigue vigente si existe resolución posterior.
