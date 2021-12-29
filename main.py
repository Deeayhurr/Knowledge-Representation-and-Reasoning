from PyQt5.QtCore import QThread
from PyQt5 import uic, Qt, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget
from query_translator import query_translator
import os
import sys


class Driver(Qt.QDialog):
    def __init__(self):

        # Initial Set up
        super(Driver, self).__init__()
        uic.loadUi("ui/main.ui", self)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.show()

        # User Inputs
        self.fluents = []
        self.actions = []
        self.agents = []
        self.PreConditionalFluentsChecboxes = []

        self.initial_states = []
        self.domains = []

        self.AddFluentBtn.clicked.connect(self.addFluent)
        self.AddActionBtn.clicked.connect(self.addAction)
        self.AddAgentBtn.clicked.connect(self.addAgent)
        self.InitialState_AddBtn.clicked.connect(self.addToInitialState)
        self.AddCause_Btn.clicked.connect(self.addCause)
        self.AddAfter_Btn.clicked.connect(self.addAfter)
        self.CausedFluent_comboBox.currentTextChanged.connect(
            self.onCausedFluentChangedListener
        )

        self.disableContainer(self.ActionsLayout)
        self.disableContainer(self.AgentLayout)
        self.disableContainer(self.CausesLayout)
        self.disableContainer(self.InitialState_verticalLayout)

        # TODO Change this
        # self.ExecuteBtn.setEnabled(False)

        self.ExecuteBtn.clicked.connect(self.execute_query)
        self.run_Btn.clicked.connect(self.add_to_prolog)

        self.query_translator = query_translator()

        self.delete_Btn.setStyleSheet("background-color: #5f2b3e; border-radius : 10px")
        self.run_Btn.setStyleSheet("background-color: #315f2b; border-radius : 10px")

        self.delete_Btn.clicked.connect(self.removeFromList)

        self.delete_Btn.setEnabled(False)
        self.run_Btn.setEnabled(False)

    def addFluent(self):
        fluent = self.Fluent_TextEdit.toPlainText()
        item = QtWidgets.QListWidgetItem(fluent)
        color = Qt.QColor()
        color.setRgb(11, 50, 13)
        item.setBackground(color)

        self.Fluent_TextEdit.clear()
        self.fluents.append(fluent)
        self.fluents.append("-" + fluent)
        self.Fluents_listWidget.addItem(item)

        self.updateInitialStateComboBox(fluent)
        self.enableContainer(self.ActionsLayout)

        self.onCausedFluentChangedListener(self.CausedFluent_comboBox.currentText())

    def addAction(self):
        action = self.Action_TextEdit.toPlainText()
        item = QtWidgets.QListWidgetItem(action)
        color = Qt.QColor()
        color.setRgb(50, 11, 11)
        item.setBackground(color)
        self.Actions_listWidget.addItem(item)

        self.Action_TextEdit.clear()
        self.actions.append(action)
        self.enableContainer(self.AgentLayout)
        self.Action_spinBox.addItem(action)

        self.addActionToCheckBoxGroup(action)

    def addAgent(self):
        agent = self.Agent_TextEdit.toPlainText()
        item = QtWidgets.QListWidgetItem(agent)
        color = Qt.QColor()
        color.setRgb(45, 50, 11)
        item.setBackground(color)
        self.Agents_listWidget.addItem(item)

        self.Agent_TextEdit.clear()
        self.agents.append(agent)
        self.enableContainer(self.InitialState_verticalLayout)
        self.Agent_spinBox.addItem(agent)
        self.AgentAfter_spinBox.addItem(agent)

    def addCause(self):
        action = self.Action_spinBox.currentText()
        agent = self.Agent_spinBox.currentText()
        caused_fluent = self.CausedFluent_comboBox.currentText()
        pre_conditional_fluents = []

        for checkbox in self.PreConditionalFluentsChecboxes:
            if checkbox.isChecked():
                pre_conditional_fluents.append(checkbox.text())

        pre_conditional_fluents = ", ".join(pre_conditional_fluents)

        if len(pre_conditional_fluents) > 0:
            message_to_show = f"{action} by {agent} causes {caused_fluent} if {pre_conditional_fluents}"
        else:
            message_to_show = f"{action} by {agent} causes {caused_fluent}"

        item = QtWidgets.QListWidgetItem(message_to_show)
        color = Qt.QColor()
        color.setRgb(4, 24, 56)
        item.setBackground(color)
        self.Representation.addItem(item)

        self.domains.append(message_to_show)

        self.delete_Btn.setEnabled(True)
        self.run_Btn.setEnabled(True)
        self.ExecuteBtn.setEnabled(True)

    def addAfter(self):
        fluent = self.FluentAfter_spinBox.currentText()
        agent = self.AgentAfter_spinBox.currentText()
        action = self.ActionAfter_SpinBox.currentText()
        message_to_show = f"{fluent} after {action} by {agent}"

        item = QtWidgets.QListWidgetItem(message_to_show)
        color = Qt.QColor()
        color.setRgb(4, 24, 56)
        item.setBackground(color)
        self.domains.append(message_to_show)
        self.Representation.addItem(item)

    def removeFromList(self):
        selected_items = self.Representation.selectedItems()
        for item in selected_items:
            self.Representation.takeItem(self.Representation.row(item))

    def addActionToCheckBoxGroup(self, action):
        self.ActionAfter_SpinBox.addItem(action)

    def updateInitialStateComboBox(self, state: str):
        self.InitialState_comboBox.addItem(state)
        self.InitialState_comboBox.addItem("-" + state)

        self.CausedFluent_comboBox.addItem(state)
        self.CausedFluent_comboBox.addItem("-" + state)

        self.FluentAfter_spinBox.addItem(state)
        self.FluentAfter_spinBox.addItem("-" + state)

    def addToInitialState(self):
        fluent = self.InitialState_comboBox.currentText()
        item = QtWidgets.QListWidgetItem(fluent)
        color = Qt.QColor()
        color.setRgb(11, 50, 13)
        item.setBackground(color)
        self.InitialState_listWidget.addItem(item)
        self.initial_states.append(fluent)
        self.InitialState_comboBox.removeItem(
            self.InitialState_comboBox.findText(fluent)
        )
        self.enableContainer(self.CausesLayout)

    def onCausedFluentChangedListener(self, value):
        fluentsToShow = [fluent for fluent in self.fluents if fluent != value]
        for i in reversed(range(self.PreConditionalFluentsBox.layout().count())):
            self.PreConditionalFluentsChecboxes.remove(
                self.PreConditionalFluentsBox.layout().itemAt(i).widget()
            )
            self.PreConditionalFluentsBox.layout().itemAt(i).widget().setParent(None)

        for fluent in fluentsToShow:
            checkbox = QtWidgets.QCheckBox(fluent)
            self.PreConditionalFluentsBox.addWidget(checkbox)
            self.PreConditionalFluentsChecboxes.append(checkbox)

    def disableContainer(self, layout):

        for child in layout.children():
            if isinstance(child, QtWidgets.QHBoxLayout) or isinstance(
                child, QtWidgets.QHBoxLayout
            ):
                index = child.layout().count() - 1
                while index >= 0:
                    try:
                        myWidget = child.layout().itemAt(index).widget()
                        myWidget.setEnabled(False)
                        index -= 1
                    except:
                        index -= 1
                        pass

            child.setEnabled(False)

    def enableContainer(self, layout):
        for child in layout.children():
            if isinstance(child, QtWidgets.QHBoxLayout) or isinstance(
                child, QtWidgets.QHBoxLayout
            ):
                index = child.layout().count() - 1
                while index >= 0:
                    try:
                        myWidget = child.layout().itemAt(index).widget()
                        myWidget.setEnabled(True)
                        index -= 1
                    except:
                        index -= 1
                        pass

            child.setEnabled(True)

    def execute_query(self):
        try:
            if not self.query_translator.inconsistent_domain:
                self.query_translator.read_query(self.Query.toPlainText())
                if self.query_translator.inconsistent_domain:
                    self.Result.setText(
                        str(self.query_translator.result) + ", Inconsistent domain"
                    )
                else:
                    self.Result.setText(str(self.query_translator.result))
            else:
                self.Result.setText(
                    str(self.query_translator.result) + ", Inconsistent domain"
                )
        except:
            pass

    def add_to_prolog(self):
        self.query_translator = query_translator()
        self.query_translator.add_domain(
            self.fluents, self.actions, self.agents, self.initial_states, self.domains
        )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Driver()
    app.exec_()  # execute application
