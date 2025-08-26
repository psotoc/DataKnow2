from __future__ import annotations
import sys

from app.rag import ask as ASK

PREGUNTAS = [
    "Dime las sentencias (en palabras simples) de 3 demandas relacionadas con redes sociales. Devuelve exactamente 3.",
    "¿De qué se trataron esas 3 demandas? Explícalo sin jerga y de forma breve.",
    "¿Cuál fue la sentencia del caso que habla de acoso escolar?",
    "¿Cuál es el detalle de la demanda de acoso escolar? Explícalo claro y corto.",
    "¿Existen casos sobre el PIAR? Si los hay, ¿de qué trataron y cuál fue la sentencia?"
]

def main():
    k = 4 
    for i, q in enumerate(PREGUNTAS, 1):
        print(f"\n{'='*20} Pregunta {i} {'='*20}")
        print("Q:", q)
        try:
            ans = ASK(q, k=k) if 'k' in ASK.__code__.co_varnames else ASK(q)
        except Exception as e:
            print("Error", e)
            sys.exit(1)
        print("\nRespuesta:\n", ans.strip())

if __name__ == "__main__":
    main()
