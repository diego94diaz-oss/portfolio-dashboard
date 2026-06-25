# Skill: Lector de Extractos y Portafolio

## Objetivo
Leer archivos PDF o Excel (extractos de cuenta, historial de transacciones, reportes de portafolio) para extraer automáticamente la cantidad de acciones, precio promedio de compra y movimientos recientes de cada activo, y actualizar `memory.md` con esa información.

---

## Archivos soportados

| Tipo | Formato | Ejemplos |
|------|---------|---------|
| Extracto de cuenta | PDF / Excel | Estado de cuenta del broker |
| Historial de transacciones | PDF / Excel / CSV | Reporte de compras y ventas |
| Reporte de portafolio | PDF / Excel | Snapshot de posiciones actuales |

---

## Flujo de ejecución

Cuando el usuario proporcione un archivo (PDF o Excel):

### Paso 1 — Identificar el tipo de documento
Determinar si el archivo es:
- **Portafolio/posiciones**: muestra el estado actual (cantidad de acciones, precio promedio, valor de mercado).
- **Historial de transacciones**: lista de compras y ventas con fecha, ticker, cantidad y precio.
- **Extracto mixto**: combina posiciones actuales con historial reciente.

### Paso 2 — Extraer los datos

**De un reporte de posiciones, extraer por cada activo:**
- Ticker
- Cantidad de acciones (shares)
- Precio promedio de compra
- Valor actual de la posición
- % del portafolio total

**De un historial de transacciones, extraer por cada operación:**
- Fecha
- Ticker
- Tipo: COMPRA o VENTA
- Cantidad de acciones
- Precio por acción
- Monto total de la operación

### Paso 3 — Calcular precio promedio ponderado
Si hay múltiples compras del mismo ticker, calcular el precio promedio ponderado:
`Precio promedio = Σ(precio_i × cantidad_i) / Σ(cantidad_i)`

### Paso 4 — Actualizar `memory.md`
- Completar las columnas `Precio compra (promedio)` y `Cantidad acciones` para cada ticker.
- Si un ticker del archivo no existe en `memory.md`, agregarlo.
- Registrar las transacciones recientes en la sección `Historial de transacciones`.
- Actualizar la fecha de última actualización.

### Paso 5 — Reportar al usuario
Mostrar un resumen de lo extraído antes de guardar:
- Posiciones actualizadas
- Transacciones detectadas (últimas 10)
- Alertas: tickers nuevos no reconocidos, discrepancias entre el archivo y `memory.md`

---

## Formato de extracción — Posiciones

```
Ticker | Acciones | Precio compra prom. | Valor actual | % portafolio
-------|----------|---------------------|--------------|-------------
AAPL   | 10       | $150.00             | $1,900.00    | 5.2%
...
```

## Formato de extracción — Transacciones recientes

```
Fecha      | Ticker | Tipo   | Acciones | Precio   | Monto total
-----------|--------|--------|----------|----------|------------
2026-05-10 | AAPL   | COMPRA | 5        | $185.00  | $925.00
2026-04-22 | GOOGL  | VENTA  | 2        | $395.00  | $790.00
...
```

---

## Sección a agregar en `memory.md`

Al finalizar, agregar o actualizar esta sección en `memory.md`:

```markdown
## Historial de transacciones recientes

| Fecha | Ticker | Tipo | Acciones | Precio | Monto total |
|-------|--------|------|----------|--------|-------------|
| ...   | ...    | ...  | ...      | ...    | ...         |

*Fuente: [nombre del archivo] — extraído el [fecha]*
```

---

## Notas
- Los archivos a procesar deben estar en `data/`.
- Si el PDF tiene texto seleccionable, leerlo directamente.
- Si el PDF es una imagen escaneada, indicar al usuario que lo convierta a texto o comparta los datos manualmente.
- Si el Excel tiene múltiples hojas, preguntar al usuario cuál contiene las posiciones y cuál el historial.
- No modificar `memory.md` sin mostrar primero el resumen al usuario para confirmación.
- Al finalizar el procesamiento, actualizar la tabla `Archivos procesados` en `data/README.md`.
