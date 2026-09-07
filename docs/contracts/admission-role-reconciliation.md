# Reconciliación de identidades del rol de Admisión

Estado: BORRADOR — NO HABILITAR, PUBLICAR NI DESPLEGAR.

Este documento permite revisar la migración separadamente del permiso de
relaciones de #222. No aprueba una política de privilegios ni autoriza merge,
release, acceso a entornos o ejecución sobre usuarios existentes. No contiene
inventarios de instalaciones, cuentas, credenciales ni datos clínicos.

## Procedencia y alcance conservado

La extracción conserva los seis changeSets, sus 172 líneas originales, la
prueba y el paso CI de `bd3c9c6647bb62fb517c6564cfefead411a00436`, cuyo padre es
`cb38db1dcf50c1d998776c422ed30ce1f60b2e07`. No cambia SQL, precondiciones,
identificadores ni orden de ejecución. Tampoco modifica changeSets anteriores.

Los archivos ejecutables son:

- `configuration/backend_configuration/liquibase/liquibase.xml`;
- `.github/scripts/test_admission_role_reconciliation.py`;
- el paso `Test admission role reconciliation` de `.github/workflows/main.yml`.

El cambio de `Delete Relationships` en `roles-core.csv` y su validador pertenece
al PR de permisos, no a esta extracción. Esta rama no modifica esos archivos ni
reserva una nueva versión de Maven.

## SQL e Initializer son etapas distintas

La fase SQL reconcilia las dos identidades conocidas de Admisión y sus
referencias conocidas antes de entregar la identidad canónica al cargador de
roles. Incluye comprobaciones de identidad, unión de asignaciones y referencias,
y retirada de la identidad histórica. No es una operación meramente documental:
puede cambiar los privilegios y las herencias efectivos de usuarios existentes.

Initializer procesa después la definición declarativa de roles. La unión que
produce el SQL no demuestra qué asignaciones permanecerán tras ese cargador,
sus checksums y sus reglas de actualización. Deben verificarse ambas etapas con
la versión concreta de Initializer y el contenido final coordinado. Esta
extracción no resuelve diferencias entre la política histórica y la canónica.

La migración está incluida en el changelog del paquete y no dispone de un
interruptor de ejecución. Mantener el PR en borrador y fuera de releases es un
control de proceso, no un bloqueo técnico si alguien despliega ese artefacto.

## Riesgos de actualización pendientes

- La historia Liquibase puede diferir entre instalaciones. Hay que comprobar el
  changelog completo, incluido el cambio anterior de normalización, cuando esté
  pendiente, aplicado o marcado como ejecutado; no basta ejecutar los seis
  bloques nuevos de forma aislada.
- Pueden variar las tablas de módulos, restricciones, referencias y colaciones.
  Las referencias conocidas en el SQL no constituyen un inventario completo de
  toda instalación. No se deben eliminar referencias desconocidas para forzar
  la finalización.
- Las colisiones, las herencias y los permisos efectivos requieren aprobación
  de la política RBAC. Conservar filas en una prueba no demuestra equivalencia
  de acceso ni ausencia de ampliación de privilegios.
- Deben comprobarse fallos intermedios, reintentos, estado parcial y recuperación
  con MariaDB/Liquibase reales. No se presume una transacción única que revierta
  toda la secuencia.
- No existe aquí un rollback explícito de los changeSets. Revertir el paquete
  no restaura por sí solo las identidades o referencias modificadas en SQL.

## Evidencia local y límites

La prueba original ejecuta cuatro escenarios con SQLite en memoria: identidades
duplicadas con referencias compartidas, identidad histórica sin tablas
opcionales, UUID canónico desactualizado y colisión con otra identidad.

Su adaptación sustituye `INSERT IGNORE` y la generación de UUID para ese modelo.
No ejecuta MariaDB, el motor Liquibase, el changelog completo, Initializer ni
autorización OpenMRS. Un resultado verde de esta prueba, del validador XML o de
Maven no es aprobación de la migración ni validación clínica.

Comprobaciones locales reproducibles, sin backend:

```sh
python3 .github/scripts/test_admission_role_reconciliation.py
python3 .github/scripts/validate_liquibase.py
mvn --batch-mode --no-transfer-progress spotless:check
git diff --check
```

## Condiciones antes de una futura aprobación

1. Revisar la política de identidad y permisos con sus responsables, separada
   del permiso puntual de #222; definir el resultado efectivo esperado sin
   resolverlo mediante esta extracción.
2. Validar en una base sintética local o DEV/QLTY coordinada los estados de
   actualización, los módulos opcionales, las restricciones, la repetición y la
   recuperación; conservar evidencia de SQL e Initializer por separado.
3. Probar con cuentas sintéticas los accesos permitidos y denegados después de
   toda la carga de contenido, además de la integridad de las referencias.
4. Acordar respaldos recuperables, procedimiento de reversión, limpieza
   sintética y autorizaciones del entorno. No usar pacientes reales ni PROD.
5. Revisar el diff final y su CI; reservar una versión inmutable nueva solamente
   cuando exista aprobación, evitando reutilizar `1.25.14` o competir con otras
   releases. Actualizar entonces la documentación de versión y coordinar el pin
   del distro. Esta rama no publica ni promete una versión futura concreta.

Hasta completar esos controles, mantener el PR Draft y no mezclarlo con el PR
de permisos ni con una release de contenido.
