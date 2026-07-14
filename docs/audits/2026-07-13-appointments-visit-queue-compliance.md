# Citas, visitas y colas: alineamiento operativo y normativo

Fecha de revisión: 2026-07-14

## Alcance

Esta revisión documenta la metadata necesaria para que el check-in de una cita pueda conservar una relación
auditable con la visita y la entrada de cola. Cubre permisos, número de turno, zona horaria, duración de servicios y
la selección de cola. No reemplaza la definición local de oferta, horarios, cupos ni disponibilidad profesional.

## Base normativa y límite de interpretación

La [Resolución Ministerial N.° 811-2018/MINSA](https://www.gob.pe/institucion/minsa/normas-legales/195801-811-2018-minsa)
aprueba la Directiva Administrativa N.° 251-MINSA/2018/DGOS para elaborar e implementar el Plan "Cero Colas" en
las IPRESS públicas adscritas al MINSA y a gobiernos regionales. La
[comunicación oficial del MINSA](https://www.gob.pe/institucion/minsa/noticias/18706-minsa-aprueba-plan-cero-colas-en-los-esta-blecimientos-de-salud-a-nivel-nacional)
ubica su aplicación en admisión, consulta externa y apoyo al diagnóstico y tratamiento, y exige supervisar y
monitorear la reducción del tiempo de espera. También promueve herramientas informáticas para el otorgamiento de
citas sin eliminar el canal telefónico.

La directiva respalda el objetivo operativo y su monitoreo, pero no prescribe:

- un modelo de datos OpenMRS para relacionar cita, visita y cola;
- un número de turno como campo nacional obligatorio;
- una duración estándar por prestación;
- horarios de atención, cupos máximos o agendas de profesionales.

Por ello, el vínculo cita-visita-cola y el número de turno se implementan como controles locales de trazabilidad. No
se presentan como campos textualmente exigidos por la RM 811-2018/MINSA. Tampoco se inventan valores de horario o
capacidad bajo una supuesta exigencia normativa.

## Contrato de metadata

- OpenMRS Core: `Add Visits` y `Edit Visits` para crear y cerrar visitas.
- Queue OMOD: `Get Queues`, `Get Queue Entries` y `Manage Queue Entries` para crear, actualizar, transicionar o
  cerrar entradas de cola.
- Appointments OMOD: `View Appointments`, `Manage Appointments` y `Manage Own Appointments` para consultar y
  cambiar el estado de las citas que corresponden al operador.
- Privilegio clinico de FUA: `Generate Fua from Visit`
  (`2293389f-8595-491f-b842-5da867f59608`).
- Atributo de visita: `Número de turno de cola`
  (`06a0b8c6-cbdf-4b42-9cbd-871129db8758`), `FreeText`, cardinalidad `0..1`.
- Propiedad global: `sihsalus.queue.visitQueueNumberAttributeUuid` apunta al atributo anterior.
- Propiedad global: `sihsalus.timezone=America/Lima` fija la zona operativa para citas, visitas y colas.

El atributo es opcional a nivel del modelo de visita porque no toda visita ingresa por una cola. El flujo de check-in
de citas debe exigir la entrada de cola; otras visitas pueden seguir existiendo sin número de turno.

No existe en OpenMRS Core 2.8.7, Queue OMOD 3.0.0 ni Appointments OMOD 2.1.0 un privilegio o endpoint transaccional
denominado `Manage Appointment Queue Lifecycle`. Ese privilegio local fue retirado porque no autorizaba ninguna de
las operaciones oficiales. Sin un OMOD de integración, el frontend debe orquestar los recursos oficiales y permitir
reintentos; la metadata no convierte las tres escrituras en una única transacción de base de datos.

## Mínimo privilegio

`Manage Queue Entries` se asigna directamente solo a `Admision`, `Application: Register Appointments`,
`Application: Gestionar Colas Servicio`, `Personal de Emergencia`, `Doctor Consulta Externa` y al rol técnico
`super admin back privileges`. El rol `Enfermera` lo hereda de `Doctor Consulta Externa`.

Los roles operativos reciben los permisos mínimos que requieren para crear visitas o trabajar con colas:

- lectura de colas y entradas;
- lectura de los conceptos de estado, prioridad y servicio usados por la cola;
- lectura, creación y edición de visitas, tipos de visita y tipos de atributo;
- lectura de ubicaciones.

`Admision` y `Application: Register Appointments` conservan `app:home.citas.editar`, pero no reciben
`app:home.colasAtencion` ni `app:home.colasAtencion.editar`. Reciben `Manage Queue Entries` porque el POST y las
transiciones de Queue OMOD 3.0.0 lo exigen cuando el check-in crea la entrada de cola. El privilegio upstream es más
amplio que la navegación de Citas; por ello su asignación queda limitada a estos roles operativos y el frontend no
les expone el dashboard general de colas. Tampoco reciben
`Reset Appointment Status`, `Manage Queues`, gestión de salas ni permisos de purga.

`Application: Gestionar Colas Servicio` conserva su dashboard y la administración de catálogos de colas y salas.
Recibe `app:home.colasAtencion.editar`, `Manage Queue Entries` y `View Appointments`, pero no `Manage Appointments`:
cerrar una entrada no cambia por sí solo la cita asociada. No recibe reinicio de estado ni purga.
`Colas Servicio Medico` permanece en modo de lectura y no recibe `Manage Queue Entries`, edición de visitas ni
privilegios de configuración o purga.

`Personal de Emergencia` es un rol directo y no hereda `Doctor Consulta Externa`. Puede buscar y registrar
pacientes, crear y editar la visita, registrar triaje y atención, y crear, actualizar o transicionar entradas de
cola mediante `Manage Queue Entries`. Las nuevas emergencias continúan como atención inmediata y cola operativa,
no como citas programadas. No recibe `Manage Appointments`, `Manage Queues`, gestión de salas, reinicio de estados,
purga ni borrado de pacientes, visitas, encuentros u observaciones.

`Doctor Consulta Externa` y su rol heredero `Enfermera` pueden iniciar y finalizar una atención vinculada desde la
hoja clínica. Reciben `Manage Queue Entries` porque Queue OMOD 3.0.0 exige ese privilegio tanto para transicionar la
entrada como para el manejador que la cierra al finalizar una visita activa. También pueden generar o reintentar la
FUA de la visita con
`Generate Fua from Visit`, sin recibir `Manage Fua` ni `Update Fua`. La generación conserva un registro pendiente
por visita antes de invocar al generador externo, de modo que una caída no pierda la trazabilidad ni cree duplicados
al reintentar. No reciben `Manage Queues`, gestión de salas ni permisos de purga.

`Digitadores FUA` recibe navegación a la superficie FUA, lectura de visitas y el mismo privilegio estrecho de
generación porque su bandeja permite generación individual y masiva desde visitas. Conserva los permisos de gestión
FUA propios de su función, pero no recibe borrado de FUA o visitas ni lectura o administración de propiedades
globales.

Ninguno de estos roles de flujo recibe `Get Global Properties` ni `View Global Properties`; los módulos leen
únicamente las propiedades técnicas que necesitan mediante servicios internos controlados.

## Duraciones

Cada servicio de cita activo tiene exactamente un tipo de servicio activo. La duración base se copia de ese único
tipo para evitar que la agenda use un valor predeterminado distinto. El validador de CI exige que ambos valores se
mantengan alineados mientras la relación siga siendo inequívoca.

No se completan `Start Time`, `End Time` ni `Max Load`. Esos valores dependen de la oferta real del establecimiento y
requieren aprobación local. La duración existente tampoco se declara como duración normativa nacional.

## Mapeo de servicio de cita a cola

La preselección automática solo es segura cuando existe una única cola cuyo concepto de servicio y ubicación son
idénticos a los del servicio de cita. Con la configuración actual hay seis mapeos automáticos:

- Consulta ambulatoria por médico general -> Cola de Consulta Externa.
- Atención ambulatoria por obstetra -> Cola de Centro Obstétrico.
- Hospitalización de Cirugía General -> Cola de Centro Quirúrgico.
- Procedimientos de Laboratorio Clínico Tipo II-1 -> Cola de Laboratorio.
- Ecografía general y Doppler -> Cola de Diagnóstico por Imágenes.
- Atención en farmacia clínica -> Cola de Farmacia.

Los otros nueve servicios requieren selección explícita. Rehabilitación, hemodiálisis y nutrición tienen una cola
relacionada por nombre y ubicación, pero usan un concepto de servicio diferente; asociarlos automáticamente sería
una inferencia no respaldada por la metadata. Los otros seis no tienen una cola exacta configurada. No se usa la
ubicación como fallback porque una ubicación puede contener varias colas.

El inventario completo y verificable está en
[`2026-07-13-appointment-service-queue-mapping.csv`](2026-07-13-appointment-service-queue-mapping.csv).

## Validación

`.github/scripts/validate_appointment_queue_integrity.py` falla en CI si:

- reaparece el privilegio local obsoleto en el catálogo o en un rol;
- las asignaciones directas de `Manage Queue Entries` difieren de los roles operativos, de emergencia, clínico y
  administrativo aprobados;
- el privilegio estrecho de generación FUA falta en el rol clínico, digitador FUA o rol técnico, aparece en otro
  rol, o el personal clínico recibe administración general de FUA;
- el personal clínico pierde el permiso oficial para cerrar una cola/visita, o recibe configuración o purga;
- `Enfermera` deja de heredar el contrato clínico, o `Colas Servicio Medico` deja de ser de solo lectura;
- falta un permiso operativo mínimo o aparece un permiso administrativo prohibido;
- cambia el UUID, datatype o cardinalidad del número de turno;
- faltan las propiedades globales o cambia la zona horaria;
- una duración base difiere de su único tipo activo;
- el inventario de mapeos omite un servicio, marca como automático un mapeo ambiguo o queda desactualizado.

## Decisiones locales pendientes

Antes de activar capacidad o disponibilidad automática, el establecimiento debe aprobar y mantener por sede:

1. horarios efectivos por servicio;
2. cupos simultáneos y capacidad diaria;
3. profesionales habilitados y sus agendas;
4. equivalencias de servicio para los nueve mapeos manuales;
5. indicadores y metas de tiempo de espera del Plan Cero Colas.

Estas decisiones no deben derivarse de la RM 811-2018/MINSA ni de valores predeterminados del software.
