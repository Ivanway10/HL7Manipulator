from PyQt5 import QtWidgets, QtCore
import json

class ConfigWindow(QtWidgets.QDialog):
    """
    Ventana de diálogo para gestionar (editar/agregar/eliminar) las reglas de una configuración.

    Args:
        config_name (str): Nombre de la configuración a editar.
        rules (list): Lista de reglas asociadas.
    """
    def __init__(self, config_name, rules, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Editar Configuración: {config_name}")
        self.rules = rules
        self.resize(700, 500)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # Sección de reglas existentes
        rules_label = QtWidgets.QLabel("Reglas existentes:")
        layout.addWidget(rules_label)
        self.rules_list = QtWidgets.QListWidget()
        self.refresh_rules()
        layout.addWidget(self.rules_list)

        # Botones para editar o eliminar reglas
        btn_layout = QtWidgets.QHBoxLayout()
        self.edit_button = QtWidgets.QPushButton("Editar Regla")
        self.delete_button = QtWidgets.QPushButton("Eliminar Regla")
        btn_layout.addWidget(self.edit_button)
        btn_layout.addWidget(self.delete_button)
        layout.addLayout(btn_layout)

        self.edit_button.clicked.connect(self.edit_rule)
        self.delete_button.clicked.connect(self.delete_rule)

        # Separador visual
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(separator)

        # Sección para agregar una nueva regla con controles gráficos
        new_rule_group = QtWidgets.QGroupBox("Agregar Nueva Regla")
        new_rule_layout = QtWidgets.QVBoxLayout()

        # Seleccionar la acción
        action_layout = QtWidgets.QHBoxLayout()
        action_label = QtWidgets.QLabel("Acción:")
        self.rule_type_combo = QtWidgets.QComboBox()
        self.rule_type_combo.addItems([
            "delete_segment", "add_segment", "modify_field",
            "reorder_fields", "copy_value", "agregar_campos"
        ])
        action_layout.addWidget(action_label)
        action_layout.addWidget(self.rule_type_combo)
        new_rule_layout.addLayout(action_layout)

        # Usar QStackedWidget para mostrar formularios según la acción
        self.stacked_widget = QtWidgets.QStackedWidget()

        # Página para delete_segment: Solo se necesita el nombre del segmento
        delete_widget = QtWidgets.QWidget()
        delete_layout = QtWidgets.QFormLayout()
        self.delete_segment_edit = QtWidgets.QLineEdit()
        delete_layout.addRow("Segmento:", self.delete_segment_edit)
        delete_widget.setLayout(delete_layout)
        self.stacked_widget.addWidget(delete_widget)

        # Página para add_segment: Nuevo segmento, posición y valores
        add_widget = QtWidgets.QWidget()
        add_layout = QtWidgets.QFormLayout()
        self.add_segment_edit = QtWidgets.QLineEdit()
        self.add_position_edit = QtWidgets.QLineEdit()
        self.add_position_edit.setPlaceholderText("Número entero (opcional)")
        self.add_values_edit = QtWidgets.QLineEdit()
        add_layout.addRow("Nuevo Segmento:", self.add_segment_edit)
        add_layout.addRow("Posición:", self.add_position_edit)
        add_layout.addRow("Valores (separados por |):", self.add_values_edit)
        add_widget.setLayout(add_layout)
        self.stacked_widget.addWidget(add_widget)

        # Página para modify_field: Segmento, índice y nuevo valor
        modify_widget = QtWidgets.QWidget()
        modify_layout = QtWidgets.QFormLayout()
        self.modify_segment_edit = QtWidgets.QLineEdit()
        self.modify_field_index_edit = QtWidgets.QLineEdit()
        self.modify_new_value_edit = QtWidgets.QLineEdit()
        modify_layout.addRow("Segmento:", self.modify_segment_edit)
        modify_layout.addRow("Índice del campo:", self.modify_field_index_edit)
        modify_layout.addRow("Nuevo valor:", self.modify_new_value_edit)
        modify_widget.setLayout(modify_layout)
        self.stacked_widget.addWidget(modify_widget)

        # Página para reorder_fields: Segmento y nuevo orden
        reorder_widget = QtWidgets.QWidget()
        reorder_layout = QtWidgets.QFormLayout()
        self.reorder_segment_edit = QtWidgets.QLineEdit()
        self.reorder_order_edit = QtWidgets.QLineEdit()
        self.reorder_order_edit.setPlaceholderText("Ej: 0,2,1,3")
        reorder_layout.addRow("Segmento:", self.reorder_segment_edit)
        reorder_layout.addRow("Nuevo Orden:", self.reorder_order_edit)
        reorder_widget.setLayout(reorder_layout)
        self.stacked_widget.addWidget(reorder_widget)

        # Página para copy_value: Segmento fuente, campo fuente, segmento destino y campo destino
        copy_widget = QtWidgets.QWidget()
        copy_layout = QtWidgets.QFormLayout()
        self.copy_source_segment_edit = QtWidgets.QLineEdit()
        self.copy_source_field_edit = QtWidgets.QLineEdit()
        self.copy_dest_segment_edit = QtWidgets.QLineEdit()
        self.copy_dest_field_edit = QtWidgets.QLineEdit()
        copy_layout.addRow("Segmento fuente:", self.copy_source_segment_edit)
        copy_layout.addRow("Campo fuente:", self.copy_source_field_edit)
        copy_layout.addRow("Segmento destino:", self.copy_dest_segment_edit)
        copy_layout.addRow("Campo destino:", self.copy_dest_field_edit)
        copy_widget.setLayout(copy_layout)
        self.stacked_widget.addWidget(copy_widget)

        # Página para agregar campos: Segmento, posición (opcional) y nuevos campos
        agregar_widget = QtWidgets.QWidget()
        agregar_layout = QtWidgets.QFormLayout()
        self.agregar_segment_edit = QtWidgets.QLineEdit()
        self.agregar_position_edit = QtWidgets.QLineEdit()
        self.agregar_position_edit.setPlaceholderText("Número entero (opcional)")
        self.agregar_values_edit = QtWidgets.QLineEdit()
        agregar_layout.addRow("Segmento:", self.agregar_segment_edit)
        agregar_layout.addRow("Posición (opcional):", self.agregar_position_edit)
        agregar_layout.addRow("Nuevos Campos (separados por |):", self.agregar_values_edit)
        agregar_widget.setLayout(agregar_layout)
        self.stacked_widget.addWidget(agregar_widget)

        new_rule_layout.addWidget(self.stacked_widget)
        self.rule_type_combo.currentIndexChanged.connect(self.stacked_widget.setCurrentIndex)

        self.add_rule_btn = QtWidgets.QPushButton("Agregar Regla")
        new_rule_layout.addWidget(self.add_rule_btn)
        self.add_rule_btn.clicked.connect(self.add_new_rule)

        new_rule_group.setLayout(new_rule_layout)
        layout.addWidget(new_rule_group)

        self.save_button = QtWidgets.QPushButton("Guardar Cambios")
        layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.accept)

        self.setLayout(layout)

    def refresh_rules(self):
        self.rules_list.clear()
        for idx, rule in enumerate(self.rules):
            self.rules_list.addItem(f"{idx+1}. {json.dumps(rule)}")

    def add_new_rule(self):
        rule_type = self.rule_type_combo.currentText()
        new_rule = {"action": rule_type}
        try:
            if rule_type == "delete_segment":
                segment = self.delete_segment_edit.text().strip()
                if not segment:
                    QtWidgets.QMessageBox.warning(self, "Error", "El campo 'Segmento' es obligatorio.")
                    return
                new_rule["segment"] = segment

            elif rule_type == "add_segment":
                segment_text = self.add_segment_edit.text().strip()
                if not segment_text:
                    QtWidgets.QMessageBox.warning(self, "Error", "El campo 'Nuevo Segmento' es obligatorio.")
                    return
                new_rule["new_segment"] = segment_text
                pos_text = self.add_position_edit.text().strip()
                if pos_text:
                    new_rule["position"] = int(pos_text)
                if self.add_values_edit.text().strip():
                    new_rule["values"] = self.add_values_edit.text().strip().split("|")

            elif rule_type == "modify_field":
                segment = self.modify_segment_edit.text().strip()
                field_index = self.modify_field_index_edit.text().strip()
                new_value = self.modify_new_value_edit.text().strip()
                if not (segment and field_index and new_value):
                    QtWidgets.QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
                    return
                new_rule["segment"] = segment
                new_rule["field_index"] = int(field_index)
                new_rule["new_value"] = new_value

            elif rule_type == "reorder_fields":
                segment = self.reorder_segment_edit.text().strip()
                order_text = self.reorder_order_edit.text().strip()
                if not (segment and order_text):
                    QtWidgets.QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
                    return
                new_rule["segment"] = segment
                new_rule["new_order"] = [int(i.strip()) for i in order_text.split(',') if i.strip().isdigit()]

            elif rule_type == "copy_value":
                source_segment = self.copy_source_segment_edit.text().strip()
                source_field = self.copy_source_field_edit.text().strip()
                dest_segment = self.copy_dest_segment_edit.text().strip()
                dest_field = self.copy_dest_field_edit.text().strip()
                if not (source_segment and source_field and dest_segment and dest_field):
                    QtWidgets.QMessageBox.warning(self, "Error", "Todos los campos son obligatorios para copiar valores.")
                    return
                new_rule["source_segment"] = source_segment
                new_rule["source_field"] = int(source_field)
                new_rule["dest_segment"] = dest_segment
                new_rule["dest_field"] = int(dest_field)

            elif rule_type == "agregar_campos":
                segment = self.agregar_segment_edit.text().strip()
                if not segment:
                    QtWidgets.QMessageBox.warning(self, "Error", "El campo 'Segmento' es obligatorio para agregar campos.")
                    return
                new_rule["segment"] = segment
                pos_text = self.agregar_position_edit.text().strip()
                if pos_text:
                    new_rule["start_index"] = int(pos_text)
                if self.agregar_values_edit.text().strip():
                    new_rule["values"] = self.agregar_values_edit.text().strip().split("|")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Acción no reconocida.")
                return

            self.rules.append(new_rule)
            self.refresh_rules()

            current_index = self.rule_type_combo.currentIndex()
            current_widget = self.stacked_widget.widget(current_index)
            for child in current_widget.findChildren(QtWidgets.QLineEdit):
                child.clear()

        except ValueError as ve:
            QtWidgets.QMessageBox.warning(self, "Error", f"Error en la conversión de datos: {ve}")

    def edit_rule(self):
        selected = self.rules_list.currentRow()
        if selected < 0:
            return
        rule_str, ok = QtWidgets.QInputDialog.getText(self, "Editar Regla", "Modificar la regla (en formato JSON):", text=json.dumps(self.rules[selected]))
        if ok and rule_str:
            try:
                self.rules[selected] = json.loads(rule_str)
                self.refresh_rules()
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Error al parsear JSON: {e}")

    def delete_rule(self):
        selected = self.rules_list.currentRow()
        if selected < 0:
            return
        self.rules.pop(selected)
        self.refresh_rules()

    def get_rules(self):
        return self.rules
