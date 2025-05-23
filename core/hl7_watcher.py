import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class HL7FileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.hl7'):
            logging.info(f"Archivo detectado (created): {event.src_path}")
            self.callback(event.src_path)

    def on_moved(self, event):
        if not event.is_directory and event.dest_path.lower().endswith('.hl7'):
            logging.info(f"Archivo detectado (moved): {event.dest_path}")
            self.callback(event.dest_path)

class HL7Watcher:
    def __init__(self, directory, callback):
        self.directory = directory
        self.callback = callback
        self.event_handler = HL7FileHandler(callback)
        self.observer = Observer()

    def start(self):
        # Procesar existentes
        try:
            for fname in os.listdir(self.directory):
                full = os.path.join(self.directory, fname)
                if os.path.isfile(full) and full.lower().endswith('.hl7'):
                    logging.info(f"Procesando existente al inicio: {full}")
                    self.callback(full)
        except Exception as e:
            logging.error(f"Error procesando existentes en {self.directory}: {e}")

        # Iniciar watcher
        self.observer.schedule(self.event_handler, self.directory, recursive=False)
        self.observer.start()
        logging.info(f"Iniciada monitorización en: {self.directory}")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        logging.info("Monitorización detenida.")