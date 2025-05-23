from PyQt5 import QtWidgets, QtCore
import json

class ConfigWindow(QtWidgets.QDialog):
    """
    Ventana de diálogo para gestionar (editar/agregar/eliminar) las reglas de una configuración HL7,
    incluyendo soporte para condiciones y múltiples acciones.
    """
    def __init__(self, config_name, rules, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Editar Configuración: {config_name}")
        self.rules = rules
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # 1) Lista de reglas existentes
        layout.addWidget(QtWidgets.QLabel("Reglas existentes:"))
        self.rules_list = QtWidgets.QListWidget()
        self.refresh_rules()
        layout.addWidget(self.rules_list)

        # Editar / Eliminar
        btn_layout = QtWidgets.QHBoxLayout()
        self.edit_btn = QtWidgets.QPushButton("Editar Regla")
        self.del_btn = QtWidgets.QPushButton("Eliminar Regla")
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.del_btn)
        layout.addLayout(btn_layout)
        self.edit_btn.clicked.connect(self.edit_rule)
        self.del_btn.clicked.connect(self.delete_rule)

        layout.addWidget(self._separator())

        # 2) Widget para agregar nueva regla
        self.group = QtWidgets.QGroupBox("Agregar Nueva Regla")
        vbox = QtWidgets.QVBoxLayout(self.group)

        # Checkbox para condición
        self.cond_chk = QtWidgets.QCheckBox("Usar condición")
        vbox.addWidget(self.cond_chk)

        # Formulario de condición (oculto por defecto)
        self.cond_widget = QtWidgets.QWidget()
        cond_form = QtWidgets.QFormLayout(self.cond_widget)
        self.cond_segment = QtWidgets.QLineEdit()
        self.cond_field_idx = QtWidgets.QSpinBox()
        self.cond_field_idx.setMaximum(200)
        self.cond_operator = QtWidgets.QComboBox()
        self.cond_operator.addItems(["equals"])
        self.cond_value = QtWidgets.QLineEdit()
        cond_form.addRow("Segmento cond:",    self.cond_segment)
        cond_form.addRow("Índice cond:",      self.cond_field_idx)
        cond_form.addRow("Operador:",         self.cond_operator)
        cond_form.addRow("Valor cond:",       self.cond_value)
        self.cond_widget.setVisible(False)
        self.cond_chk.stateChanged.connect(
            lambda s: self.cond_widget.setVisible(s == QtCore.Qt.Checked)
        )
        vbox.addWidget(self.cond_widget)

        # Selección de acción
        action_layout = QtWidgets.QHBoxLayout()
        action_layout.addWidget(QtWidgets.QLabel("Acción:"))
        self.action_combo = QtWidgets.QComboBox()
        self.action_combo.addItems([
            "delete_segment", "add_segment", "modify_field",
            "reorder_fields", "copy_value", "agregar_campos"
        ])
        action_layout.addWidget(self.action_combo)
        vbox.addLayout(action_layout)

        # Parámetros de cada acción
        self.stacked = QtWidgets.QStackedWidget()
        # ---- delete_segment ----
        w1 = QtWidgets.QWidget()
        f1 = QtWidgets.QFormLayout(w1)
        self.delete_segment_edit = QtWidgets.QLineEdit()
        f1.addRow("Segmento:", self.delete_segment_edit)
        self.stacked.addWidget(w1)
        # ---- add_segment ----
        w2 = QtWidgets.QWidget()
        f2 = QtWidgets.QFormLayout(w2)
        self.add_segment_edit  = QtWidgets.QLineEdit()
        self.add_position_edit = QtWidgets.QLineEdit()
        self.add_values_edit   = QtWidgets.QLineEdit()
        self.add_position_edit.setPlaceholderText("Número entero (opcional)")
        self.add_values_edit.setPlaceholderText("Valores separados por |")
        f2.addRow("Segmento:", self.add_segment_edit)
        f2.addRow("Posición:", self.add_position_edit)
        f2.addRow("Valores:", self.add_values_edit)
        self.stacked.addWidget(w2)
        # ---- modify_field ----
        w3 = QtWidgets.QWidget()
        f3 = QtWidgets.QFormLayout(w3)
        self.modify_segment_edit     = QtWidgets.QLineEdit()
        self.modify_field_idx_edit   = QtWidgets.QLineEdit()
        self.modify_new_value_edit   = QtWidgets.QLineEdit()
        f3.addRow("Segmento:", self.modify_segment_edit)
        f3.addRow("Índice de campo:", self.modify_field_idx_edit)
        f3.addRow("Nuevo valor:", self.modify_new_value_edit)
        self.stacked.addWidget(w3)
        # ---- reorder_fields ----
        w4 = QtWidgets.QWidget()
        f4 = QtWidgets.QFormLayout(w4)
        self.reorder_segment_edit = QtWidgets.QLineEdit()
        self.reorder_order_edit   = QtWidgets.QLineEdit()
        self.reorder_order_edit.setPlaceholderText("Ej: 0,2,1,3")
        f4.addRow("Segmento:", self.reorder_segment_edit)
        f4.addRow("Nuevo orden:", self.reorder_order_edit)
        self.stacked.addWidget(w4)
        # ---- copy_value ----
        w5 = QtWidgets.QWidget()
        f5 = QtWidgets.QFormLayout(w5)
        self.copy_src_seg_edit = QtWidgets.QLineEdit()
        self.copy_src_idx_edit = QtWidgets.QLineEdit()
        self.copy_dst_seg_edit = QtWidgets.QLineEdit()
        self.copy_dst_idx_edit = QtWidgets.QLineEdit()
        f5.addRow("Seg fuente:", self.copy_src_seg_edit)
        f5.addRow("Índice fuente:", self.copy_src_idx_edit)
        f5.addRow("Seg destino:", self.copy_dst_seg_edit)
        f5.addRow("Índice destino:", self.copy_dst_idx_edit)
        self.stacked.addWidget(w5)
        # ---- agregar_campos ----
        w6 = QtWidgets.QWidget()
        f6 = QtWidgets.QFormLayout(w6)
        self.agregar_seg_edit  = QtWidgets.QLineEdit()
        self.agregar_pos_edit  = QtWidgets.QLineEdit()
        self.agregar_vals_edit = QtWidgets.QLineEdit()
        self.agregar_pos_edit.setPlaceholderText("Número entero (opcional)")
        self.agregar_vals_edit.setPlaceholderText("Valores separados por |")
        f6.addRow("Segmento:", self.agregar_seg_edit)
        f6.addRow("Posición:", self.agregar_pos_edit)
        f6.addRow("Valores:", self.agregar_vals_edit)
        self.stacked.addWidget(w6)

        vbox.addWidget(self.stacked)
        self.action_combo.currentIndexChanged.connect(self.stacked.setCurrentIndex)

        # Botón de agregar regla
        self.add_rule_btn = QtWidgets.QPushButton("Agregar Regla")
        self.add_rule_btn.clicked.connect(self.add_new_rule)
        vbox.addWidget(self.add_rule_btn)

        layout.addWidget(self.group)

        # Botón guardar
        self.save_btn = QtWidgets.QPushButton("Guardar Cambios")
        self.save_btn.clicked.connect(self.accept)
        layout.addWidget(self.save_btn)

    def _separator(self):
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setFrameShadow(QtWidgets.QFrame.Sunken)
        return sep

    def refresh_rules(self):
        self.rules_list.clear()
        for idx, rule in enumerate(self.rules, 1):
            self.rules_list.addItem(f"{idx}. {json.dumps(rule)}")

    def add_new_rule(self):
        rule = {}
        # Condición
        if self.cond_chk.isChecked():
            rule["condition"] = {
                "segment":     self.cond_segment.text().strip(),
                "field_index": self.cond_field_idx.value(),
                "operator":    self.cond_operator.currentText(),
                "value":       self.cond_value.text().strip()
            }
            rule["actions"] = []
        # Datos de la acción seleccionada
        action = self.action_combo.currentText()
        details = {}
        if action == "delete_segment":
            details = {"action": "delete_segment", "segment": self.delete_segment_edit.text().strip()}
        elif action == "add_segment":
            details = {
                "action":      "add_segment",
                "new_segment": self.add_segment_edit.text().strip(),
                "position":    int(self.add_position_edit.text()) if self.add_position_edit.text() else None,
                "values":      self.add_values_edit.text().split("|") if self.add_values_edit.text() else []
            }
        elif action == "modify_field":
            details = {
                "action":     "modify_field",
                "segment":    self.modify_segment_edit.text().strip(),
                "field_index":int(self.modify_field_idx_edit.text()),
                "new_value":  self.modify_new_value_edit.text().strip()
            }
        elif action == "reorder_fields":
            details = {
                "action":   "reorder_fields",
                "segment":  self.reorder_segment_edit.text().strip(),
                "new_order":[int(x) for x in self.reorder_order_edit.text().split(",")]
            }
        elif action == "copy_value":
            details = {
                "action":          "copy_value",
                "source_segment":  self.copy_src_seg_edit.text().strip(),
                "source_field":    int(self.copy_src_idx_edit.text()),
                "dest_segment":    self.copy_dst_seg_edit.text().strip(),
                "dest_field":      int(self.copy_dst_idx_edit.text())
            }
        elif action == "agregar_campos":
            details = {
                "action":     "agregar_campos",
                "segment":    self.agregar_seg_edit.text().strip(),
                "start_index":int(self.agregar_pos_edit.text()) if self.agregar_pos_edit.text() else None,
                "values":     self.agregar_vals_edit.text().split("|") if self.agregar_vals_edit.text() else []
            }

        # Insertar en rule
        if "condition" in rule:
            rule["actions"].append(details)
        else:
            rule = details

        # Agregar y refrescar
        self.rules.append(rule)
        self.refresh_rules()

    def edit_rule(self):
        sel = self.rules_list.currentRow()
        if sel < 0:
            return
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Editar Regla", "Modificar la regla (JSON):", text=json.dumps(self.rules[sel])
        )
        if ok:
            try:
                self.rules[sel] = json.loads(text)
                self.refresh_rules()
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"JSON inválido: {e}")

    def delete_rule(self):
        sel = self.rules_list.currentRow()
        if sel < 0:
            return
        self.rules.pop(sel)
        self.refresh_rules()

    def get_rules(self):
        return self.rules
