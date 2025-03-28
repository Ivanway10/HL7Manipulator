import json
import os
import logging

CONFIG_FILE = "configurations.json"

def load_configurations():
    """
    Carga las configuraciones desde el archivo JSON.
    Retorna un diccionario con las configuraciones.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_configurations(configs):
    """
    Guarda las configuraciones en el archivo JSON.
    
    Args:
        configs (dict): Diccionario de configuraciones a guardar.
    """
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(configs, f, indent=4)
    logging.info("Configuraciones guardadas.")

def export_configurations(export_path, configs):
    """
    Exporta las configuraciones a un archivo JSON especificado.
    
    Args:
        export_path (str): Ruta del archivo de exportación.
        configs (dict): Configuraciones a exportar.
    """
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(configs, f, indent=4)
    logging.info(f"Configuraciones exportadas a: {export_path}")

def import_configurations(import_path):
    """
    Importa configuraciones desde un archivo JSON.
    
    Args:
        import_path (str): Ruta del archivo a importar.
    
    Returns:
        dict: Configuraciones importadas o un diccionario vacío si falla.
    """
    if os.path.exists(import_path):
        with open(import_path, 'r', encoding='utf-8') as f:
            imported_configs = json.load(f)
        logging.info(f"Configuraciones importadas desde: {import_path}")
        return imported_configs
    else:
        logging.warning(f"El archivo de importación no existe: {import_path}")
        return {}
