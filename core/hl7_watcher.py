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
            logging.info(f"Archivo detectado: {event.src_path}")
            self.process_file_callback(event.src_path)

class HL7Watcher:
    """
    Clase para monitorizar un directorio en busca de archivos HL7.
    
    Args:
        directory (str): Directorio a monitorizar.
        process_file_callback (function): Función a ejecutar al detectar un archivo.
    """
    def __init__(self, directory, process_file_callback):
        self.directory = directory
        self.event_handler = HL7FileHandler(process_file_callback)
        self.observer = Observer()

    def start(self):
        """Inicia la monitorización del directorio."""
        self.observer.schedule(self.event_handler, self.directory, recursive=False)
        self.observer.start()
        logging.info(f"Iniciada la monitorización en: {self.directory}")

    def stop(self):
        """Detiene la monitorización."""
        self.observer.stop()
        self.observer.join()
        logging.info("Monitorización detenida.")
