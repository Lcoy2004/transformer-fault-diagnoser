# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QMainWindow, QMenu,
    QMenuBar, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 800)
        MainWindow.setMinimumSize(QSize(1000, 700))
        icon = QIcon()
        icon.addFile(u":/icon.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet(u"\n"
"/* ================================================\n"
"   \u73b0\u4ee3\u5316\u5de5\u4e1a\u8f6f\u4ef6\u754c\u9762\u6837\u5f0f\u8868\n"
"   \u8bbe\u8ba1\u7406\u5ff5\uff1a\u7b80\u6d01\u3001\u4e13\u4e1a\u3001\u9ad8\u6548\u3001\u6241\u5e73\u5316\n"
"   \u4e3b\u8272\u8c03\uff1a\u6df1\u84dd\u7070 (#1E293B)\n"
"   \u5f3a\u8c03\u8272\uff1a\u79d1\u6280\u84dd (#3B82F6)\n"
"   \u8f85\u52a9\u8272\uff1a\u4e2d\u7070 (#64748B)\u3001\u6d45\u7070 (#F1F5F9)\n"
"   ================================================ */\n"
"\n"
"/* ========== \u5168\u5c40\u80cc\u666f ========== */\n"
"QMainWindow {\n"
"    background-color: #F8FAFC;\n"
"}\n"
"\n"
"QWidget {\n"
"    font-family: \"Microsoft YaHei\", \"Segoe UI\", Arial, sans-serif;\n"
"    font-size: 13px;\n"
"    color: #1E293B;\n"
"}\n"
"\n"
"/* ========== \u83dc\u5355\u680f ========== */\n"
"QMenuBar {\n"
"    background-color: #FFFFFF;\n"
"    border-bottom: 1px solid #E2E8F0;\n"
"    padding: 6px 12px;\n"
"}\n"
"\n"
"QMenuBar::item {\n"
"    background-color: transparent;\n"
""
                        "    padding: 8px 16px;\n"
"    border-radius: 6px;\n"
"    color: #334155;\n"
"}\n"
"\n"
"QMenuBar::item:selected {\n"
"    background-color: #EFF6FF;\n"
"    color: #3B82F6;\n"
"}\n"
"\n"
"QMenuBar::item:pressed {\n"
"    background-color: #DBEAFE;\n"
"}\n"
"\n"
"QMenu {\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 8px;\n"
"    padding: 8px 0px;\n"
"}\n"
"\n"
"QMenu::item {\n"
"    padding: 10px 32px 10px 16px;\n"
"    border-radius: 4px;\n"
"    color: #334155;\n"
"}\n"
"\n"
"QMenu::item:selected {\n"
"    background-color: #EFF6FF;\n"
"    color: #3B82F6;\n"
"}\n"
"\n"
"QMenu::separator {\n"
"    height: 1px;\n"
"    background-color: #F1F5F9;\n"
"    margin: 6px 16px;\n"
"}\n"
"\n"
"/* ========== \u72b6\u6001\u680f ========== */\n"
"QStatusBar {\n"
"    background-color: #F1F5F9;\n"
"    color: #64748B;\n"
"    border-top: 1px solid #E2E8F0;\n"
"    padding: 8px 16px;\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"/* ========== \u6309\u94ae\u57fa\u7840\u6837\u5f0f ="
                        "========= */\n"
"QPushButton {\n"
"    background-color: #3B82F6;\n"
"    color: #FFFFFF;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    padding: 10px 20px;\n"
"    min-width: 80px;\n"
"    font-weight: 500;\n"
"    font-size: 13px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2563EB;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #1D4ED8;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"    background-color: #CBD5E1;\n"
"    color: #94A3B8;\n"
"}\n"
"\n"
"/* ========== \u529f\u80fd\u6309\u94ae\u533a\u5206 ========== */\n"
"\n"
"/* \u5237\u65b0\u6570\u636e\u8868\u6309\u94ae - \u6df1\u7070 */\n"
"QPushButton#pushButton {\n"
"    background-color: #475569;\n"
"}\n"
"QPushButton#pushButton:hover {\n"
"    background-color: #334155;\n"
"}\n"
"\n"
"/* PCA/\u6570\u636e\u964d\u7ef4\u6309\u94ae - \u84dd\u7070 */\n"
"QPushButton#btn_pca {\n"
"    background-color: #64748B;\n"
"}\n"
"QPushButton#btn_pca:hover {\n"
"    background-color: #475569;\n"
"}\n"
"\n"
"/* RF/\u8bad\u7ec3\u6a21"
                        "\u578b\u6309\u94ae - \u7eff\u8272 */\n"
"QPushButton#btn_rf {\n"
"    background-color: #10B981;\n"
"}\n"
"QPushButton#btn_rf:hover {\n"
"    background-color: #059669;\n"
"}\n"
"\n"
"/* \u9884\u6d4b\u6309\u94ae - \u6a59\u8272\uff08\u9192\u76ee CTA\uff09 */\n"
"QPushButton#btn_pd {\n"
"    background-color: #F97316;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"    padding: 12px 28px;\n"
"    border-radius: 10px;\n"
"}\n"
"QPushButton#btn_pd:hover {\n"
"    background-color: #EA580C;\n"
"}\n"
"QPushButton#btn_pd:pressed {\n"
"    background-color: #C2410C;\n"
"}\n"
"\n"
"/* \u65e5\u5fd7\u6309\u94ae - \u6b21\u8981\u6837\u5f0f */\n"
"QPushButton#showlog_btn {\n"
"    background-color: transparent;\n"
"    color: #64748B;\n"
"    border: 1px solid #CBD5E1;\n"
"    padding: 8px 16px;\n"
"}\n"
"QPushButton#showlog_btn:hover {\n"
"    background-color: #F1F5F9;\n"
"    border-color: #94A3B8;\n"
"    color: #334155;\n"
"}\n"
"\n"
"/* ========== \u4e0b\u62c9\u6846 ========== */\n"
"QComboBox {\n"
"    border"
                        ": 1px solid #CBD5E1;\n"
"    border-radius: 8px;\n"
"    padding: 9px 14px;\n"
"    background-color: #FFFFFF;\n"
"    min-height: 22px;\n"
"    color: #334155;\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    border-color: #94A3B8;\n"
"}\n"
"\n"
"QComboBox:focus {\n"
"    border-color: #3B82F6;\n"
"    outline: none;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: center right;\n"
"    width: 32px;\n"
"    border-left: 1px solid #E2E8F0;\n"
"    border-top-right-radius: 8px;\n"
"    border-bottom-right-radius: 8px;\n"
"    background-color: #F8FAFC;\n"
"}\n"
"\n"
"QComboBox::drop-down:hover {\n"
"    background-color: #F1F5F9;\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    image: none;\n"
"    border-left: 5px solid transparent;\n"
"    border-right: 5px solid transparent;\n"
"    border-top: 6px solid #64748B;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    border: 1px solid #CBD5E1;\n"
"    border-radius: 8px;\n"
"    background-color: #FFFFFF;\n"
"    sel"
                        "ection-background-color: #EFF6FF;\n"
"    outline: none;\n"
"    padding: 6px 0px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item {\n"
"    padding: 10px 16px;\n"
"    min-height: 22px;\n"
"    color: #334155;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item:hover {\n"
"    background-color: #EFF6FF;\n"
"    color: #1D4ED8;\n"
"}\n"
"\n"
"/* ========== \u8868\u683c ========== */\n"
"QTableWidget {\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 10px;\n"
"    background-color: #FFFFFF;\n"
"    gridline-color: #F1F5F9;\n"
"    selection-background-color: #EFF6FF;\n"
"}\n"
"\n"
"QTableWidget::item {\n"
"    padding: 10px 8px;\n"
"    border-bottom: 1px solid #F8FAFC;\n"
"    color: #334155;\n"
"}\n"
"\n"
"QTableWidget::item:selected {\n"
"    background-color: #EFF6FF;\n"
"    color: #1D4ED8;\n"
"}\n"
"\n"
"QTableWidget::item:hover {\n"
"    background-color: #F8FAFC;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    background-color: #F8FAFC;\n"
"    padding: 12px 10px;\n"
"    border: none;\n"
"    bord"
                        "er-bottom: 2px solid #E2E8F0;\n"
"    border-right: 1px solid #F1F5F9;\n"
"    font-weight: 600;\n"
"    color: #475569;\n"
"}\n"
"\n"
"QHeaderView::section:hover {\n"
"    background-color: #F1F5F9;\n"
"}\n"
"\n"
"QTableWidget QTableCornerButton::section {\n"
"    background-color: #F8FAFC;\n"
"    border: none;\n"
"    border-bottom: 2px solid #E2E8F0;\n"
"    border-right: 1px solid #F1F5F9;\n"
"}\n"
"\n"
"/* ========== \u8f93\u5165\u8868\u683c ========== */\n"
"#showinput_tableWidget {\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 10px;\n"
"    gridline-color: #F1F5F9;\n"
"    selection-background-color: #EFF6FF;\n"
"}\n"
"\n"
"#showinput_tableWidget::item {\n"
"    padding: 8px;\n"
"    border-bottom: 1px solid #F1F5F9;\n"
"    color: #1E293B;\n"
"    background-color: #FFFFFF;\n"
"}\n"
"\n"
"#showinput_tableWidget::item:hover {\n"
"    background-color: #F8FAFC;\n"
"}\n"
"\n"
"#showinput_tableWidget::item:selected {\n"
"    background-color: #EFF6FF;\n"
"   "
                        " color: #1D4ED8;\n"
"}\n"
"\n"
"#showinput_tableWidget QHeaderView::section {\n"
"    background-color: #F8FAFC;\n"
"    padding: 10px 8px;\n"
"    border: none;\n"
"    border-bottom: 2px solid #E2E8F0;\n"
"    border-right: 1px solid #F1F5F9;\n"
"    font-weight: 600;\n"
"    color: #475569;\n"
"}\n"
"\n"
"/* ========== \u6587\u672c\u7f16\u8f91\u6846 ========== */\n"
"QTextEdit {\n"
"    border: 1px solid #CBD5E1;\n"
"    border-radius: 10px;\n"
"    padding: 14px;\n"
"    background-color: #FFFFFF;\n"
"    color: #334155;\n"
"    selection-background-color: #DBEAFE;\n"
"}\n"
"\n"
"QTextEdit:hover {\n"
"    border-color: #94A3B8;\n"
"}\n"
"\n"
"QTextEdit:focus {\n"
"    border-color: #3B82F6;\n"
"    outline: none;\n"
"}\n"
"\n"
"/* ========== \u6807\u7b7e ========== */\n"
"QLabel {\n"
"    color: #334155;\n"
"    background-color: transparent;\n"
"    padding: 2px 4px;\n"
"}\n"
"\n"
"/* \u529f\u80fd\u6027\u6807\u7b7e */\n"
"QLabel#showtext_label,\n"
"QLabel#showtext_label_2,\n"
"QLabel#label {\n"
"    font-"
                        "weight: 600;\n"
"    color: #475569;\n"
"}\n"
"\n"
"/* \u901a\u77e5\u6807\u7b7e */\n"
"QLabel#notification_label {\n"
"    font-weight: 700;\n"
"    color: #3B82F6;\n"
"}\n"
"\n"
"/* \u65f6\u95f4\u6807\u7b7e */\n"
"QLabel#showtime_label {\n"
"    font-weight: 700;\n"
"    color: #F97316;\n"
"}\n"
"\n"
"/* ========== \u8fdb\u5ea6\u6761 ========== */\n"
"QProgressBar {\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    background-color: #E2E8F0;\n"
"    text-align: center;\n"
"    color: #1E293B;\n"
"    font-weight: 700;\n"
"    min-height: 10px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #3B82F6;\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"/* ========== \u4e2d\u5fc3\u90e8\u4ef6 ========== */\n"
"QWidget#centralwidget {\n"
"    background-color: transparent;\n"
"}\n"
"\n"
"/* ========== \u6eda\u52a8\u6761 ========== */\n"
"QScrollBar:vertical {\n"
"    background-color: #F8FAFC;\n"
"    width: 10px;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    backgr"
                        "ound-color: #CBD5E1;\n"
"    border-radius: 5px;\n"
"    min-height: 30px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical:hover {\n"
"    background-color: #94A3B8;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical,\n"
"QScrollBar::sub-line:vertical {\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar:horizontal {\n"
"    background-color: #F8FAFC;\n"
"    height: 10px;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"    background-color: #CBD5E1;\n"
"    border-radius: 5px;\n"
"    min-width: 30px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal:hover {\n"
"    background-color: #94A3B8;\n"
"}\n"
"\n"
"QScrollBar::add-line:horizontal,\n"
"QScrollBar::sub-line:horizontal {\n"
"    width: 0px;\n"
"}\n"
"")
        self.action_6 = QAction(MainWindow)
        self.action_6.setObjectName(u"action_6")
        font = QFont()
        font.setFamilies([u"Microsoft YaHei"])
        font.setPointSize(10)
        self.action_6.setFont(font)
        self.action_7 = QAction(MainWindow)
        self.action_7.setObjectName(u"action_7")
        self.action_7.setFont(font)
        self.action_8 = QAction(MainWindow)
        self.action_8.setObjectName(u"action_8")
        self.action_8.setFont(font)
        self.action = QAction(MainWindow)
        self.action.setObjectName(u"action")
        self.action.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.showtext_label = QLabel(self.centralwidget)
        self.showtext_label.setObjectName(u"showtext_label")
        font1 = QFont()
        font1.setFamilies([u"Microsoft YaHei"])
        font1.setWeight(QFont.DemiBold)
        self.showtext_label.setFont(font1)

        self.gridLayout.addWidget(self.showtext_label, 2, 4, 1, 1)

        self.textEdit_output = QTextEdit(self.centralwidget)
        self.textEdit_output.setObjectName(u"textEdit_output")
        self.textEdit_output.setMinimumSize(QSize(0, 150))
        font2 = QFont()
        font2.setFamilies([u"Microsoft YaHei"])
        self.textEdit_output.setFont(font2)
        self.textEdit_output.setReadOnly(True)

        self.gridLayout.addWidget(self.textEdit_output, 6, 4, 1, 3)

        self.input_combobox = QComboBox(self.centralwidget)
        self.input_combobox.setObjectName(u"input_combobox")
        self.input_combobox.setFont(font2)

        self.gridLayout.addWidget(self.input_combobox, 3, 4, 1, 2)

        self.showlog_btn = QPushButton(self.centralwidget)
        self.showlog_btn.setObjectName(u"showlog_btn")
        font3 = QFont()
        font3.setFamilies([u"Microsoft YaHei"])
        font3.setWeight(QFont.Medium)
        self.showlog_btn.setFont(font3)

        self.gridLayout.addWidget(self.showlog_btn, 2, 5, 1, 1)

        self.btn_pca = QPushButton(self.centralwidget)
        self.btn_pca.setObjectName(u"btn_pca")
        self.btn_pca.setFont(font3)

        self.gridLayout.addWidget(self.btn_pca, 0, 4, 2, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setFont(font1)

        self.gridLayout.addWidget(self.label, 5, 4, 1, 1)

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setFont(font3)

        self.gridLayout.addWidget(self.pushButton, 0, 0, 1, 1)

        self.btn_pd = QPushButton(self.centralwidget)
        self.btn_pd.setObjectName(u"btn_pd")
        font4 = QFont()
        font4.setFamilies([u"Microsoft YaHei"])
        font4.setBold(True)
        self.btn_pd.setFont(font4)

        self.gridLayout.addWidget(self.btn_pd, 2, 6, 2, 1)

        self.table_selector = QComboBox(self.centralwidget)
        self.table_selector.addItem("")
        self.table_selector.setObjectName(u"table_selector")
        self.table_selector.setFont(font2)

        self.gridLayout.addWidget(self.table_selector, 0, 1, 1, 2)

        self.btn_rf = QPushButton(self.centralwidget)
        self.btn_rf.setObjectName(u"btn_rf")
        self.btn_rf.setFont(font3)

        self.gridLayout.addWidget(self.btn_rf, 0, 5, 2, 2)

        self.showinput_tableWidget = QTableWidget(self.centralwidget)
        self.showinput_tableWidget.setObjectName(u"showinput_tableWidget")
        self.showinput_tableWidget.setMinimumSize(QSize(0, 280))
        self.showinput_tableWidget.setMaximumSize(QSize(16777215, 280))
        self.showinput_tableWidget.setFont(font2)
        self.showinput_tableWidget.setAlternatingRowColors(False)

        self.gridLayout.addWidget(self.showinput_tableWidget, 4, 4, 1, 3)

        self.showdata_tableWidget = QTableWidget(self.centralwidget)
        self.showdata_tableWidget.setObjectName(u"showdata_tableWidget")
        self.showdata_tableWidget.setFont(font2)

        self.gridLayout.addWidget(self.showdata_tableWidget, 1, 0, 6, 3)


        self.verticalLayout.addLayout(self.gridLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.showtext_label_2 = QLabel(self.centralwidget)
        self.showtext_label_2.setObjectName(u"showtext_label_2")
        self.showtext_label_2.setMinimumSize(QSize(60, 0))
        self.showtext_label_2.setMaximumSize(QSize(80, 16777215))
        self.showtext_label_2.setFont(font1)

        self.horizontalLayout.addWidget(self.showtext_label_2)

        self.notification_label = QLabel(self.centralwidget)
        self.notification_label.setObjectName(u"notification_label")
        self.notification_label.setMinimumSize(QSize(180, 20))
        self.notification_label.setMaximumSize(QSize(16777215, 16777215))
        self.notification_label.setFont(font4)

        self.horizontalLayout.addWidget(self.notification_label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMinimumSize(QSize(120, 10))
        self.progressBar.setMaximumSize(QSize(120, 20))
        self.progressBar.setFont(font1)
        self.progressBar.setValue(24)

        self.horizontalLayout.addWidget(self.progressBar)

        self.showtime_label = QLabel(self.centralwidget)
        self.showtime_label.setObjectName(u"showtime_label")
        self.showtime_label.setMinimumSize(QSize(180, 0))
        self.showtime_label.setFont(font4)

        self.horizontalLayout.addWidget(self.showtime_label)


        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setFont(font2)
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1000, 47))
        self.menuBar.setFont(font2)
        self.menu = QMenu(self.menuBar)
        self.menu.setObjectName(u"menu")
        self.menu.setFont(font2)
        self.menu_2 = QMenu(self.menuBar)
        self.menu_2.setObjectName(u"menu_2")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menu.menuAction())
        self.menuBar.addAction(self.menu_2.menuAction())
        self.menu.addAction(self.action_6)
        self.menu.addSeparator()
        self.menu.addAction(self.action)
        self.menu_2.addAction(self.action_7)
        self.menu_2.addSeparator()
        self.menu_2.addAction(self.action_8)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u57fa\u4e8e\u591a\u6e90\u76d1\u6d4b\u6570\u636e\u7684\u7535\u529b\u53d8\u538b\u5668\u6545\u969c\u667a\u80fd\u8bca\u65ad", None))
        self.action_6.setText(QCoreApplication.translate("MainWindow", u"\u6570\u636e\u5bfc\u5165", None))
        self.action_7.setText(QCoreApplication.translate("MainWindow", u"\u64cd\u4f5c\u8bf4\u660e", None))
        self.action_8.setText(QCoreApplication.translate("MainWindow", u"\u5173\u4e8e", None))
        self.action.setText(QCoreApplication.translate("MainWindow", u"\u539f\u59cb\u56fe\u8868", None))
        self.showtext_label.setText(QCoreApplication.translate("MainWindow", u"\u9009\u62e9\u5bf9\u5e94\u8868\u8f93\u5165\u6570\u636e\uff1a", None))
        self.showlog_btn.setText(QCoreApplication.translate("MainWindow", u"\u67e5\u8be2\u65e5\u5fd7", None))
        self.btn_pca.setText(QCoreApplication.translate("MainWindow", u"\u6570\u636e\u964d\u7ef4", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u64cd\u4f5c\u7ed3\u679c\uff1a", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0\u8bad\u7ec3\u6570\u636e\u8868", None))
        self.btn_pd.setText(QCoreApplication.translate("MainWindow", u"\u667a\u80fd\u5224\u65ad", None))
        self.table_selector.setItemText(0, QCoreApplication.translate("MainWindow", u"\u67e5\u9605\u6570\u636e", None))

        self.btn_rf.setText(QCoreApplication.translate("MainWindow", u"\u8bad\u7ec3\u5224\u65ad\u6a21\u578b", None))
        self.showtext_label_2.setText(QCoreApplication.translate("MainWindow", u"\u5b9e\u65f6\u72b6\u6001:", None))
        self.notification_label.setText(QCoreApplication.translate("MainWindow", u"\u663e\u793a\u5b9e\u65f6\u72b6\u6001", None))
        self.showtime_label.setText(QCoreApplication.translate("MainWindow", u"\u5b9e\u65f6\u65f6\u95f4\u663e\u793a", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6", None))
        self.menu_2.setTitle(QCoreApplication.translate("MainWindow", u"\u5e2e\u52a9", None))
    # retranslateUi

