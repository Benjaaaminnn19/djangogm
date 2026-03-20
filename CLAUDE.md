# CLAUDE.md — Proyecto Gimnasio Leblon Calama

## Descripción del proyecto

Plataforma web para un cliente real (Gimnasio Leblon, Calama, Chile).
Sistema completo que incluye e-commerce, reserva de clases, gestión de membresías y pagos online.

## Stack técnico

- **Framework:** Django 5.2.5
- **Lenguaje:** Python
- **Base de datos:** PostgreSQL en producción (dj-database-url), SQLite en desarrollo
- **Archivos estáticos:** WhiteNoise
- **Variables de entorno:** python-decouple (.env)
- **Servidor:** Gunicorn
- **Deploy:** Railway (https://proud-integrity-production.up.railway.app)
- **Dominio producción:** gimnasiolebloncalama.cl
- **Pasarela de pago:** Flow (modo sandbox y producción, controlado por FLOW_SANDBOX en .env)

## Estructura de apps Django

### `principal/`
Es la app central del sistema. Contiene:
- `Miembro` — Usuario personalizado (AbstractUser). No usa `username`; autentica por `email` o `telefono`. Campos: nombre, fecha_inicio, activo.
- `Clase` — Clases del gimnasio con cupos y fecha.
- `Reserva` — Reserva de un Miembro a una Clase. Tiene campo `aprobado` (visto bueno del admin).
- `SolicitudPlan` — Compra de planes de membresía (Plan Azul, Amarillo, Verde). Estados: pendiente, pagado, activado, cancelado.
- `Asistencia` — Registro de entrada/salida de miembros.
- `Lead` — Formulario de contacto/interés.
- `authentication.py` — Lógica de autenticación personalizada.

### `tienda/`
E-commerce de productos del gimnasio. Contiene:
- `Producto` — Categorías: ropa, suplementos, accesorios. Precio en entero (pesos chilenos CLP). Tiene stock y flag activo.
- `Orden` — Orden de compra vinculada a Flow. Campos clave: `orden_id` (único), `flow_token`, `flow_order`, `productos` (JSONField con lista de productos), estado (pendiente/pagado/cancelado/fallido).
- `ImagenProducto` — Imágenes múltiples por producto con orden y flag `es_principal`.
- `flow_service.py` — Servicio de integración con la API de Flow.

### `participaciones/`
Módulo para registrar participaciones o actividades especiales. Contiene:
- `Participacion` — Código único auto-generado (formato PART-XXXXXX), correo, teléfono, descripción, estado.
- `Evidencia` — Archivos adjuntos a una participación (upload a `evidencias/`).

### `gimnasio/` (configuración)
- `settings.py` — Usa decouple para todas las variables sensibles. Flow tiene credenciales separadas para sandbox y producción.
- `urls.py` — URLs raíz del proyecto.

## Variables de entorno importantes (.env)

- `SECRET_KEY` — Clave secreta Django
- `DEBUG` — True en desarrollo, False en producción
- `ALLOWED_HOSTS` — Hosts permitidos
- `DATABASE_URL` — URL de PostgreSQL (Railway lo inyecta automáticamente)
- `FLOW_SANDBOX` — True = modo pruebas, False = producción real
- `FLOW_SANDBOX_API_KEY` / `FLOW_SANDBOX_SECRET_KEY` — Credenciales sandbox
- `FLOW_PROD_API_KEY` / `FLOW_PROD_SECRET_KEY` — Credenciales producción

## Decisiones de arquitectura tomadas

- El modelo `Miembro` extiende `AbstractUser` y elimina el campo `username`. La autenticación es por email O teléfono (lógica en `authentication.py`).
- Los precios se almacenan como `IntegerField` en pesos chilenos (CLP), sin decimales.
- Las órdenes de Flow guardan la lista de productos comprados como `JSONField` para no requerir una tabla intermedia.
- WhiteNoise maneja los archivos estáticos directamente desde Django (sin CDN externo).
- El proyecto está preparado para Railway: usa `dj-database-url` y `runtime.txt`.

## Convenciones del proyecto

- Los modelos usan `verbose_name` en español para el panel de administración.
- Los campos de estado usan `choices` con tuplas (valor_interno, etiqueta_legible).
- Las imágenes de productos suben a `media/productos/`, las evidencias a `media/evidencias/`.
- Los templates están en la carpeta raíz `templates/`.
- Los archivos estáticos sirven desde `static/` y se recopilan en `staticfiles/`.
