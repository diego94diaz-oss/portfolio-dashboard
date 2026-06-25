# Skill: Dashboard Manager

Skill unificada para `app/index.html`. Cubre dos responsabilidades:
- **Sección A — Datos**: actualizar `portfolio[]`, `recommendations[]`, `transactions[]` y tarjetas de resumen.
- **Sección B — Diseño**: agregar secciones, gráficos, columnas, cambios de layout o estilo visual.

Ambas editan el mismo archivo. Si el cambio requiere datos nuevos que no están en el HTML, empezar por la Sección A antes de aplicar el diseño.

---

## Cuándo activar esta skill

| Trigger | Sección |
|---------|---------|
| "actualiza la app", "refresca el dashboard" | A — Datos |
| Se procesaron nuevos CSVs o hay análisis nuevos en `analisis_activos.md` | A — Datos |
| "agregá una sección / columna / gráfico" | B — Diseño |
| "cambiá el color / layout / responsive" | B — Diseño |
| "la app no se ve bien en móvil" | B — Diseño |

---

## Stack tecnológico

| Elemento | Detalle |
|----------|---------|
| Archivo principal | `app/index.html` (autocontenido — todo en un solo archivo) |
| CSS | Variables CSS en `:root`, sin frameworks externos |
| JS | Vanilla JS, sin frameworks |
| Gráficos | Chart.js 4.4.0 (CDN) |
| Precios live | Finnhub API (key guardada en localStorage) |
| Deploy | GitHub Pages → `https://diego94diaz-oss.github.io/portfolio-dashboard/` |
| Git remote | `https://github.com/diego94diaz-oss/portfolio-dashboard.git` |

### Paleta de colores (variables CSS)
```css
--bg:       #0f1117   /* fondo principal */
--surface:  #1a1d27   /* cards y tablas */
--surface2: #22263a   /* headers de tabla, hover */
--border:   #2e3248   /* bordes */
--text:     #e8eaf0   /* texto principal */
--muted:    #7a7f99   /* texto secundario */
--green:    #22c55e   /* positivo */
--red:      #ef4444   /* negativo */
--yellow:   #f59e0b   /* alertas */
--blue:     #3b82f6   /* info */
--purple:   #a855f7   /* dividendos */
--accent:   #6366f1   /* botones, highlights */
```

---

## SECCIÓN A — Actualizar datos

### Fuentes de datos

| Fuente | Dato a extraer |
|--------|---------------|
| `memory.md` | Posiciones, precios de compra, cantidad de acciones, % portafolio, retorno, efectivo |
| `analysis/analisis_activos.md` | Tabla resumen: upside y señal por ticker |
| `memory.md` → sección transacciones | Últimas 15 transacciones |

> **Atajo**: si `analizar_activos.py` ya fue ejecutado con opción de actualizar dashboard, los arrays `portfolio[]` y `recommendations[]` ya están actualizados. Solo verificar `transactions[]` y tarjetas de resumen.

### Paso 1 — Leer fuentes
1. Leer `memory.md` → tabla de portafolio e historial de transacciones.
2. Leer `analysis/analisis_activos.md` → tabla resumen (sección `## Resumen — Última recomendación por ticker`).

### Paso 2 — Mapear señales
- `COMPRAR MÁS` → `"buy"`
- `MANTENER` → `"hold"`
- `VENDER` → `"sell"`
- Sin datos / advertencia → `"warn"`

### Paso 3 — Actualizar `app/index.html`

Arrays a editar en el bloque `<script>`:
```javascript
const portfolio = [
  { ticker:"XXXX", name:"Nombre", shares:X, buyPrice:X, price:X, value:X, pct:X, ret:X, alert:bool },
];

const recommendations = [
  { ticker:"XXXX", upside:X, signal:"buy|hold|sell|warn",
    fundamento:"...", riesgo:"..." },
];

const transactions = [
  { date:"YYYY-MM-DD", asset:"TICK — Nombre", type:"Compra|Venta|Dividendo", shares:"X", price:"$X", amount:"$X" },
];
```

Tarjetas de resumen (HTML directo):
- Valor total, retorno total, costo total, efectivo disponible
- Alertas de concentración (tickers > 20%)
- Fecha en el `<header>`

### Reglas de orden
- `portfolio[]`: mayor a menor valor de mercado
- `transactions[]`: más reciente a más antigua (máx. 15)
- `recommendations[]`: sell → buy → hold → warn

---

## SECCIÓN B — Cambios de diseño

### Flujo obligatorio

1. Leer `app/index.html` completo antes de editar.
2. Identificar exactamente qué secciones del HTML/CSS/JS modificar. Preferir ediciones quirúrgicas.
3. Aplicar el cambio.
4. Tomar screenshot con Chrome headless para verificar antes del push:

```powershell
$url = "file:///C:/Users/PC/Desktop/Claude%20Code/app/index.html"
$img = "$env:TEMP\dash_preview.png"
Start-Process -FilePath "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  -ArgumentList "--headless=new","--screenshot=$img","--window-size=1400,900","--no-sandbox",$url
Start-Sleep -Seconds 5
```
Leer la imagen y confirmar el resultado. Para móvil usar `--window-size=390,844`.

5. Solo si la captura es correcta, hacer push:
```bash
cd "c:\Users\PC\Desktop\Claude Code\app"
git add index.html
git commit -m "descripción del cambio"
git push
```

### Reglas CSS
- Usar siempre las variables CSS de `:root` (no hardcodear colores).
- Nuevas clases al bloque `<style>` existente, ordenadas temáticamente.
- Mobile-first: todo componente nuevo necesita su `@media (max-width: 768px)`.
- Tablas con `overflow-x: auto` para scroll horizontal en móvil.

### Reglas JavaScript
- No agregar librerías externas sin evaluar si Chart.js ya lo cubre.
- Orden en `<script>`: datos → live prices → render → charts → init().
- `init()` siempre al final del script.
- No usar `DOMContentLoaded` (el script está al final del `<body>`).

### Reglas Chart.js
- `responsive: true, maintainAspectRatio: false` con altura fija en `.chart-wrap`.
- Registrar `Chart.defaults` globales al inicio del bloque de charts.
- Tooltips en español con callbacks cuando sea relevante.

### Estructura HTML de secciones
- `.grid-full` → ancho completo
- `.grid-2` → dos columnas
- `.charts-row` → tres gráficos
- `.cards` → tarjetas de resumen
- Nuevas secciones: entre los charts y la tabla de posiciones, o al final antes del footer.

### Componentes reutilizables
```html
<!-- Card -->
<div class="card">
  <div class="label">TÍTULO</div>
  <div class="value green/red">VALOR</div>
  <div class="sub">subtítulo</div>
</div>

<!-- Badge -->
<span class="badge badge-buy">COMPRAR +</span>
<span class="badge badge-hold">MANTENER</span>
<span class="badge badge-sell">VENDER</span>
<span class="badge badge-warn">REVISAR</span>

<!-- Alerta -->
<div class="alert">⚠️ <span>TICKER</span> — mensaje</div>

<!-- Tabla -->
<div class="table-wrap">
  <table><thead>...</thead><tbody>...</tbody></table>
</div>

<!-- Gráfico Chart.js -->
<div class="chart-card">
  <div class="section-title">TÍTULO</div>
  <div class="chart-wrap"><canvas id="miChart"></canvas></div>
</div>
```
