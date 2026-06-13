# Portfolio Dashboard

Dashboard HTML estático para seguimiento de portafolio USD y CLP.

## Archivos principales

- `index.html`: portafolio USD, precios live vía Finnhub y gráficos con Chart.js.
- `chile.html`: portafolio CLP / Bolsa de Santiago, precios vía Yahoo Finance y edición manual.

## Estado actual

- Repositorio público.
- La API key de Finnhub se ingresa desde la interfaz y se guarda en `localStorage`; no hay key hardcodeada.
- El HTML contiene posiciones y transacciones embebidas. Para uso público permanente, conviene migrar esos datos a archivos privados/generados o datos ficticios.

## Uso

No requiere build:

```bash
python -m http.server 8000
```

Abrir:

- `http://localhost:8000/index.html`
- `http://localhost:8000/chile.html`

## Recomendación de privacidad

Este repositorio debe tratarse como código/demostración. Si se quiere publicar en GitHub Pages, idealmente reemplazar posiciones reales por datos de ejemplo o cargar datos desde un archivo local no versionado.
