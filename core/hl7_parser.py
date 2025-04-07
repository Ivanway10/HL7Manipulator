import logging

def parse_hl7_file(file_path):
    """
    Lee un archivo HL7 y lo separa en segmentos y campos.

    Args:
        file_path (str): Ruta del archivo HL7.

    Returns:
        list: Lista de segmentos, donde cada segmento es una lista de campos.
    """
    segments = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                segments.append(line.split('|'))
    return segments

def add_segment(segments, new_segment, position, values=None):
    """
    Inserta un nuevo segmento en la posición especificada con campos opcionales.

    Args:
        segments (list): Lista de segmentos actuales.
        new_segment (str): Nombre del nuevo segmento (ej: "NK1").
        position (int): Índice donde se insertará el segmento.
        values (list, optional): Lista de valores para los campos.

    Returns:
        list: Lista de segmentos actualizada.
    """
    segment_fields = [new_segment] + (values if values else [])
    if position < 0 or position > len(segments):
        position = len(segments)
    segments.insert(position, segment_fields)
    logging.info(f"Segmento agregado en la posición {position}: {segment_fields}")
    return segments

def modify_field(segments, segment_name, field_index, new_value):
    """
    Modifica el valor de un campo específico en el primer segmento que coincida con segment_name.

    Args:
        segments (list): Lista de segmentos.
        segment_name (str): Nombre del segmento (ej: "PID").
        field_index (int): Índice del campo a modificar.
        new_value (str): Nuevo valor para el campo.

    Returns:
        list: Lista de segmentos actualizada.
    """
    for seg in segments:
        if seg[0] == segment_name:
            if 0 <= field_index < len(seg):
                old_value = seg[field_index]
                seg[field_index] = new_value
                logging.info(f"Campo modificado en segmento {segment_name}: índice {field_index} de '{old_value}' a '{new_value}'")
            break
    return segments

def reorder_fields(segments, segment_name, new_order):
    """
    Reordena los campos de un segmento específico según un nuevo orden.
    Si el segmento no tiene suficientes campos, se rellenan con cadenas vacías.

    Args:
        segments (list): Lista de segmentos.
        segment_name (str): Nombre del segmento a reordenar.
        new_order (list): Lista de índices que define el nuevo orden.

    Returns:
        list: Lista de segmentos actualizada.
    """
    for seg in segments:
        if seg[0] == segment_name:
            # Rellenar con cadenas vacías si es necesario
            max_index = max(new_order)
            if len(seg) <= max_index:
                seg.extend([''] * (max_index - len(seg) + 1))
            seg[:] = [seg[i] for i in new_order]
            logging.info(f"Campos reordenados en segmento {segment_name}: nuevo orden {new_order}")
            break
    return segments

def copy_value(segments, from_segment, source_field, to_segment, dest_field):
    """
    Copia el valor de un campo a otro entre segmentos.

    Args:
        segments (list): Lista de segmentos.
        from_segment (str): Segmento de origen.
        source_field (int): Índice del campo fuente.
        to_segment (str): Segmento de destino.
        dest_field (int): Índice del campo destino.

    Returns:
        list: Lista de segmentos actualizada.
    """
    source_value = None
    for seg in segments:
        if seg[0] == from_segment and 0 <= source_field < len(seg):
            source_value = seg[source_field]
            break
    if source_value is not None:
        for seg in segments:
            if seg[0] == to_segment:
                while len(seg) <= dest_field:
                    seg.append('')
                seg[dest_field] = source_value
                logging.info(f"Valor copiado de {from_segment}[{source_field}] a {to_segment}[{dest_field}]: {source_value}")
                break
    return segments

def agregar_campos(segments, segment_name, new_fields, start_index=None):
    """
    Agrega nuevos campos a un segmento existente.
    Si start_index se proporciona, inserta en esa posición; de lo contrario, agrega al final.

    Args:
        segments (list): Lista de segmentos.
        segment_name (str): Nombre del segmento donde se agregarán los campos.
        new_fields (list): Lista de nuevos campos a agregar.
        start_index (int, optional): Posición en la que insertar los nuevos campos.

    Returns:
        list: Lista de segmentos actualizada.
    """
    for seg in segments:
        if seg[0] == segment_name:
            if start_index is None or start_index >= len(seg):
                seg.extend(new_fields)
                logging.info(f"Campos agregados al final del segmento {segment_name}: {new_fields}")
            else:
                for i, field in enumerate(new_fields):
                    seg.insert(start_index + i, field)
                logging.info(f"Campos insertados en el segmento {segment_name} en la posición {start_index}: {new_fields}")
            break
    return segments

def apply_transformations(segments, transformations):
    """
    Aplica una serie de transformaciones al mensaje HL7.

    Cada transformación es un diccionario que debe contener la clave "action" y los parámetros necesarios.
    Acciones implementadas:
      - delete_segment: Elimina todos los segmentos con el nombre especificado.
      - add_segment: Agrega un nuevo segmento en la posición indicada con campos opcionales.
      - modify_field: Modifica un campo específico.
      - reorder_fields: Reordena los campos de un segmento.
      - copy_value: Copia el valor de un campo a otro entre segmentos.
      - agregar_campos: Agrega nuevos campos a un segmento existente.

    Args:
        segments (list): Lista de segmentos del mensaje HL7.
        transformations (list): Lista de reglas de transformación.

    Returns:
        list: Lista de segmentos transformada.
    """
    for rule in transformations:
        action = rule.get('action')
        if action == 'delete_segment':
            segment_name = rule.get('segment')
            segments = [seg for seg in segments if seg[0] != segment_name]
            logging.info(f"Eliminado segmento: {segment_name}")
        elif action == 'add_segment':
            new_segment = rule.get('new_segment')
            position = rule.get('position', len(segments))
            values = rule.get('values', [])
            segments = add_segment(segments, new_segment, position, values)
        elif action == 'modify_field':
            segment_name = rule.get('segment')
            field_index = rule.get('field_index')
            new_value = rule.get('new_value')
            segments = modify_field(segments, segment_name, field_index, new_value)
        elif action == 'reorder_fields':
            segment_name = rule.get('segment')
            new_order = rule.get('new_order')
            segments = reorder_fields(segments, segment_name, new_order)
        elif action == 'copy_value':
            from_segment = rule.get('source_segment')
            source_field = rule.get('source_field')
            to_segment = rule.get('dest_segment')
            dest_field = rule.get('dest_field')
            segments = copy_value(segments, from_segment, source_field, to_segment, dest_field)
        elif action == 'agregar_campos':
            segment_name = rule.get('segment')
            new_fields = rule.get('values', [])
            start_index = rule.get('start_index')
            segments = agregar_campos(segments, segment_name, new_fields, start_index)
        else:
            logging.warning(f"Acción no reconocida: {action}")
    return segments

def write_hl7_file(segments, output_path):
    """
    Escribe la lista de segmentos en un archivo HL7.

    Args:
        segments (list): Lista de segmentos.
        output_path (str): Ruta del archivo de salida.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for seg in segments:
            f.write('|'.join(seg) + '\n')
    logging.info(f"Archivo HL7 escrito en: {output_path}")
