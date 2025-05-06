import sys
import os
import argparse
import logging
import time
import signal

from PyQt5 import QtWidgets
# importamos sólo en GUI mode
try:
    from gui.main_window import MainWindow
except ImportError:
    MainWindow = None

from config.manager import (
    load_configurations,
    save_configurations,
    export_configurations,
    import_configurations
)
from core.hl7_parser import (
    parse_hl7_file,
    apply_transformations,
    write_hl7_file
)
from core.hl7_watcher import HL7Watcher

# Directorio de logs
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "hl7_processor.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def process_file_cli(file_path, output_dir, backup_dir, config_name, configs):
    """Procesa un solo archivo HL7 y sale."""
    print(f"[CLI] Procesando archivo: {file_path}")
    logging.info(f"[CLI] Procesando archivo: {file_path}")

    segments = parse_hl7_file(file_path)
    if config_name and config_name in configs:
        segments = apply_transformations(segments, configs[config_name])

    output_file = os.path.join(output_dir or os.path.dirname(file_path), os.path.basename(file_path))
    write_hl7_file(segments, output_file)

    if backup_dir:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        os.replace(file_path, os.path.join(backup_dir, os.path.basename(file_path)))

    print(f"[CLI] Archivo procesado. Salida en: {output_file}")
    logging.info(f"[CLI] Archivo procesado. Salida en: {output_file}")

def monitor_cli(input_dir, output_dir, backup_dir, config_name, configs):
    """Arranca el watcher en modo headless y da feedback en consola."""
    print(f"[CLI] Monitor iniciando en: {input_dir} (config: {config_name})")
    logging.info(f"[CLI] Monitorizando {input_dir} (config: {config_name})")

    # Procesar archivos existentes al inicio
    try:
        for fname in os.listdir(input_dir):
            full = os.path.join(input_dir, fname)
            if os.path.isfile(full) and full.lower().endswith('.hl7'):
                print(f"[CLI] Procesando existente al inicio: {full}")
                process_file_cli(full, output_dir, backup_dir, config_name, configs)
    except Exception as e:
        print(f"[CLI][ERROR] Al procesar existentes: {e}")
        logging.error(f"[CLI] Error procesando existentes en {input_dir}: {e}")

    # Definir señal de terminación
    def _handle_signal(sig, frame):
        watcher.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # Callback para nuevos archivos
    def callback(path):
        print(f"[CLI] Detectado y procesando: {path}")
        try:
            process_file_cli(path, output_dir, backup_dir, config_name, configs)
        except Exception as e:
            print(f"[CLI][ERROR] Procesando {path}: {e}")
            logging.error(f"[CLI] Error procesando {path}: {e}")

    watcher = HL7Watcher(input_dir, callback)
    watcher.start()

    # Mantener vivo y mostrar heartbeat
    while True:
        time.sleep(10)
        print(f"[CLI] Monitor activo en: {input_dir} — esperando nuevos archivos...")

def main():
    parser = argparse.ArgumentParser(
        description="HL7 Interface Manager (GUI & CLI)"
    )
    sub = parser.add_subparsers(dest="cmd")

    # GUI (default)
    sub.add_parser("gui", help="Arranca en modo gráfico")

    # Monitor CLI
    sub_mon = sub.add_parser("monitor", help="Monitoriza un directorio en modo CLI")
    sub_mon.add_argument("--input-dir",   required=True, help="Carpeta de entrada")
    sub_mon.add_argument("--output-dir",  required=True, help="Carpeta de salida")
    sub_mon.add_argument("--backup-dir",  required=True, help="Carpeta de backups")
    sub_mon.add_argument("--config",      required=False, help="Nombre de la configuración a usar")

    # Procesar un solo archivo
    sub_one = sub.add_parser("process-file", help="Procesa un archivo y sale")
    sub_one.add_argument("file",           help="Archivo .hl7 a procesar")
    sub_one.add_argument("--output-dir",   help="Carpeta de salida (si no se especifica, misma carpeta que el archivo)")
    sub_one.add_argument("--backup-dir",   help="Carpeta de backups opcional")
    sub_one.add_argument("--config",       required=False, help="Nombre de la configuración a usar")

    # Exportar configuraciones
    sub_exp = sub.add_parser("export-config", help="Exporta configs a JSON")
    sub_exp.add_argument("path", help="Ruta donde guardar el JSON")

    # Importar configuraciones
    sub_imp = sub.add_parser("import-config", help="Importa configs desde JSON")
    sub_imp.add_argument("path", help="Ruta del JSON a importar")

    # (Opcional) Si deseas más comandos CLI, agrégalos aquí.

    args = parser.parse_args()
    configs = load_configurations()

    if args.cmd == "monitor":
        monitor_cli(args.input_dir, args.output_dir, args.backup_dir, args.config, configs)

    elif args.cmd == "process-file":
        process_file_cli(args.file, args.output_dir, args.backup_dir, args.config, configs)

    elif args.cmd == "export-config":
        export_configurations(args.path, configs)
        print(f"Configuraciones exportadas a {args.path}")

    elif args.cmd == "import-config":
        imported = import_configurations(args.path)
        configs.update(imported)
        save_configurations(configs)
        print(f"Configuraciones importadas desde {args.path}")

    else:
        # GUI por defecto
        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
