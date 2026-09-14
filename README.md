# Agente personal por Telegram con Claude Code

Una **skill de Claude Code** que te arma, conversando y paso a paso, tu propio asistente personal: le escribes o le mandas una nota de voz por Telegram desde el celular, y Claude Code trabaja en tu computador y te responde por el mismo chat.

Sin frameworks de terceros ni servidores intermedios: tu plan de Claude, Python y Telegram.

## Qué hace el agente
- Entiende **texto y notas de voz**; transcribe localmente con faster-whisper.
- **Consulta** tus archivos, correo, calendario y documentos a través de conectores (Gmail, Google Drive, Calendar, Microsoft 365, Notion, Nextcloud…).
- **Hace encargos**: «haz…», «quiero que agendes…», «¿puedes…?». Crea y edita archivos, eventos y tareas.
- **Investiga** en la web y entrega en **Word o PDF** en tu nube o carpeta sincronizada.
- **Recuerda**: «recuerda que…» y lo guarda en su memoria.
- **Mantenimiento semanal**: cierra la semana, limpia la memoria y te manda el resumen.
- Arranca solo con el computador (Windows, macOS o Linux).

## Seguridad de serie
- Solo obedece a tu cuenta de Telegram. No abre puertos.
- Permisos por lista blanca en cada modo. **Nunca** envía correos o mensajes (deja borradores), no borra, no comparte, no paga, no ejecuta comandos.
- Escribe solo dentro de su carpeta de trabajo; los secretos (`.env`, sesión de Claude, llaves SSH) quedan bloqueados.
- Trata como datos, no como órdenes, lo que venga en correos o páginas web.

## Requisitos
- Plan de Claude **Pro o Max** con [Claude Code](https://docs.claude.com/claude-code) instalado y la sesión iniciada.
- Python 3.10 o más reciente.
- Telegram en el celular.
- Un computador que pueda quedar encendido cuando quieras usar el agente.

## Instalación
1. Descarga este repositorio (botón **Code › Download ZIP**) o clónalo.
2. Copia la carpeta `agente-personal` a tu carpeta de skills:
   - Windows: `C:\Users\<tu usuario>\.claude\skills\agente-personal`
   - macOS / Linux: `~/.claude/skills/agente-personal`
3. Abre Claude Code en el computador donde vivirá el agente y escribe: **«quiero armar mi propio agente personal»**.

La skill te hace las preguntas (sistema, nombre del asistente, cuántos computadores, cómo revisar tu información, conectores, permisos, voz, documentos, rutina), instala todo, lo prueba y te deja una **guía de configuración** y una **guía de uso**.

## Estructura
```
agente-personal/
├── SKILL.md              el flujo de preguntas que sigue Claude
├── assets/plantilla/     el bot: agente.py, entregas, mantenimiento, configurar.py, servicio.py
├── scripts/              verificar entorno, crear agente, listar y clasificar herramientas, generar guías
└── references/           conectores, seguridad, sistemas operativos, memoria y Cerebro, problemas frecuentes
```

## ¿Algo falló?
Abre un **Issue** con la plantilla «Reportar un error»: tu sistema operativo, en qué fase iba la skill y el mensaje de error (**borra tokens, contraseñas o datos personales** antes de pegarlo). Así lo vamos corrigiendo entre todos.

## Estado
Probado en Windows 11. El arranque automático de macOS y Linux está implementado pero falta que alguien lo pruebe: si lo haces, cuéntanos.

## Licencia
MIT. Úsalo, adáptalo y compártelo.
