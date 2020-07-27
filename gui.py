import PyQt5.QtWidgets
import pyqtgraph
from pyqtgraph import PlotWidget, plot
import sys
import GroupMeStats

class GUI(PyQt5.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_gui()
    
    def init_gui(self):
        self.setWindowTitle("GroupMeStats GUI")
        self.init_tab_widget()
        self.setCentralWidget(self.tab_widget)
        self.setMinimumSize(300,300)
        self.show()

    def init_tab_widget(self):
        self.tab_widget = TabWidget(self)


class TabWidget(PyQt5.QtWidgets.QWidget):
    def __init__(self, parent):
        super(TabWidget, self).__init__(parent)
        self.layout = PyQt5.QtWidgets.QVBoxLayout(self)
        self.users = set()
        self.setup()

    def setup(self):
        self.tab_widget = PyQt5.QtWidgets.QTabWidget()
        self.group_tab = PyQt5.QtWidgets.QWidget()
        self.chat_tab = PyQt5.QtWidgets.QWidget()
        self.settings_tab = PyQt5.QtWidgets.QWidget()
        self.stats_tab = PyQt5.QtWidgets.QScrollArea()

        self.setup_group_tab()
        self.setup_chat_tab()
        self.setup_settings_tab()
        self.setup_stats_tab()

        self.tab_widget.addTab(self.group_tab, "Groups")
        self.tab_widget.addTab(self.chat_tab, "Chats")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)

    def setup_group_tab(self):
        self.load_groups_btn = PyQt5.QtWidgets.QPushButton('Load Groups', self)
        self.load_groups_btn.clicked.connect(self.setup_group_table_widget)
        self.group_tab_layout = PyQt5.QtWidgets.QGridLayout(self.group_tab)
        self.group_tab_sublayout = PyQt5.QtWidgets.QHBoxLayout()
        self.group_tab_sublayout.addStretch()
        self.group_tab_sublayout.addWidget(self.load_groups_btn)
        self.group_tab_sublayout.addStretch()
        self.group_tab_layout.addLayout(self.group_tab_sublayout, 0, 0)
        self.group_tab.setLayout(self.group_tab_layout)

    def setup_chat_tab(self):
        self.load_chats_btn = PyQt5.QtWidgets.QPushButton('Load Chats', self)
        self.chat_tab_layout = PyQt5.QtWidgets.QGridLayout(self.chat_tab)
        self.load_chats_btn.clicked.connect(self.setup_chat_table_widget)
        self.chat_tab_sublayout = PyQt5.QtWidgets.QHBoxLayout()
        self.chat_tab_sublayout.addStretch()
        self.chat_tab_sublayout.addWidget(self.load_chats_btn)
        self.chat_tab_sublayout.addStretch()
        self.chat_tab_layout.addLayout(self.chat_tab_sublayout, 0, 0)
        self.chat_tab.setLayout(self.chat_tab_layout)
    
    def setup_settings_tab(self):
        print("This is the settings tab")
    
    def setup_stats_tab(self):
        self.stats_tab.setVerticalScrollBarPolicy(PyQt5.QtCore.Qt.ScrollBarAlwaysOn)
        self.stats_tab_widget = PyQt5.QtWidgets.QWidget() #content
        self.stats_tab.setWidget(self.stats_tab_widget)
        self.stats_tab_layout = PyQt5.QtWidgets.QFormLayout(self.stats_tab_widget)
        self.stats_tab.setWidgetResizable(True)
        test = PyQt5.QtWidgets.QLabel("test")
        self.stats_tab_layout.addRow(test)
        
    
    def get_groups(self):
        while not GroupMeStats.set_token(None, from_gui=True):
            self.token_error_dialog()
            self.get_token()
        valid_token = False
        while not valid_token:
            try:
                groups = GroupMeStats.get_groups(self.users, suppress_print=True)
                valid_token = True
            except KeyError:
                valid_token = False
                self.token_error_dialog()
                self.get_token()
        return groups

    def get_chats(self):
        while not GroupMeStats.set_token(None, from_gui=True):
            self.token_error_dialog()
            self.get_token()
        valid_token = False
        while not valid_token:
            try:
                chats = GroupMeStats.get_chats(self.users, suppress_print=True)
                valid_token = True
            except KeyError:
                valid_token = False
                self.token_error_dialog()
                self.get_token()
        return chats
    
    def get_token(self):
        token_dialog = PyQt5.QtWidgets.QDialog()
        token_dialog.setWindowTitle("Token")
        token_dialog_layout = PyQt5.QtWidgets.QVBoxLayout(token_dialog)
        token_lineedit = PyQt5.QtWidgets.QLineEdit()
        token_lineedit.setPlaceholderText("Please enter your token")
        okay_btn = PyQt5.QtWidgets.QPushButton("Confirm")
        okay_btn.clicked.connect(lambda:self.save_entered_token(token_lineedit.text()))
        okay_btn.clicked.connect(lambda:token_dialog.close())
        token_dialog_layout.addWidget(token_lineedit)
        token_dialog_layout.addWidget(okay_btn)
        token_dialog.setLayout(token_dialog_layout)
        token_dialog.exec()
    
    def token_error_dialog(self):
        incorrect_token_dialog = PyQt5.QtWidgets.QErrorMessage()
        incorrect_token_dialog.setWindowTitle("Token Error")
        incorrect_token_dialog.showMessage("Your token appears to be incorrect or missing.\nPlease enter your token in the following dialog")
        incorrect_token_dialog.exec()
    
    def save_entered_token(self, token):
        if len(token) > 0:
            with open('token.txt', 'w') as token_file:
                token_file.write(token)
            GroupMeStats.TOKEN = token
    
    def setup_group_table_widget(self):
        self.groups = self.get_groups()
        self.group_table_widget = PyQt5.QtWidgets.QTableWidget(len(self.groups[1]), 3, self)
        self.group_table_widget.setHorizontalHeaderLabels(['Group', 'Message Count', 'Group ID'])
        i = 0
        for group in self.groups[1]:
            self.group_table_widget.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(self.groups[2][group][0]))
            self.group_table_widget.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(str(self.groups[2][group][1])))
            self.group_table_widget.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem(str(group)))
            i += 1
        self.group_table_widget.itemSelectionChanged.connect(self.group_table_widget_update_selection)
        self.group_table_widget.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectRows)
        self.group_table_widget.setEditTriggers(PyQt5.QtWidgets.QTableWidget.NoEditTriggers)
        header = self.group_table_widget.horizontalHeader()
        header.setSectionResizeMode(0, PyQt5.QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, PyQt5.QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, PyQt5.QtWidgets.QHeaderView.ResizeToContents)
        self.group_tab_layout.addWidget(self.group_table_widget, 1, 0)
        self.group_analysis_all_btn = PyQt5.QtWidgets.QPushButton('Analyze All', self)
        self.group_analysis_selected_btn = PyQt5.QtWidgets.QPushButton('Analyze Selected', self)
        self.group_analysis_all_btn.clicked.connect(self.retrieve_group_messages)
        self.group_analysis_selected_btn.clicked.connect(self.retrieve_group_messages)
        group_tab_sublayout_2 = PyQt5.QtWidgets.QHBoxLayout()
        group_tab_sublayout_2.addStretch()
        group_tab_sublayout_2.addWidget(self.group_analysis_all_btn)
        group_tab_sublayout_2.addStretch()
        group_tab_sublayout_2.addWidget(self.group_analysis_selected_btn)
        group_tab_sublayout_2.addStretch()
        self.group_tab_layout.addLayout(group_tab_sublayout_2, 2, 0)
        label = PyQt5.QtWidgets.QLabel("No multithreading currently. GUI may lock up when retrieving messages from GroupMe servers.")
        label.setWordWrap(True)
        label.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        group_tab_sublayout3 = PyQt5.QtWidgets.QHBoxLayout()
        group_tab_sublayout3.addWidget(label)
        self.group_tab_layout.addLayout(group_tab_sublayout3, 3, 0)
    
    def setup_chat_table_widget(self):
        self.chats = self.get_chats()
        self.chat_table_widget = PyQt5.QtWidgets.QTableWidget(len(self.chats[1]), 3, self)
        self.chat_table_widget.setHorizontalHeaderLabels(['Chat', 'Message Count', 'Chat ID'])
        i = 0
        for chat in self.chats[1]:
            self.chat_table_widget.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(self.chats[2][chat][0]))
            self.chat_table_widget.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(str(self.chats[2][chat][1])))
            self.chat_table_widget.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem(str(chat)))
            i += 1
        self.chat_table_widget.itemSelectionChanged.connect(self.chat_table_widget_update_selection)
        self.chat_table_widget.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectRows)
        self.chat_table_widget.setEditTriggers(PyQt5.QtWidgets.QTableWidget.NoEditTriggers)
        header = self.chat_table_widget.horizontalHeader()
        header.setSectionResizeMode(0, PyQt5.QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, PyQt5.QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, PyQt5.QtWidgets.QHeaderView.ResizeToContents)
        self.chat_tab_layout.addWidget(self.chat_table_widget, 1, 0)
        self.chat_analysis_all_btn = PyQt5.QtWidgets.QPushButton('Analyze All', self)
        self.chat_analysis_selected_btn = PyQt5.QtWidgets.QPushButton('Analyze Selected', self)
        self.chat_analysis_all_btn.clicked.connect(self.retrieve_chat_messages)
        self.chat_analysis_selected_btn.clicked.connect(self.retrieve_chat_messages)
        chat_tab_sublayout2 = PyQt5.QtWidgets.QHBoxLayout()
        chat_tab_sublayout2.addStretch()
        chat_tab_sublayout2.addWidget(self.chat_analysis_all_btn)
        chat_tab_sublayout2.addStretch()
        chat_tab_sublayout2.addWidget(self.chat_analysis_selected_btn)
        chat_tab_sublayout2.addStretch()
        self.chat_tab_layout.addLayout(chat_tab_sublayout2, 2, 0)
        label = PyQt5.QtWidgets.QLabel("No multithreading currently. GUI may lock up when retrieving messages from GroupMe servers.")
        label.setWordWrap(True)
        label.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        chat_tab_sublayout3 = PyQt5.QtWidgets.QHBoxLayout()
        chat_tab_sublayout3.addWidget(label)
        self.chat_tab_layout.addLayout(chat_tab_sublayout3, 3, 0)

    def group_table_widget_update_selection(self):
        selected_groups = self.group_table_widget.selectedItems()
        self.selected_group_ids = []
        for group in selected_groups:
            if group.text() in self.groups[1]:         # we only want the Group ID for retrieving messages
                self.selected_group_ids.append(group.text())
    
    def chat_table_widget_update_selection(self):
        selected_chats = self.chat_table_widget.selectedItems()
        self.selected_chat_ids = []
        for chat in selected_chats:
            if chat.text() in self.chats[1]:
                self.selected_chat_ids.append(chat.text())
    
    def retrieve_group_messages(self):
        if self.group_analysis_all_btn == self.sender():
            self.group_analysis_results = GroupMeStats.retrieve_group_messages(self.groups[1], self.groups[2])
            self.display_statistics()
        elif self.group_analysis_selected_btn == self.sender():
            try:
                if len(self.selected_group_ids) > 0:
                    self.group_analysis_results = GroupMeStats.retrieve_group_messages(self.selected_group_ids, self.groups[2])
                    print(self.selected_group_ids)
                    self.display_statistics()
                else:
                    error_dialog = PyQt5.QtWidgets.QMessageBox()
                    error_dialog.setIcon(PyQt5.QtWidgets.QMessageBox.Critical)
                    error_dialog.setText("Error")
                    error_dialog.setInformativeText("Some error occurred. Expecting at least one group selected.")
                    error_dialog.setWindowTitle("Error")
                    error_dialog.exec_()
            except AttributeError:
                warning_dialog = PyQt5.QtWidgets.QMessageBox()
                warning_dialog.setIcon(PyQt5.QtWidgets.QMessageBox.Warning)
                warning_dialog.setText("Warning")
                warning_dialog.setInformativeText("You should select at least one group to use this function.")
                warning_dialog.setWindowTitle("Warning")
                warning_dialog.exec_()
    
    def retrieve_chat_messages(self):
        if self.chat_analysis_all_btn == self.sender():
            self.chat_analysis_results = GroupMeStats.retrieve_chat_messages(self.chats[1], self.chats[2])
            self.display_statistics()
        elif self.chat_analysis_selected_btn == self.sender():
            try:
                if len(self.selected_chat_ids) > 0:
                    self.chat_analysis_results = GroupMeStats.retrieve_chat_messages(self.selected_chat_ids, self.chats[2])
                    print(self.selected_chat_ids)
                    self.display_statistics()
                else:
                    error_dialog = PyQt5.QtWidgets.QMessageBox()
                    error_dialog.setIcon(PyQt5.QtWidgets.QMessageBox.Critical)
                    error_dialog.setText("Error")
                    error_dialog.setInformativeText("Some error occurred. Expecting at least one chat selected.")
                    error_dialog.setWindowTitle("Error")
                    error_dialog.exec_()
            except AttributeError:
                warning_dialog = PyQt5.QtWidgets.QMessageBox()
                warning_dialog.setIcon(PyQt5.QtWidgets.QMessageBox.Warning)
                warning_dialog.setText("Warning")
                warning_dialog.setInformativeText("You should select at least one chat to use this function.")
                warning_dialog.setWindowTitle("Warning")
                warning_dialog.exec_()
    
    def display_statistics(self):
        self.tab_widget.addTab(self.stats_tab, "Stats")
        self.tab_widget.setCurrentIndex(3)
        hour = [1,2,3,4,5,6,7,8,9,10]
        temperature = [30,32,34,32,33,31,29,32,35,45]
        test = pyqtgraph.PlotWidget()
        test.plot(hour, temperature)
        self.stats_tab_layout.addRow(test)

if __name__ == '__main__':
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())