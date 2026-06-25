# Skill: Análisis de Activos vía Web Search (Fallback)

## Cuándo usar esta skill

**Esta skill es el fallback.** Activarla únicamente cuando `analizar_activos.py` no pueda obtener datos de un ticker (yfinance no lo cubre o retorna datos vacíos). Para el análisis habitual del portafolio, usar el script primero.

Casos típicos de fallback:
- Tickers sin cobertura en yfinance: `ASST`, `LDI`, `ASST-VRS`, `MSTR-VRS`
- El script imprime: `"Sin datos en yfinance. Usar skill PrecioWEB como fallback."`
- El usuario pide análisis manual con contexto adicional que el script no provee

---

## Flujo de ejecución

1. **Buscar en la web** por cada ticker:
   `[TICKER] stock current price analyst target price consensus 2026`

2. **Extraer**:
   - Precio actual de mercado
   - Precio objetivo promedio de consenso
   - Rango mínimo–máximo de precios objetivo
   - Número de analistas

3. **Leer `memory.md`** para obtener precio de compra, cantidad de acciones y % del portafolio.

4. **Calcular**:
   - Upside: `(precio_objetivo - precio_actual) / precio_actual × 100`
   - P&L: `(precio_actual - precio_compra) / precio_compra × 100`
   - Sugerencia de posición (si recomendación = COMPRAR MÁS): acciones a agregar sin superar 25%

5. **Emitir recomendación**:
   - Upside > 30% → **COMPRAR MÁS**
   - Upside 0–30% → **MANTENER**
   - Upside ≤ 0% → **VENDER**

6. **Guardar en `analysis/analisis_activos.md`** usando el formato estándar.

---

## Formato de salida

```
Ticker:                     [SYMBOL]
Precio actual:              $X.XX
Precio compra (promedio):   $X.XX | P&L actual: +/-X%
Precio objetivo (consenso): $X.XX (rango: $X – $X, N analistas) | Upside: +/-X%
Recomendación:              COMPRAR MÁS / MANTENER / VENDER
  → Sugerencia de posición:  [solo si COMPRAR MÁS] Agregar ~X acciones (+X% portafolio). Tope: no superar 25%.
  → Alerta concentración:    [solo si peso > 20%] ⚠️ Posición actual en X% del portafolio.
Fundamento:                 [2–3 líneas]
Riesgo principal a vigilar: [1 línea]
```

---

## Fuentes de búsqueda preferidas
- Yahoo Finance
- MarketWatch
- Finviz
- TipRanks

## Notas
- Si las fuentes difieren, usar el promedio o Yahoo Finance como referencia.
- Si no hay precio objetivo para un ticker, indicarlo y omitir la recomendación.
- Después de guardar en `analisis_activos.md`, actualizar manualmente la tabla resumen del archivo.
