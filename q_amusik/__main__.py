import sys

try:
    from .app import main
except (ImportError, ValueError) as error:
    print("q_AMusik necesita Python GTK 3 y GStreamer en Linux.\n"
          "Consulta las dependencias de Ubuntu/Zorin en README.md.\n"
          f"Detalle: {error}", file=sys.stderr)
    raise SystemExit(1)

raise SystemExit(main())
