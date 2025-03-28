import os
import shutil
import logging
import json
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from config import manager as config_manager
from core import hl7_parser
from core import hl7_watcher
from gui import config_window

class MainWindow(QtWidgets.QMainWindow):
    """
    Ventana principal de la aplicación HL7 Editor.
    
    Funcionalidades:
      - Seleccionar directorios de entrada, salida y backups.
      - Iniciar y detener la monitorización de archivos HL7.
      - Visualizar logs y gestionar configuraciones.
    """
    def __init__(self):
        super().__init__()
        # Inicializar atributos antes de crear la UI
        self.input_dir = ""
        self.output_dir = ""
        self.backup_dir = ""
        self.configurations = config_manager.load_configurations()
        self.active_config = None
        self.watcher = None

        self.setWindowTitle("HL7 Editor")
        self.resize(1000, 700)
        self.init_ui()  # Ahora self.configurations ya está definido
        self.log("Aplicación iniciada.")

    def init_ui(self):
        # Widget central y layout principal
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Selección de directorios
        dir_layout = QtWidgets.QHBoxLayout()
        self.input_btn = QtWidgets.QPushButton("Seleccionar Directorio de Entrada")
        self.output_btn = QtWidgets.QPushButton("Seleccionar Directorio de Salida")
        self.backup_btn = QtWidgets.QPushButton("Seleccionar Carpeta de Backups")
        dir_layout.addWidget(self.input_btn)
        dir_layout.addWidget(self.output_btn)
        dir_layout.addWidget(self.backup_btn)
        main_layout.addLayout(dir_layout)

        # Conectar botones de directorios
        self.input_btn.clicked.connect(self.select_input_dir)
        self.output_btn.clicked.connect(self.select_output_dir)
        self.backup_btn.clicked.connect(self.select_backup_dir)

        # Gestión de Configuraciones
        config_layout = QtWidgets.QHBoxLayout()
        self.config_combo = QtWidgets.QComboBox()
        self.refresh_config_combo()
        self.select_config_btn = QtWidgets.QPushButton("Seleccionar Configuración Activa")
        self.edit_config_btn = QtWidgets.QPushButton("Editar Configuración")
        self.export_config_btn = QtWidgets.QPushButton("Exportar Configuraciones")
        self.import_config_btn = QtWidgets.QPushButton("Importar Configuraciones")
        self.new_config_btn = QtWidgets.QPushButton("Nueva Configuración")
        config_layout.addWidget(self.config_combo)
        config_layout.addWidget(self.select_config_btn)
        config_layout.addWidget(self.edit_config_btn)
        config_layout.addWidget(self.new_config_btn)
        config_layout.addWidget(self.export_config_btn)
        config_layout.addWidget(self.import_config_btn)
        main_layout.addLayout(config_layout)

        # Conectar botones de configuración
        self.select_config_btn.clicked.connect(self.select_active_config)
        self.edit_config_btn.clicked.connect(self.edit_active_config)
        self.new_config_btn.clicked.connect(self.create_new_config)
        self.export_config_btn.clicked.connect(self.export_configs)
        self.import_config_btn.clicked.connect(self.import_configs)

        # Botones para iniciar y detener monitorización
        monitor_layout = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("Iniciar Monitorización")
        self.start_btn.setStyleSheet("background-color: green; color: white;")
        self.stop_btn = QtWidgets.QPushButton("Detener Monitorización")
        self.stop_btn.setStyleSheet("background-color: red; color: white;")
        monitor_layout.addWidget(self.start_btn)
        monitor_layout.addWidget(self.stop_btn)
        main_layout.addLayout(monitor_layout)

        self.start_btn.clicked.connect(self.start_monitoring)
        self.stop_btn.clicked.connect(self.stop_monitoring)

        # Área de logs
        self.log_area = QtWidgets.QTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(self.log_area)

    def log(self, message):
        """Muestra un mensaje en el área de logs y lo registra en el sistema."""
        self.log_area.append(message)
        logging.info(message)

    def select_input_dir(self):
        """Permite seleccionar el directorio de entrada."""
        directory = QFileDialog.getExistingDirectory(self, "Seleccione Directorio de Entrada")
        if directory:
            self.input_dir = directory
            self.log(f"Directorio de entrada: {self.input_dir}")

    def select_output_dir(self):
        """Permite seleccionar el directorio de salida."""
        directory = QFileDialog.getExistingDirectory(self, "Seleccione Directorio de Salida")
        if directory:
            self.output_dir = directory
            self.log(f"Directorio de salida: {self.output_dir}")

    def select_backup_dir(self):
        """Permite seleccionar la carpeta de backups."""
        directory = QFileDialog.getExistingDirectory(self, "Seleccione Carpeta de Backups")
        if directory:
            self.backup_dir = directory
            self.log(f"Carpeta de backups: {self.backup_dir}")

    def refresh_config_combo(self):
        """Actualiza el combobox de configuraciones disponibles."""
        self.config_combo.clear()
        self.config_combo.addItems(list(self.configurations.keys()))

    def select_active_config(self):
        """Selecciona la configuración activa según el combobox."""
        config_name = self.config_combo.currentText()
        if config_name:
            self.active_config = config_name
            self.log(f"Configuración activa: {self.active_config}")
        else:
            QMessageBox.warning(self, "Configuración", "No hay configuraciones disponibles.")

    def edit_active_config(self):
        """Abre la ventana para editar la configuración activa."""
        if not self.active_config:
            QMessageBox.warning(self, "Configuración", "Seleccione una configuración activa primero.")
            return
        rules = self.configurations.get(self.active_config, [])
        dialog = config_window.ConfigWindow(self.active_config, rules, self)
        if dialog.exec_():
            # Actualizar las reglas con los cambios realizados
            self.configurations[self.active_config] = dialog.get_rules()
            config_manager.save_configurations(self.configurations)
            self.log(f"Configuración '{self.active_config}' actualizada.")

    def create_new_config(self):
        """Crea una nueva configuración vacía a partir del nombre ingresado por el usuario."""
        config_name, ok = QtWidgets.QInputDialog.getText(self, "Nueva Configuración", "Ingrese el nombre de la nueva configuración:")
        if ok and config_name:
            if config_name in self.configurations:
                QMessageBox.warning(self, "Configuración", "Esa configuración ya existe.")
            else:
                self.configurations[config_name] = []  # Configuración vacía (lista de reglas)
                config_manager.save_configurations(self.configurations)
                self.refresh_config_combo()
                self.log(f"Nueva configuración '{config_name}' creada.")
        else:
            self.log("Creación de configuración cancelada o sin nombre ingresado.")

    def export_configs(self):
        """Exporta las configuraciones a un archivo JSON."""
        export_path, _ = QFileDialog.getSaveFileName(self, "Exportar Configuraciones", "", "JSON Files (*.json)")
        if export_path:
            config_manager.export_configurations(export_path, self.configurations)
            self.log(f"Configuraciones exportadas a: {export_path}")

    def import_configs(self):
        """Importa configuraciones desde un archivo JSON."""
        import_path, _ = QFileDialog.getOpenFileName(self, "Importar Configuraciones", "", "JSON Files (*.json)")
        if import_path:
            imported = config_manager.import_configurations(import_path)
            self.configurations.update(imported)
            config_manager.save_configurations(self.configurations)
            self.refresh_config_combo()
            self.log(f"Configuraciones importadas desde: {import_path}")

    def start_monitoring(self):
        """Inicia la monitorización del directorio de entrada."""
        if not (self.input_dir and self.output_dir and self.backup_dir):
            QMessageBox.warning(self, "Directorios", "Debe seleccionar los directorios de entrada, salida y backups.")
            return

        # Inicia el Watcher
        self.watcher = hl7_watcher.HL7Watcher(self.input_dir, self.process_file)
        self.watcher.start()
        self.log("Monitorización iniciada.")

    def stop_monitoring(self):
        """Detiene la monitorización del directorio de entrada."""
        if self.watcher:
            self.watcher.stop()
            self.log("Monitorización detenida.")
        else:
            self.log("No hay monitorización activa.")

    def process_file(self, file_path):
        """
        Procesa un archivo HL7:
          - Lee y parsea el archivo.
          - Aplica transformaciones según la configuración activa (si se seleccionó).
          - Escribe el archivo modificado en el directorio de salida.
          - Mueve el archivo original a la carpeta de backups.
        """
        self.log(f"Procesando archivo: {file_path}")
        try:
            segments = hl7_parser.parse_hl7_file(file_path)
            if self.active_config and self.active_config in self.configurations:
                transformations = self.configurations[self.active_config]
                segments = hl7_parser.apply_transformations(segments, transformations)
            else:
                self.log("No se aplican transformaciones (ninguna configuración activa).")
            # Generar el nombre del archivo de salida
            base_name = os.path.basename(file_path)
            output_file = os.path.join(self.output_dir, base_name)
            hl7_parser.write_hl7_file(segments, output_file)
            # Mover el archivo original a backups
            backup_file = os.path.join(self.backup_dir, base_name)
            shutil.move(file_path, backup_file)
            self.log(f"Archivo procesado. Original movido a backups: {backup_file}")
        except Exception as e:
            self.log(f"Error procesando {file_path}: {str(e)}")
