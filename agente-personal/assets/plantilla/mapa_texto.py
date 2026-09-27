"""Mapa de lectura de un archivo largo, para que el agente no lo lea completo.

    python mapa_texto.py "<archivo o carpeta>"        -> escribe el mapa y lo imprime
    python mapa_texto.py "<archivo>" --bloque 7        -> imprime solo ese bloque
    python mapa_texto.py "<archivo>" --buscar contrato -> imprime los bloques que traen esa palabra

Un texto de una hora de video son unas 25.000 fichas (tokens); su mapa, 1.300. El agente lee el
mapa, ve en qué bloque está lo que busca y pide solo ese pedazo. Sirve para transcripciones,
sentencias, actas, contratos y cualquier archivo largo que se revise cada semana.
"""
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

PALABRAS_BLOQUE = 1200  # ~8 minutos de alguien hablando
VACIAS = set("""a al algo algun alguna algunas alguno algunos ahi ahora aqui asi aun aunque bien cada como con
contra cual cuando de del desde donde dos el ella ellas ellos en entonces entre era eran eres es esa esas ese eso
esos esta estaba estamos estan estar estas este esto estos fue fueron ha habia hace hacer hacia han hasta hay la
las le les lo los mas me mi mientras muy nada ni no nos nosotros o os otra otro para pero poco por porque pues
que quien se segun ser si sin sobre son su sus tambien tan tanto te tiene tienen toda todas todo todos tu un una
uno unos usted ustedes ya yo bueno digamos verdad vamos vaya hacen hecho cosa cosas parte""".split())
CIFRA = re.compile(r"[^.]*?\b\d[\d.,]*\s*(?:%|por ciento|millones|millon|millón|mil|pesos|euros|dolares|dólares|puntos|años|año)\b[^.]*\.?")


def normalizar(p):
    p = unicodedata.normalize("NFD", p.lower())
    return "".join(c for c in p if unicodedata.category(c) != "Mn")


def bloques(texto):
    palabras = texto.split()
    return [" ".join(palabras[i:i + PALABRAS_BLOQUE]) for i in range(0, len(palabras), PALABRAS_BLOQUE)]


def temas(bloque):
    cuenta = Counter(w for w in (normalizar(p).strip(".,;:¿?¡!()\"'") for p in bloque.split())
                     if len(w) > 4 and w not in VACIAS)
    return ", ".join(w for w, _ in cuenta.most_common(8))


def mapa(archivo):
    texto = archivo.read_text(encoding="utf-8", errors="ignore")
    trozos = bloques(texto)
    total = len(texto.split())
    lineas = [f"# Mapa de {archivo.name}",
              f"{total:,} palabras · {len(trozos)} bloques de ~{PALABRAS_BLOQUE}",
              f'Lee solo los bloques que te sirvan: `python mapa_texto.py "{archivo}" --bloque N`', ""]
    for i, b in enumerate(trozos, 1):
        cifras = [c.strip() for c in CIFRA.findall(b)[:2]]
        lineas.append(f"## Bloque {i}")
        lineas.append(f"**Empieza.** {' '.join(b.split()[:35])}…")
        lineas.append(f"**Temas.** {temas(b)}")
        if cifras:
            lineas.append("**Cifras.** " + " · ".join(c[:160] for c in cifras))
        lineas.append("")
    return "\n".join(lineas)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    destino = Path(args[0])
    archivos = sorted(destino.glob("*.txt")) if destino.is_dir() else [destino]
    if "--bloque" in args:
        n = int(args[args.index("--bloque") + 1])
        trozos = bloques(archivos[0].read_text(encoding="utf-8", errors="ignore"))
        print(trozos[n - 1] if 1 <= n <= len(trozos) else f"No hay bloque {n}; son {len(trozos)}.")
        return
    if "--buscar" in args:
        aguja = normalizar(args[args.index("--buscar") + 1])
        for archivo in archivos:
            for i, b in enumerate(bloques(archivo.read_text(encoding="utf-8", errors="ignore")), 1):
                if aguja in normalizar(b):
                    print(f"\n=== {archivo.name} · bloque {i} ===\n{b}")
        return
    for archivo in archivos:
        salida = archivo.parent / "mapas" / (archivo.stem + ".md")
        salida.parent.mkdir(parents=True, exist_ok=True)
        texto = mapa(archivo)
        salida.write_text(texto, encoding="utf-8")
        print(texto if len(archivos) == 1 else f"{salida}")


if __name__ == "__main__":
    main()
