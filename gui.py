from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QPushButton
import sys
import GroupMeStats

class GUI(QMainWindow):
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

class TabWidget(QWidget):
    def __init__(self, parent):
        super(TabWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setup()

    def setup(self):
        self.tab_widget = QTabWidget()
        self.group_tab = QWidget()
        self.chat_tab = QWidget()
        self.settings_tab = QWidget()

        self.setup_group_tab()
        self.setup_chat_tab()
        self.setup_settings_tab()

        self.tab_widget.addTab(self.group_tab, "Groups")
        self.tab_widget.addTab(self.chat_tab, "Chats")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)

    def setup_group_tab(self):
        self.load_groups_btn = QPushButton('Load Groups', self)
        self.group_tab_layout = QVBoxLayout(self.group_tab)
        self.group_tab_sublayout = QHBoxLayout(self.group_tab)
        self.group_tab_sublayout.addStretch()
        self.group_tab_sublayout.addWidget(self.load_groups_btn)
        self.group_tab_sublayout.addStretch()
        self.group_tab_layout.addLayout(self.group_tab_sublayout)
        self.group_tab_layout.addStretch()
        self.group_tab.setLayout(self.group_tab_layout)

    def setup_chat_tab(self):
        self.load_chats_btn = QPushButton('Load Chats', self)
        self.chat_tab_layout = QVBoxLayout(self.chat_tab)
        self.chat_tab_sublayout = QHBoxLayout(self.chat_tab)
        self.chat_tab_sublayout.addStretch()
        self.chat_tab_sublayout.addWidget(self.load_chats_btn)
        self.chat_tab_sublayout.addStretch()
        self.chat_tab_layout.addLayout(self.chat_tab_sublayout)
        self.chat_tab_layout.addStretch()
        self.chat_tab.setLayout(self.chat_tab_layout)
    
    def setup_settings_tab(self):
        print("hi")

class ListWidget(QWidget):
    def __init__(self, parent):
        super(ListWidget, self).__init__(parent)
        self.item = ""
    def selected(self, item):
        self.item = item
    def get_selected_item(self):
        return self.item


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())