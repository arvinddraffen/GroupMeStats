import PyQt5.QtWidgets
import sys
import GroupMeStats
from pyqtgraph import PlotWidget, plot, AxisItem
import pyqtgraph

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

class GraphManager(pyqtgraph.PlotWidget):
    def __init__(self, parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)
        self.stringaxis = pyqtgraph.AxisItem(orientation="bottom")
        self.setBackground('w')
    
    def set_x_axis(self, values: list):
        self.x_axis = values
        self.x_axis_dict = dict(enumerate(self.x_axis))
    
    def set_y_axis(self, values: list):
        self.y_axis = values
    
    def set_axes(self, x_values: list, y_values: list):
        self.set_x_axis(x_values)
        self.set_y_axis(y_values)
    
    def plot_graph(self):
        self.stringaxis.setTicks([self.x_axis_dict.items()])
        self.setAxisItems(axisItems = {'bottom': self.stringaxis})
        # self.plot(list(self.x_axis_dict.keys()), self.y_axis)
        bargraph = pyqtgraph.BarGraphItem(x = list(self.x_axis_dict.keys()), height = self.y_axis, width = 1.0)
        self.addItem(bargraph)


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
        self.plots_tab = PyQt5.QtWidgets.QWidget()
        self.settings_tab = PyQt5.QtWidgets.QWidget()

        self.setup_group_tab()
        self.setup_chat_tab()
        self.setup_plots_tab()
        self.setup_settings_tab()

        self.tab_widget.addTab(self.group_tab, "Groups")
        self.tab_widget.addTab(self.chat_tab, "Chats")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        self.tab_widget.addTab(self.plots_tab, "Graphs")
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
    
    def setup_plots_tab(self):
        print("This is the plots tab")
        self.generate_plots_layout()

    def generate_plots_layout(self):
        self.plots_tab_layout = PyQt5.QtWidgets.QGridLayout(self.plots_tab)
        # messages sent
        self.messages_sent_graph = GraphManager(parent=self.plots_tab)
        self.plots_tab_layout.addWidget(self.messages_sent_graph, 0, 0)
        # likes received
        self.likes_received_graph = GraphManager(parent=self.plots_tab)
        self.plots_tab_layout.addWidget(self.likes_received_graph, 0, 1)
        # likes given
        self.likes_given_graph = GraphManager(parent=self.plots_tab)
        self.plots_tab_layout.addWidget(self.likes_given_graph, 0, 2)
        # self likes
        self.self_likes_graph = GraphManager(parent=self.plots_tab)
        self.plots_tab_layout.addWidget(self.self_likes_graph, 1, 0)
        # words sent
        self.words_sent_graph = GraphManager(parent=self.plots_tab)
        self.plots_tab_layout.addWidget(self.words_sent_graph, 1, 1)
        # images sent
        self.images_sent_graph = GraphManager(parent=self.plots_tab)
        self.plots_tab_layout.addWidget(self.images_sent_graph, 1, 2)
        self.plots_tab.setLayout(self.plots_tab_layout)
    
    def setup_settings_tab(self):
        print("This is the settings tab")
    
    def get_groups(self):
        if not GroupMeStats.set_token(None, from_gui=True):
            sys.exit()
        return GroupMeStats.get_groups(self.users, suppress_print=True)

    def get_chats(self):
        if not GroupMeStats.set_token(None, from_gui=True):
            sys.exit()
        return GroupMeStats.get_chats(self.users, suppress_print=True)
    
    def setup_group_table_widget(self):
        self.groups = self.get_groups()
        self.group_table_widget = PyQt5.QtWidgets.QTableWidget(len(self.groups[1]), 3, self)
        self.group_table_widget.setHorizontalHeaderLabels(['Group', '  Message Count  ', '  Group ID  '])
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
    
    def setup_chat_table_widget(self):
        self.chats = self.get_chats()
        self.chat_table_widget = PyQt5.QtWidgets.QTableWidget(len(self.chats[1]), 3, self)
        self.chat_table_widget.setHorizontalHeaderLabels(['Chat', '  Message Count  ', '  Chat ID  '])
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
            self.received_group_msgs = GroupMeStats.retrieve_group_messages(self.groups[1], self.groups[2])
        elif self.group_analysis_selected_btn == self.sender():
            try:
                if len(self.selected_group_ids) > 0:
                    self.received_group_msgs = GroupMeStats.retrieve_group_messages(self.selected_group_ids, self.groups[2])
                    print(self.selected_group_ids)
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
        else:       # should never hit
            return
    
        total_stats = {}
        group_stats = GroupMeStats.determine_user_statistics(self.received_group_msgs, self.selected_group_ids, 'group', self.users)
        total_stats.update(group_stats[0])
        num_messages = group_stats[1]
        GroupMeStats.write_to_csv(total_stats, num_messages)
    
    def retrieve_chat_messages(self):
        if self.chat_analysis_all_btn == self.sender():
            self.selected_chat_ids = self.chats[1]
            self.received_chat_msgs = GroupMeStats.retrieve_chat_messages(self.chats[1], self.chats[2], from_gui = True)
        elif self.chat_analysis_selected_btn == self.sender():
            try:
                if len(self.selected_chat_ids) > 0:
                    # message_dialog = PyQt5.QtWidgets.QMessageBox()
                    # message_dialog.setText("Please Wait")
                    # message_dialog.setInformativeText("Retrieving messages")
                    # message_dialog.show()
                    self.received_chat_msgs = GroupMeStats.retrieve_chat_messages(self.selected_chat_ids, self.chats[2], from_gui = True)
                    print(self.selected_chat_ids)
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
        else:       # should never hit
            return

        total_stats = {}
        chat_stats = GroupMeStats.determine_user_statistics(self.received_chat_msgs, self.selected_chat_ids, 'direct', self.users)
        total_stats.update(chat_stats[0])
        num_messages = chat_stats[1]
        GroupMeStats.write_to_csv(total_stats, num_messages)
        self.plot_chat_messages(total_stats)
    
    def plot_chat_messages(self, stats):
        x_axis = []
        messages_sent_y_axis, likes_received_y_axis, likes_given_y_axis, self_likes_y_axis, words_sent_y_axis, images_sent_y_axis = ([] for i in range(6))
        for key, value in stats.items():
            if stats[key]["name"]:
                x_axis.append(value["name"])
            else:
                x_axis.append(key)
            messages_sent_y_axis.append(value["messages_sent"])
            likes_received_y_axis.append(value["likes_received"])
            likes_given_y_axis.append(value["likes_given"])
            self_likes_y_axis.append(value["self_likes"])
            words_sent_y_axis.append(value["words_sent"])
            images_sent_y_axis.append(value["images_sent"])
        
        self.messages_sent_graph.set_axes(x_axis, messages_sent_y_axis)
        self.likes_received_graph.set_axes(x_axis, likes_received_y_axis)
        self.likes_given_graph.set_axes(x_axis, likes_given_y_axis)
        self.self_likes_graph.set_axes(x_axis, self_likes_y_axis)
        self.words_sent_graph.set_axes(x_axis, words_sent_y_axis)
        self.images_sent_graph.set_axes(x_axis, images_sent_y_axis)
        self.messages_sent_graph.plot_graph()
        self.likes_received_graph.plot_graph()
        self.likes_given_graph.plot_graph()
        self.self_likes_graph.plot_graph()
        self.words_sent_graph.plot_graph()
        self.images_sent_graph.plot_graph()


class OutputWindow(PyQt5.QtWidgets.QPlainTextEdit):
    def write(self, text):
        self.appendPlainText("str(text)")
        self.update()

if __name__ == '__main__':
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())