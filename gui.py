from nntplib import GroupInfo
from tkinter import Scrollbar
from turtle import width
from PyQt5 import QtCore, QtWidgets, QtGui
import sys
from matplotlib import cm
import GroupMeStats
import numpy
import pandas
from pyqtgraph import PlotWidget, plot, AxisItem
import pyqtgraph

class GUI(QtWidgets.QMainWindow):
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
    def __init__(self, title="", xLabel="", yLabel="", parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)
        self.stringaxis = pyqtgraph.AxisItem(orientation="bottom")
        cmap = cm.get_cmap('tab10')
        self.colors = [tuple(255*x for x in cmap(i/10))[:-1] for i in range(10)]
        QtWidgets.QWidget.setMinimumSize(self, 300, 300)
        self.setBackground('w')
        if title:
            self.title = title
        if xLabel:
            self.xLabel = xLabel
        if yLabel:
            self.yLabel = yLabel
    
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
        bargraph = pyqtgraph.BarGraphItem(x = list(self.x_axis_dict.keys()), height = self.y_axis, width = 1.0)
        self.addItem(bargraph)
        if self.title:
            self.setTitle(self.title)
    
    def plot_graph_multiple_y_axes(self, df: pandas.DataFrame):
        x_axis_dictionary = dict(enumerate(df.index.values.tolist()))
        self.stringaxis.setTicks([x_axis_dictionary.items()])
        self.setAxisItems(axisItems = {'bottom': self.stringaxis})
        bottom = numpy.zeros(len(df))
        for col, color in zip(df.columns, self.colors):
            bargraph = pyqtgraph.BarGraphItem(x = list(x_axis_dictionary.keys()), height = df[col].values.tolist(), y0 = bottom, width = 1.0, brush = pyqtgraph.mkBrush(color = color), pen = pyqtgraph.mkPen(color = color))
            self.addItem(bargraph)
            bottom += df[col].values.tolist()
        if self.title:
            self.setTitle(self.title)


class TabWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(TabWidget, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.users = set()
        self.setup()

    def setup(self):
        self.tab_widget = QtWidgets.QTabWidget()
        self.group_tab = QtWidgets.QWidget()
        self.chat_tab = QtWidgets.QWidget()
        self.plots_tab = QtWidgets.QScrollArea()
        self.settings_tab = QtWidgets.QWidget()

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
        self.load_groups_btn = QtWidgets.QPushButton('Load Groups', self)
        self.load_groups_btn.clicked.connect(self.setup_group_table_widget)
        self.group_tab_layout = QtWidgets.QGridLayout(self.group_tab)
        self.group_tab_sublayout = QtWidgets.QHBoxLayout()
        self.group_tab_sublayout.addStretch()
        self.group_tab_sublayout.addWidget(self.load_groups_btn)
        self.group_tab_sublayout.addStretch()
        self.group_tab_layout.addLayout(self.group_tab_sublayout, 0, 0)
        self.group_tab.setLayout(self.group_tab_layout)

    def setup_chat_tab(self):
        self.load_chats_btn = QtWidgets.QPushButton('Load Chats', self)
        self.chat_tab_layout = QtWidgets.QGridLayout(self.chat_tab)
        self.load_chats_btn.clicked.connect(self.setup_chat_table_widget)
        self.chat_tab_sublayout = QtWidgets.QHBoxLayout()
        self.chat_tab_sublayout.addStretch()
        self.chat_tab_sublayout.addWidget(self.load_chats_btn)
        self.chat_tab_sublayout.addStretch()
        self.chat_tab_layout.addLayout(self.chat_tab_sublayout, 0, 0)
        self.chat_tab.setLayout(self.chat_tab_layout)
    
    def setup_plots_tab(self):
        print("This is the plots tab")
        self.generate_plots_layout()

    def generate_plots_layout(self):
        self.plots_tab_layout_primary = QtWidgets.QHBoxLayout(self.plots_tab)
        self.scroll_area = QtWidgets.QScrollArea(self.plots_tab)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_widget_contents = QtWidgets.QWidget()
        self.plots_tab_layout = QtWidgets.QGridLayout(self.scroll_area_widget_contents)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        self.plots_tab_layout_primary.addWidget(self.scroll_area)
        # messages sent
        self.messages_sent_graph = GraphManager(parent=self.plots_tab, title="Messages Sent Per User", xLabel="User", yLabel="Message Count")
        self.plots_tab_layout.addWidget(self.messages_sent_graph, 0, 0)
        # likes received
        self.likes_received_graph = GraphManager(parent=self.plots_tab, title="Likes Received Per User", xLabel="User", yLabel="Likes Received Count")
        self.plots_tab_layout.addWidget(self.likes_received_graph, 1, 0)
        # likes given
        self.likes_given_graph = GraphManager(parent=self.plots_tab, title="Likes Given Per User", xLabel="User", yLabel="Likes Given Count")
        self.plots_tab_layout.addWidget(self.likes_given_graph, 2, 0)
        # self likes
        self.self_likes_graph = GraphManager(parent=self.plots_tab, title="Self Likes Per User", xLabel="User", yLabel="Self Likes Count")
        self.plots_tab_layout.addWidget(self.self_likes_graph, 3, 0)
        # words sent
        self.words_sent_graph = GraphManager(parent=self.plots_tab, title="Words Sent Per User", xLabel="User", yLabel="Words Sent Count")
        self.plots_tab_layout.addWidget(self.words_sent_graph, 4, 0)
        # images sent
        self.images_sent_graph = GraphManager(parent=self.plots_tab, title="Images Sent Per User", xLabel="User", yLabel="Images Sent Count")
        self.plots_tab_layout.addWidget(self.images_sent_graph, 5, 0)
        # common words
        self.common_words_graph = GraphManager(parent=self.plots_tab, title="Commonly Sent Words", xLabel="Word", yLabel="Times Sent")
        self.plots_tab_layout.addWidget(self.common_words_graph, 6, 0)
        self.plots_tab.setWidgetResizable(False)
        # self.plots_tab.setLayout(self.plots_tab_layout)
        self.plots_tab.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    
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
        self.group_table_widget = QtWidgets.QTableWidget(len(self.groups[1]), 3, self)
        self.group_table_widget.setHorizontalHeaderLabels(['Group', '  Message Count  ', '  Group ID  '])
        i = 0
        for group in self.groups[1]:
            self.group_table_widget.setItem(i, 0, QtWidgets.QTableWidgetItem(self.groups[2][group][0]))
            self.group_table_widget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(self.groups[2][group][1])))
            self.group_table_widget.setItem(i, 2, QtWidgets.QTableWidgetItem(str(group)))
            i += 1
        self.group_table_widget.itemSelectionChanged.connect(self.group_table_widget_update_selection)
        self.group_table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.group_table_widget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        header = self.group_table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.group_tab_layout.addWidget(self.group_table_widget, 1, 0)
        self.group_analysis_all_btn = QtWidgets.QPushButton('Analyze All', self)
        self.group_analysis_selected_btn = QtWidgets.QPushButton('Analyze Selected', self)
        self.group_analysis_all_btn.clicked.connect(self.retrieve_group_messages)
        self.group_analysis_selected_btn.clicked.connect(self.retrieve_group_messages)
        group_tab_sublayout_2 = QtWidgets.QHBoxLayout()
        group_tab_sublayout_2.addStretch()
        group_tab_sublayout_2.addWidget(self.group_analysis_all_btn)
        group_tab_sublayout_2.addStretch()
        group_tab_sublayout_2.addWidget(self.group_analysis_selected_btn)
        group_tab_sublayout_2.addStretch()
        self.group_tab_layout.addLayout(group_tab_sublayout_2, 2, 0)
    
    def setup_chat_table_widget(self):
        self.chats = self.get_chats()
        self.chat_table_widget = QtWidgets.QTableWidget(len(self.chats[1]), 3, self)
        self.chat_table_widget.setHorizontalHeaderLabels(['Chat', '  Message Count  ', '  Chat ID  '])
        i = 0
        for chat in self.chats[1]:
            self.chat_table_widget.setItem(i, 0, QtWidgets.QTableWidgetItem(self.chats[2][chat][0]))
            self.chat_table_widget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(self.chats[2][chat][1])))
            self.chat_table_widget.setItem(i, 2, QtWidgets.QTableWidgetItem(str(chat)))
            i += 1
        self.chat_table_widget.itemSelectionChanged.connect(self.chat_table_widget_update_selection)
        self.chat_table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.chat_table_widget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        header = self.chat_table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.chat_tab_layout.addWidget(self.chat_table_widget, 1, 0)
        self.chat_analysis_all_btn = QtWidgets.QPushButton('Analyze All', self)
        self.chat_analysis_selected_btn = QtWidgets.QPushButton('Analyze Selected', self)
        self.chat_analysis_all_btn.clicked.connect(self.retrieve_chat_messages)
        self.chat_analysis_selected_btn.clicked.connect(self.retrieve_chat_messages)
        chat_tab_sublayout2 = QtWidgets.QHBoxLayout()
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
                    error_dialog = QtWidgets.QMessageBox()
                    error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
                    error_dialog.setText("Error")
                    error_dialog.setInformativeText("Some error occurred. Expecting at least one group selected.")
                    error_dialog.setWindowTitle("Error")
                    error_dialog.exec_()
            except AttributeError:
                warning_dialog = QtWidgets.QMessageBox()
                warning_dialog.setIcon(QtWidgets.QMessageBox.Warning)
                warning_dialog.setText("Warning")
                warning_dialog.setInformativeText("You should select at least one group to use this function.")
                warning_dialog.setWindowTitle("Warning")
                warning_dialog.exec_()
        else:       # should never hit
            return
    
        total_stats = {}
        users_subset = set()
        users_list = []
        for group_id in self.selected_group_ids:
            for group in self.groups[0]:
                if group["group_id"] == group_id:
                    for member in group["members"]:
                        users_list.append(member["user_id"])
        
        current_user_id = GroupMeStats.get_me()["response"]["id"]
        if current_user_id not in users_list:
            users_list.append(current_user_id)

        users_subset.update(users_list)
        group_stats = GroupMeStats.determine_user_statistics(self.received_group_msgs, self.selected_group_ids, 'group', users_subset)
        total_stats.update(group_stats[0])
        num_messages = group_stats[1]
        GroupMeStats.write_to_csv(total_stats, num_messages)
        self.plot_stats(total_stats)
    
    def retrieve_chat_messages(self):
        if self.chat_analysis_all_btn == self.sender():
            self.selected_chat_ids = self.chats[1]
            self.received_chat_msgs = GroupMeStats.retrieve_chat_messages(self.chats[1], self.chats[2], from_gui = True)
        elif self.chat_analysis_selected_btn == self.sender():
            try:
                if len(self.selected_chat_ids) > 0:
                    # message_dialog = QtWidgets.QMessageBox()
                    # message_dialog.setText("Please Wait")
                    # message_dialog.setInformativeText("Retrieving messages")
                    # message_dialog.show()
                    self.received_chat_msgs = GroupMeStats.retrieve_chat_messages(self.selected_chat_ids, self.chats[2], from_gui = True)
                    print(self.selected_chat_ids)
                else:
                    error_dialog = QtWidgets.QMessageBox()
                    error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
                    error_dialog.setText("Error")
                    error_dialog.setInformativeText("Some error occurred. Expecting at least one chat selected.")
                    error_dialog.setWindowTitle("Error")
                    error_dialog.exec_()
            except AttributeError:
                warning_dialog = QtWidgets.QMessageBox()
                warning_dialog.setIcon(QtWidgets.QMessageBox.Warning)
                warning_dialog.setText("Warning")
                warning_dialog.setInformativeText("You should select at least one chat to use this function.")
                warning_dialog.setWindowTitle("Warning")
                warning_dialog.exec_()
        else:       # should never hit
            return

        total_stats = {}
        users_subset = set()
        users_list = []
        current_user_id = GroupMeStats.get_me()["response"]["id"]
        users_list.append(current_user_id)
        for chat_id in self.selected_chat_ids:
            users_list.append(chat_id)
        users_subset.update(users_list)
        chat_stats = GroupMeStats.determine_user_statistics(self.received_chat_msgs, self.selected_chat_ids, 'direct', users_subset)
        total_stats.update(chat_stats[0])
        num_messages = chat_stats[1]
        GroupMeStats.write_to_csv(total_stats, num_messages)
        self.plot_stats(total_stats)
    
    def plot_stats(self, stats):
        common_words_dict = {}
        x_axis = []
        words_x_axis = []
        messages_sent_y_axis, likes_received_y_axis, likes_given_y_axis, self_likes_y_axis, words_sent_y_axis, images_sent_y_axis, common_words_y_axis = ([] for i in range(7))
        name_order = []
        for key, value in stats.items():
            name_val = ""
            if stats[key]["name"]:
                x_axis.append(value["name"])
                name_val = value["name"]
            else:
                x_axis.append(key)
                name_val = key
            name_order.append(name_val)
            messages_sent_y_axis.append(value["messages_sent"])
            likes_received_y_axis.append(value["likes_received"])
            likes_given_y_axis.append(value["likes_given"])
            self_likes_y_axis.append(value["self_likes"])
            words_sent_y_axis.append(value["words_sent"])
            images_sent_y_axis.append(value["images_sent"])
            common_words_dict.update(value["common_words"])
        
        common_words_dict_sorted = dict(sorted(common_words_dict.items(), key=lambda item: item[1], reverse=True))
        common_words_list = [(k,v) for k,v in common_words_dict_sorted.items()]

        common_words_x_axis = []
        for i in range(10):
            common_words_x_axis.append(common_words_list[i][0])
        #df = pandas.DataFrame(columns = common_words_x_axis[0:10])
        df = pandas.DataFrame(columns = name_order)
        common_words_data = {} #dict.fromkeys(stats.keys())
        for word in common_words_x_axis[0:10]:
            words_count = []
            for key, value in stats.items():
                if word in value["common_words"].keys():
                    words_count.append(value["common_words"][word])
                else:
                    words_count.append(0)
            df.loc[len(df.index)] = words_count
        df.index = common_words_x_axis[0:10]
        for name in name_order:
            df[name] = pandas.to_numeric(df[name])

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
        self.common_words_graph.plot_graph_multiple_y_axes(df)


class OutputWindow(QtWidgets.QPlainTextEdit):
    def write(self, text):
        self.appendPlainText("str(text)")
        self.update()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())