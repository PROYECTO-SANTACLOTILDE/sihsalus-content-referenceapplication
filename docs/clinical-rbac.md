# Línea base RBAC para mutaciones clínicas

Este cambio separa las capacidades de lectura y escritura que el frontend usa
para formularios clínicos y tareas. No modifica masivamente los privilegios de
los tipos de encuentro: OpenMRS aplica `viewPrivilege` y `editPrivilege` en el
servidor, y hacerlo sin una matriz aprobada rompería flujos de Emergencia,
Laboratorio, Farmacia y Hospitalización.

## Capacidades provisionadas

- `app:hoja.clinica.formulariosClinicos` permite abrir el catálogo de
  formularios.
- `app:hoja.clinica.formulariosClinicos.editar` permite crear o editar un
  formulario cuyo tipo de encuentro todavía no tenga un privilegio específico.
- `app:hoja.clinica.listaTareas` permite consultar tareas.
- `app:hoja.clinica.listaTareas.editar` permite crear, editar, completar o
  anular tareas.

El rol `SIHSALUS Consulta Externa` recibe ambas capacidades de escritura y el
rol `Enfermera` las hereda de él. No se asignan a Admisión, Laboratorio,
Farmacia ni Emergencia.

Cuando un tipo de encuentro declara un privilegio específico, el frontend exige
ese privilegio y no usa la capacidad genérica. Cuando la metadata está ausente,
la ausencia no equivale a acceso público: se exige explícitamente
`app:hoja.clinica.formulariosClinicos.editar`.

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

El contenido debe instalarse antes o junto con el frontend. Si se instala solo el
frontend, los formularios legacy quedan cerrados hasta que el usuario reciba la
nueva capacidad genérica.

La reversión del frontend no elimina privilegios. Si se revierte el contenido,
Initializer no borra automáticamente metadata de tipos de encuentro al dejar una
celda vacía; cualquier futura migración de esos campos debe incluir un changeset
de reversión explícito.

## Validación operativa requerida

- Consulta Externa: puede crear formularios y mutar tareas.
- Admisión: no puede crear formularios ni mutar tareas.
- Emergencia, Laboratorio y Farmacia: sus flujos especializados siguen
  funcionando sin recibir la capacidad clínica genérica.
- Acceso directo a un workspace por UUID: se resuelve el formulario y se valida
  el privilegio antes de montar React Form Entry o HTML Form Entry.
- Los endpoints REST deben probarse por rol; ocultar controles en el frontend no
  reemplaza la autorización del servidor.

`validate_csv_widths.py` verifica que los privilegios existan en el catálogo y
que `SIHSALUS Consulta Externa` conserve las capacidades mínimas. No valida aún
una matriz de tipos de encuentro porque esa migración no forma parte de este
checkpoint.
