import sys
import os

try:
    if os.environ.get("Q_AMUSIK_EMBEDDED") == "1":
        from .app import main
    else:
        from .desktop import main
except (ImportError, ValueError) as error:
    print("q_AMusik necesita GTK 3, GStreamer y Qt WebEngine en Linux.\n"
          "Consulta las dependencias de Ubuntu/Zorin en README.md.\n"
          f"Detalle: {error}", file=sys.stderr)
    raise SystemExit(1)

raise SystemExit(main())
