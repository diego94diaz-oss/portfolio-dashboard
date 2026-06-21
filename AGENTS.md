# AGENTS.md — portfolio-dashboard

## Rol del repositorio

Dashboard HTML público de inversiones/portfolio.

## Reglas específicas

- Priorizar estabilidad visual y carga rápida.
- No romper el layout responsive.
- PC A debe validar cambios visuales importantes.
- PC B puede ejecutar smoke tests, revisar endpoints/publicación y corregir errores menores.
- Capturas, referencias visuales y assets pesados deben vivir en Drive.

## Drive asociado sugerido

`Drive/Mercurio/proyectos/portfolio-dashboard/`

Subcarpetas:

- `capturas/`
- `assets/`
- `referencias/`

## Reglas generales para agentes

- Trabajar en ramas; no modificar `main` directamente salvo instrucción explícita.
- Antes de cambiar archivos: revisar `git status` y hacer `git pull --ff-only`.
- No tocar secretos, tokens, credenciales ni archivos `.env`.
- No subir datos personales/sensibles sin confirmación.
- Preferir cambios pequeños, verificables y con commit claro.
- Si hay duda entre reescribir o preguntar, preguntar.
- PC A se usa para cambios pesados y revisión visual.
- PC B/Hermes/OpenClaw se usa para auditoría, coordinación y cambios menores.
- Assets grandes o documentos de trabajo deben vivir en Google Drive, no en el repo.

## Convención de ramas

- `pc-a/...` para trabajo desde PC A con Claude Code.
- `mercurio/...` para trabajo desde Hermes/Mercurio en PC B.
- `openclaw/...` para tareas desde OpenClaw.
- `docs/...` para documentación.
- `fix/...` para correcciones pequeñas.
- `exp/...` para experimentos.

## Flujo mínimo

```bash
git pull --ff-only
git checkout -b mercurio/nombre-tarea
# cambios
git status
git add .
git commit -m "tipo: descripción clara"
git push -u origin HEAD
```
