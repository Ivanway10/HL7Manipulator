import logging

def parse_hl7_file(file_path):
    """
    Lee un archivo HL7 y lo separa en segmentos y campos.
    Returns: list de segmentos (listas de campos).
    """
    segments = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                segments.append(line.split('|'))
    return segments


def write_hl7_file(segments, output_path):
    """
    Escribe segmentos de vuelta a un archivo HL7.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for seg in segments:
            f.write('|'.join(seg) + '\n')
    logging.info(f"Archivo HL7 escrito en: {output_path}")

# Transformaciones atómicas

def add_segment(segments, new_segment, position, values=None):
    segment_fields = [new_segment] + (values if values else [])
    if position < 0 or position > len(segments):
        position = len(segments)
    segments.insert(position, segment_fields)
    logging.info(f"[RULE] add_segment {new_segment} at {position} values={values}")
    return segments


def modify_field(segments, segment_name, field_index, new_value):
    for seg in segments:
        if seg[0] == segment_name:
            if 0 <= field_index < len(seg):
                old = seg[field_index]
                seg[field_index] = new_value
                logging.info(f"[RULE] modify_field {segment_name}.{field_index} '{old}' -> '{new_value}'")
            break
    return segments


def reorder_fields(segments, segment_name, new_order):
    for seg in segments:
        if seg[0] == segment_name:
            max_idx = max(new_order)
            if len(seg) <= max_idx:
                seg.extend([''] * (max_idx - len(seg) + 1))
            seg[:] = [seg[i] for i in new_order]
            logging.info(f"[RULE] reorder_fields {segment_name} order={new_order}")
            break
    return segments


def copy_value(segments, source_segment, source_field, dest_segment, dest_field):
    source_val = None
    for seg in segments:
        if seg[0] == source_segment and 0 <= source_field < len(seg):
            source_val = seg[source_field]
            break
    if source_val is not None:
        for seg in segments:
            if seg[0] == dest_segment:
                while len(seg) <= dest_field:
                    seg.append('')
                seg[dest_field] = source_val
                logging.info(f"[RULE] copy_value {source_segment}.{source_field} -> {dest_segment}.{dest_field} '{source_val}'")
                break
    return segments


def agregar_campos(segments, segment_name, new_fields, start_index=None):
    for seg in segments:
        if seg[0] == segment_name:
            if start_index is None or start_index >= len(seg):
                seg.extend(new_fields)
                logging.info(f"[RULE] agregar_campos {segment_name} append {new_fields}")
            else:
                for i, f in enumerate(new_fields):
                    seg.insert(start_index + i, f)
                logging.info(f"[RULE] agregar_campos {segment_name} at {start_index} {new_fields}")
            break
    return segments

# Condición y orquestación

def _evaluate_condition(segments, cond):
    for seg in segments:
        if seg[0] == cond['segment']:
            idx = cond['field_index']
            if 0 <= idx < len(seg):
                res = seg[idx] == cond['value']
                logging.info(f"[COND] {cond['segment']}.{idx} == '{cond['value']}' -> {res}")
                return res
    return False


def _apply_single_rule(segments, rule):
    action = rule.get('action')
    if action == 'delete_segment':
        segments = [s for s in segments if s[0] != rule.get('segment')]
        logging.info(f"[RULE] delete_segment {rule.get('segment')}")
    elif action == 'add_segment':
        segments = add_segment(segments, rule.get('new_segment'), rule.get('position', len(segments)), rule.get('values', []))
    elif action == 'modify_field':
        segments = modify_field(segments, rule.get('segment'), rule.get('field_index'), rule.get('new_value'))
    elif action == 'reorder_fields':
        segments = reorder_fields(segments, rule.get('segment'), rule.get('new_order'))
    elif action == 'copy_value':
        segments = copy_value(segments, rule.get('source_segment'), rule.get('source_field'), rule.get('dest_segment'), rule.get('dest_field'))
    elif action == 'agregar_campos':
        segments = agregar_campos(segments, rule.get('segment'), rule.get('values', []), rule.get('start_index'))
    else:
        logging.warning(f"[RULE] Acción no reconocida: {action}")
    return segments


def apply_transformations(segments, transformations):
    for rule in transformations:
        cond = rule.get('condition')
        if cond:
            if not _evaluate_condition(segments, cond):
                continue
            for act in rule.get('actions', []):
                segments = _apply_single_rule(segments, act)
        else:
            segments = _apply_single_rule(segments, rule)
    return segments