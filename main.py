import sys
import os
import logging
from PyQt5 import QtWidgets
from gui import main_window

# Configuración de Logging: se asegura que la carpeta "logs" exista
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
logging.basicConfig(
    filename=f"{LOG_DIR}/hl7_processor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    """
    Punto de entrada principal de la aplicación HL7 Editor.
    Inicia la aplicación PyQt y muestra la ventana principal.
    """
    app = QtWidgets.QApplication(sys.argv)
    window = main_window.MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
