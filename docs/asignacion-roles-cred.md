# Asignación de roles CRED y Vacunación por ambiente

Los privilegios y roles del módulo CRED y de Vacunación se declaran en este repo
(`configuration/backend_configuration/privileges/privileges_core-demo.csv` y
`configuration/backend_configuration/roles/roles-core.csv`) y los carga Initializer
en cada despliegue:

| Rol (declarado en content) | Privilegios |
|---|---|
| `CRED lectura` | los 7 `app:cred.*` de lectura + `app:immunization` |
| `CRED lectura y edicion` | los 14 `app:cred.*` + `app:immunization` + `app:immunization.edit` |
| `Vacunacion lectura` | `app:immunization` |
| `Vacunacion lectura y edicion` | `app:immunization` + `app:immunization.edit` |

## Por qué este repo NO declara `Enfermera CRED` ni `Medico`

Esos roles se crearon manualmente en cada servidor (QLTY, DEV) y tienen privilegios
que este repo no conoce. El dominio *roles* de Initializer usa **semántica de
reemplazo**: `RoleLineProcessor.fill()` llama a `role.setInheritedRoles(new HashSet<>(...))`
y `role.setPrivileges(new HashSet<>(...))` con únicamente lo que dice el CSV. Declarar
aquí `Medico` con solo la herencia CRED **borraría todos los privilegios actuales del
rol en el servidor**.

## Paso manual requerido (una vez por ambiente)

Con un usuario administrador: **Administration → Manage Roles** y editar:

1. `Enfermera CRED` → en *Inherited Roles* marcar **`CRED lectura y edicion`**.
2. `Medico` → en *Inherited Roles* marcar **`CRED lectura y edicion`**
   (o `CRED lectura` si se decide que el médico solo consulta).
3. (Opcional) personal vacunador que no hace CRED → asignar
   `Vacunacion lectura y edicion` directamente al usuario o a su rol.

`Admin` no requiere asignación: el frontend concede acceso total a usuarios con el
rol `System Developer` (bypass de superusuario de `userHasAccess`).

## Migración futura a GitOps

Para que content sea dueño de `Enfermera CRED`/`Medico`: exportar la definición
completa actual de cada rol (privilegios + roles heredados, idealmente vía
`GET /ws/rest/v1/role/<uuid>?v=full`), verificar que sea idéntica en todos los
ambientes, y recién entonces declararla íntegra en `roles-core.csv` agregando la
herencia CRED. Mientras las definiciones difieran entre ambientes, mantener el paso
manual.
