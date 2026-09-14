# Memoria y Cerebro

## Tres formas de revisar el computador
| Opción | Preparación | Costo por pregunta | Cuándo conviene |
|---|---|---|---|
| A. Carpeta tal como está | ninguna | alto: busca a ciegas cada vez | poca información, o para empezar ya |
| B. Carpeta organizada (áreas › proyectos, CLAUDE.md corto en cada uno) | moderada | medio-bajo | casi siempre |
| C. Cerebro local (índice y páginas por proyecto) | alta, una sola vez | muy bajo: sabe dónde buscar | muchos proyectos activos |
| B + C | organizar lo activo y hacer su Cerebro | muy bajo | la que mejor funciona |

Si hay muchísima información vieja que ya no se usa, no hagas Cerebro de todo: no es rentable. Organiza y resume solo lo activo; lo archivado puede quedar fuera de la carpeta de trabajo.

**Un solo computador:** nada de nube ni sincronización. La memoria vive local y el mantenimiento semanal la limpia.

## Organizar carpetas sin romper nada (opción B)
1. Haz un inventario y propón la estructura (áreas › proyectos). Muéstrala como árbol y espera el visto bueno.
2. Pide cerrar Word, Excel y cualquier programa con archivos abiertos: un archivo en uso hace que un movimiento quede a medias.
3. Simula primero: lista qué se moverá de dónde a dónde, sin mover nada.
4. Respalda la lista de rutas originales para poder deshacer.
5. Mueve carpetas completas con un movimiento atómico (renombrar), no copiando y borrando; si una falla, detente y reporta.
6. Crea un CLAUDE.md de 3-5 líneas por área y por proyecto: qué es, qué hay, reglas propias.
7. Verifica que no quedó nada suelto y que accesos directos o apps que apuntaban a rutas viejas sigan funcionando.

## Crear el Cerebro (opción C, una sola vez)
1. Recorre la carpeta de trabajo proyecto por proyecto (solo lo activo). Lee los CLAUDE.md, READMEs y nombres de archivos; abre documentos solo si hace falta entender el estado.
2. Escribe una página por proyecto en `01 Proyectos` (qué es, estado, pendientes, dónde está), una por persona u organización recurrente y las decisiones que crucen proyectos.
3. Arma `index.md` con una línea por página y abre `log.md` con la fecha de la ingesta.
4. Muéstrale el índice a la persona y corrige lo que diga. De ahí en adelante el agente lo mantiene: al cerrar trabajos importantes y en el mantenimiento semanal.

## Opción simple (memoria sin Cerebro)
- `MEMORIA.md` en la carpeta de trabajo: una lista corta de datos y preferencias de la persona.
- `CLAUDE.md` en la carpeta de trabajo la importa (`@MEMORIA.md`), así el agente la carga en cada mensaje.
- «Recuerda que...» agrega una línea. El mantenimiento semanal la limpia.
- Sirve para una persona con un computador y pocos proyectos.

## Opción Cerebro (varios proyectos o varios computadores)
Inspirado en el «LLM Wiki» de Andrej Karpathy: en vez de que el modelo busque a ciegas cada vez, mantiene una wiki en Markdown que él mismo actualiza.

```
Cerebro/
├── index.md                       qué hay y dónde: una línea por proyecto (nombre · computador · carpeta · estado)
├── log.md                         bitácora: una línea por trabajo importante
├── 01 Proyectos/<Proyecto>.md     qué es, estado, pendientes, decisiones
├── 02 Personas y organizaciones/  clientes, colaboradores, empresas
└── 03 Decisiones y aprendizajes/  reglas que cruzan proyectos
```

Cada página de proyecto empieza con un encabezado simple:
```
---
area: Clientes
pc: Portátil
ruta: "Documentos/Proyectos/Cocina Martínez"
estado: activo
---
```
Se lleva bien con Obsidian si la persona quiere verla como grafo, pero no lo necesita.

## Varios computadores
La idea: **una sola fuente de verdad en la nube, sincronizada en cada equipo**.
1. El Cerebro vive en una carpeta sincronizada (Nextcloud, Google Drive, OneDrive o Dropbox con su app de escritorio).
2. En cada computador, la carpeta sincronizada del Cerebro queda **dentro** de la carpeta de trabajo (o la carpeta de trabajo es la sincronizada): el agente solo lee y escribe dentro de su carpeta de trabajo. Su `CLAUDE.md` dice «lee el Cerebro».
3. El campo `pc` de cada proyecto le dice al agente dónde están los archivos. Si están en otro equipo, lo dice en vez de inventar.
4. Cada computador que quiera su propio agente necesita **su propio bot de Telegram** (token distinto).
5. Escala a 3, 4 o más equipos, o a un servidor que concentre el trabajo: todos leen y escriben el mismo Cerebro.

Conflictos de sincronización: si dos equipos editan la misma página a la vez, la app de sincronización crea una copia en conflicto. Por eso las páginas son cortas y el log es de una línea por entrada.

## Qué nunca va en la memoria
Documentos de identidad, números de cuenta, contraseñas, direcciones, datos de salud de terceros. Viven en los documentos del proyecto; la memoria solo dice dónde están.
