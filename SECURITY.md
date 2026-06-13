# Seguridad y privacidad

Este repositorio es público y contiene información financiera de portafolio.

## Riesgos actuales

- Las posiciones, cantidades, precios promedio, efectivo y transacciones embebidas permiten inferir patrimonio e historial de inversión.
- La API key de Finnhub no está hardcodeada, pero se guarda en `localStorage` del navegador.

## Checklist antes de publicar cambios

- No agregar API keys, tokens ni credenciales.
- No agregar extractos de broker, cartolas ni capturas.
- Revisar si los datos embebidos son reales o ficticios.
- Preferir datos de ejemplo para vistas públicas.

## Siguiente mejora recomendada

Externalizar los arrays de portafolio/transacciones a archivos `*.local.js` ignorados por Git y mantener ejemplos ficticios versionados.
