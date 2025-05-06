import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class HL7FileHandler(FileSystemEventHandler):
    """
    Handler para detectar y procesar nuevos archivos HL7 en un directorio.
    
    Args:
        process_file_callback (function): Función a llamar cuando se detecta un archivo HL7.
    """
    def __init__(self, process_file_callback):
        self.process_file_callback = process_file_callback

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.hl7'):
            logging.info(f"Archivo detectado (created): {event.src_path}")
            self.process_file_callback(event.src_path)

    def on_moved(self, event):
        # Captura archivos movidos / pegados (Cortar & Pegar)
        if not event.is_directory and event.dest_path.lower().endswith('.hl7'):
            logging.info(f"Archivo detectado (moved): {event.dest_path}")
            self.process_file_callback(event.dest_path)


class HL7Watcher:
    """
    Clase para monitorizar un directorio en busca de archivos HL7.
    
    Al iniciar, procesa también cualquier .hl7 existente en la carpeta.
    Luego queda escuchando eventos de created y moved.
    """
    def __init__(self, directory, process_file_callback):
        self.directory = directory
        self.process_file_callback = process_file_callback
        self.event_handler = HL7FileHandler(process_file_callback)
        self.observer = Observer()

    def start(self):
        """Procesa existentes, luego inicia la monitorización del directorio."""
        # 1) Procesar archivos ya existentes
        try:
            for fname in os.listdir(self.directory):
                full = os.path.join(self.directory, fname)
                if os.path.isfile(full) and full.lower().endswith('.hl7'):
                    logging.info(f"Archivo existente procesado al inicio: {full}")
                    self.process_file_callback(full)
        except Exception as e:
            logging.error(f"Error al procesar existentes en {self.directory}: {e}")

        # 2) Iniciar watcher para nuevos archivos
        self.observer.schedule(self.event_handler, self.directory, recursive=False)
        self.observer.start()
        logging.info(f"Iniciada la monitorización en: {self.directory}")

    def stop(self):
        """Detiene la monitorización."""
        self.observer.stop()
        self.observer.join()
        logging.info("Monitorización detenida.")
