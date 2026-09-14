# Seguridad del agente

Un agente que lee correo y archivos y recibe órdenes desde un celular es útil justamente porque tiene acceso. Por eso la seguridad está en capas que no dependen de que el modelo "se porte bien".

## Capas
1. **Un solo dueño.** El bot solo procesa mensajes privados del ID de Telegram registrado con `configurar.py`. Todo lo demás se ignora y queda en el log.
2. **Sin puertos abiertos.** Usa *long polling*: el computador pregunta a Telegram; nadie se conecta al computador.
3. **Lista blanca por modo** (`--permission-mode dontAsk` + `--allowedTools`): lo que no está en la lista no se puede usar, y `--disallowedTools` gana siempre.
   - consulta: leer, buscar, listar, y crear borradores de correo.
   - trabajo (encargos): además crear, editar, mover, etiquetar, subir.
   - prohibidas: enviar, responder, reenviar, borrar, papelera, compartir, publicar, invitar, pagar, comprar, ejecutar comandos (Bash/PowerShell) y leer o escribir archivos `.env`.
4. **Archivos solo dentro de la carpeta de trabajo.** Las herramientas de archivos van con ruta: `Read(./**)`, `Glob(./**)`, `Grep(./**)`, `Edit(./**)`, `Write(./**)` (relativo a la carpeta donde corre Claude). Sin la ruta, `Read` y `Grep` leen cualquier archivo del computador: probado, un `Read` sin ruta leyó el `.env` de otra carpeta aunque existía la regla `Read(**/.env)`, que solo cubre la carpeta actual. Además se niega `Read(//**/.env)` (cualquier ruta del disco), que también frena a Grep. No agregues `Read`, `Grep`, `Edit` o `Write` sin ruta en `herramientas.json`.
   **Lectura de todo el computador** (`archivos.lectura = "todo"` en `config.json`): el bot quita la ruta solo a `Read`, `Glob` y `Grep`; `Edit` y `Write` siguen limitados a la carpeta de trabajo, así el agente no puede tocar su propia configuración. Quedan negados siempre `.env`, `.claude.json` (conectores con claves), `.credentials.json` (sesión de Claude) y `.ssh/`. Probado: con lectura abierta lee archivos comunes de otras carpetas y esos cuatro quedan bloqueados, también para Grep.
5. **Código de confianza para lo delicado.** Claude no genera binarios ni sube archivos: escribe Markdown y un pedido JSON en `<trabajo>/_entregas`; `entregas.py` valida rutas y formato y hace la subida.
6. **Secretos fuera del alcance.** `.env`, `config.json` y `herramientas.json` viven en la carpeta del agente, que no puede estar dentro de la carpeta de trabajo (`crear_agente.py` lo impide): así el agente no puede leer sus secretos ni ampliarse los permisos. El log reemplaza cualquier secreto por `<secreto>`. En macOS/Linux el `.env` queda con permisos 600.
7. **Contenido externo = datos.** Las instrucciones le dicen al agente que no obedezca órdenes que vengan dentro de correos, webs o documentos, y que se las cuente al dueño. Es la defensa contra inyección de instrucciones; la lista blanca es el respaldo si el modelo se equivoca.
8. **Datos sensibles fuera de la memoria.** Documentos de identidad, cuentas, contraseñas y direcciones no se guardan en MEMORIA.md ni en el Cerebro.

## Clasificar herramientas
`scripts/clasificar_herramientas.py` aplica estas reglas; revisa con la persona lo que marque.
- **Prohibida gana** si el nombre tiene: send, reply, forward, delete, trash, share, publish, post, invite, meeting (manda invitaciones), participant, react, spam, pay, purchase, transfer, execute, run, deploy, bulk, manage, permission, member.
- **Borradores** (draft) van en consulta: no salen de la bandeja y ahorran pedir permiso para algo inofensivo.
- **Lectura** (get, list, search, find, read, fetch...) → consulta.
- **Escritura** (create, update, add, move, label, upload, complete...) → trabajo. Revisa `remove` y `archive`: suelen ser inofensivos (quitar etiqueta, archivar tarjeta) pero depende del servicio.
- **Desconocida** → prohibida hasta que la persona decida. Explícale en una frase qué hace y pregúntale.

Si la persona pide permitir algo prohibido (por ejemplo, que envíe correos), explícale el riesgo concreto: cualquiera que logre meter una instrucción en un correo que el agente lea podría hacerlo enviar mensajes en su nombre. Si igual lo quiere, muévelo a `trabajo_extra`, anótalo en la guía de configuración y nunca lo pongas en consulta.

## Qué decirle a la persona (en simple)
- Lo que le dice al bot pasa por Telegram y por Claude (Anthropic), igual que cuando usa Claude normalmente.
- El token del bot es la llave: si se filtra, `/revoke` en BotFather y `configurar.py` otra vez.
- Cada computador necesita su propio bot: dos copias con el mismo token se roban los mensajes.
