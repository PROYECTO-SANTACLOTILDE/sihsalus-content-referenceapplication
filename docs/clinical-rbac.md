# Línea base RBAC clínica y de adjuntos

Este contenido provisiona capacidades de lectura para formularios clínicos y
tareas, además de los privilegios necesarios para adjuntos. No provisiona
privilegios genéricos de mutación para formularios o tareas ni modifica
masivamente los privilegios de los tipos de encuentro: OpenMRS aplica
`viewPrivilege` y `editPrivilege` en el servidor, y hacerlo sin una matriz
aprobada rompería flujos de Emergencia, Laboratorio, Farmacia y Hospitalización.

## Capacidades provisionadas

- `app:hoja.clinica.formulariosClinicos` permite abrir el catálogo de
  formularios.
- `app:hoja.clinica.listaTareas` permite consultar tareas.
- `View Attachments` autoriza la lectura mediante la API del módulo de adjuntos.
- `Create Attachments` declara la capacidad de creación del módulo y preserva
  compatibilidad con sus endpoints protegidos.

La lectura de adjuntos forma parte de `Application: Uses Patient Summary`. El
rol `SIHSALUS Consulta Externa` recibe además `Create Attachments` y ambos
privilegios de forma directa; `Enfermera` los hereda. `View Attachments` es
necesario aunque el rol ya tenga `View Observations`, porque el módulo protege
sus endpoints de lectura con una capacidad propia.
En la versión 4.0.0 desplegada, la carga guarda el archivo directamente mediante
`ObsService` y por eso también exige conservar `Add Observations`; el validador
protege las tres capacidades de Consulta Externa.

Cuando un tipo de encuentro declara un privilegio específico, el frontend exige
ese privilegio. La ausencia de metadata no equivale a acceso público y este
paquete no provisiona una capacidad genérica de mutación como reemplazo.

## Límite deliberado

La metadata actual contiene tipos sin `viewPrivilege` o `editPrivilege`, incluido
el UUID histórico mixto de Triaje
`67a71486-1a54-468f-ac3e-7091a9a79584`. No se rellenan en bloque porque:

- Laboratorio agrega resultados al encuentro que originó la orden.
- Farmacia consulta prescripciones creadas desde distintos tipos de encuentro.
- `LAB-001-RESULTADOS DE LABORATORIO - ÁREA HOSPITALIZACIÓN` todavía referencia
  el tipo `Hospitalización`.
- varios consumidores todavía escriben signos vitales al Triaje histórico.

Por ello, esta entrega mejora la autorización de interfaz sin afirmar que existe
segregación completa en backend. La matriz por dominio debe migrar primero los
escritores y después asignar los privilegios de tipo de encuentro.

## Despliegue y reversión

El contenido debe mantenerse sincronizado con el frontend. Retirar una fila del
catálogo evita que Initializer vuelva a provisionarla, pero no elimina de la base
de datos un privilegio creado por una versión anterior. Si se necesita borrarlo
físicamente de una instalación existente, debe hacerse mediante una migración
explícita y controlada.

## Validación operativa requerida

- Consulta Externa y Enfermería: pueden crear y volver a consultar adjuntos.
- Los roles no reciben privilegios genéricos de mutación para formularios o
  tareas desde este paquete.
- Acceso directo a un workspace por UUID: se resuelve el formulario y se valida
  el privilegio antes de montar React Form Entry o HTML Form Entry.
- Los endpoints REST deben probarse por rol; ocultar controles en el frontend no
  reemplaza la autorización del servidor.

`validate_csv_widths.py` verifica la estructura de los CSV y que
`SIHSALUS Consulta Externa` conserve las capacidades mínimas para adjuntos. No
valida aún una matriz de tipos de encuentro porque esa migración no forma parte
de este checkpoint.
