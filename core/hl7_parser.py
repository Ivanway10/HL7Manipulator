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

def add_segment(segments, new_segment, position):
    """
    Inserta un nuevo segmento en la posición especificada.
    
    Args:
        segments (list): Lista de segmentos actuales.
        new_segment (str): Segmento completo en formato string (ej: "NK1|campo1|campo2").
        position (int): Índice donde se insertará el segmento.
    
    Returns:
        list: Lista de segmentos actualizada.
    """
    segment_fields = new_segment.strip().split('|')
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
    
    Args:
        segments (list): Lista de segmentos.
        segment_name (str): Nombre del segmento a reordenar.
        new_order (list): Lista de índices que define el nuevo orden.
    
    Returns:
        list: Lista de segmentos actualizada.
    """
    for seg in segments:
        if seg[0] == segment_name:
            if len(new_order) != len(seg):
                logging.warning(f"El nuevo orden no coincide con el número de campos en el segmento {segment_name}.")
                continue
            seg[:] = [seg[i] for i in new_order]
            logging.info(f"Campos reordenados en segmento {segment_name}: nuevo orden {new_order}")
            break
    return segments

def copy_value(segments, segment_name, source_field, dest_field):
    """
    Copia el valor de un campo a otro en el primer segmento que coincida con segment_name.
    
    Args:
        segments (list): Lista de segmentos.
        segment_name (str): Nombre del segmento.
        source_field (int): Índice del campo origen.
        dest_field (int): Índice del campo destino.
    
    Returns:
        list: Lista de segmentos actualizada.
    """
    for seg in segments:
        if seg[0] == segment_name:
            if source_field < len(seg) and dest_field < len(seg):
                seg[dest_field] = seg[source_field]
                logging.info(f"Valor copiado en segmento {segment_name}: de índice {source_field} a índice {dest_field}")
            break
    return segments

def apply_transformations(segments, transformations):
    """
    Aplica una serie de transformaciones al mensaje HL7.
    
    Cada transformación es un diccionario que debe contener la clave "action" y los parámetros necesarios.
    
    Acciones implementadas:
      - delete_segment: Elimina todos los segmentos con el nombre especificado.
      - add_segment: Agrega un segmento en la posición indicada.
      - modify_field: Modifica un campo específico.
      - reorder_fields: Reordena los campos de un segmento.
      - copy_value: Copia el valor de un campo a otro.
    
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
            segments = add_segment(segments, new_segment, position)
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
            segment_name = rule.get('segment')
            source_field = rule.get('source_field')
            dest_field = rule.get('dest_field')
            segments = copy_value(segments, segment_name, source_field, dest_field)
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