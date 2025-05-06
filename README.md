HL7 Interface Manager
=====================

Descripción:
------------
HL7 Interface Manager es una aplicación de escritorio desarrollada en Python con PyQt5 que permite gestionar y transformar mensajes HL7 v2.x de forma ágil y configurada. Utilizando reglas personalizables, el usuario puede:

  - Eliminar segmentos completos.
  - Agregar nuevos segmentos en posiciones específicas, con valores definidos.
  - Modificar valores de campos individuales.
  - Reordenar campos dentro de un segmento, rellenando campos faltantes.
  - Copiar valores de un campo a otro, incluso entre segmentos distintos.
  - Agregar campos a segmentos existentes.

El programa monitorea un directorio de entrada en tiempo real (usando watchdog), procesa automáticamente los archivos HL7 que aparecen, aplica las transformaciones definidas en la configuración activa y guarda los mensajes resultantes en un directorio de salida. El archivo original se mueve a una carpeta de backups.

Contexto y problema que soluciona:
-----------------------------------
Históricamente, el departamento de interfaces tenía dificultades para implementar y mantener las múltiples variantes de interfaces HL7 requeridas por cada cliente. Cada cambio solicitaba semanas de desarrollo y pruebas.

Un ejemplo concreto es la interfaz con AthenaHealth:

  1. Al inicio del proyecto, Athena nos pidió reordenar varios segmentos en el mensaje HL7 que exportábamos. Este cambio nos llevó aproximadamente **3 semanas**.
  2. Después, Athena solicitó que **no enviemos el segmento IN1**. Esta petición aún está en progreso.

Este caso es solo uno de muchos en los que el problema es el mismo: la diversidad de reglas por cliente y el tiempo que consume aplicar cambios tradicionales.

HL7 Interface Manager resuelve esta necesidad al ofrecer una herramienta configurable, que permite definir, guardar y reutilizar reglas de transformación sin modificar el código fuente. Así, un equipo de soporte puede ajustar las interfaces en minutos en lugar de semanas.

Características principales:
---------------------------
- Interfaz gráfica intuitiva basada en PyQt5.
- Definición de configuraciones por cliente, exportables e importables en JSON.
- Reglas de transformación dinámicas: agregación, eliminación, modificación, reordenamiento y copia de campos.
- Monitorización automática de un directorio de entrada (24/7).
- Gestión de backups de los archivos originales.
- Registro de logs y mensajes en pantalla para trazabilidad.
- Empaquetado en un único ejecutable para Windows mediante PyInstaller.

Requisitos:
-----------
- Python 3.7+
- PyQt5
- watchdog

Instalación de dependencias:
---------------------------
```bash
pip install -r requirements.txt
```

Ejecución en desarrollo:
-----------------------
```bash
python main.py
```

Empaquetado para Windows:
-------------------------
```bash
pip install pyinstaller
pyinstaller --clean --onefile --windowed main.py
```
El ejecutable se encontrará en `dist/main.exe`.

Uso:
----
1. Seleccionar directorios de **Entrada**, **Salida** y **Backups**.
2. Crear o importar una **Configuración**.
3. Definir reglas de transformación en "Editar Configuración".
4. Iniciar la monitorización; cada archivo HL7 que aparezca será procesado automáticamente.

Contribuciones:
--------------
Las contribuciones son bienvenidas. Por favor, abre un _issue_ o _pull request_ en GitHub.

Licencia:
---------
MIT License. Consulta el archivo LICENSE para más detalles.

