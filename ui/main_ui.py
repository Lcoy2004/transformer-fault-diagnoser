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
    QStatusBar, QTableWidget, QTableWidgetItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(825, 625)
        MainWindow.setMinimumSize(QSize(800, 600))
        MainWindow.setStyleSheet(u"/* ========== \u5168\u5c40\u80cc\u666f ========== */\n"
"QMainWindow, QDialog {\n"
"    background-color: #f5f7fa;   /* \u67d4\u548c\u7070\u84dd */\n"
"}\n"
"\n"
"/* ========== \u83dc\u5355\u680f ========== */\n"
"QMenuBar {\n"
"    background-color: #ffffff;\n"
"    border-bottom: 1px solid #e0e4e8;\n"
"    padding: 4px 8px;\n"
"}\n"
"QMenuBar::item {\n"
"    background-color: transparent;\n"
"    padding: 6px 12px;\n"
"    border-radius: 6px;\n"
"    color: #2c3e50;\n"
"}\n"
"QMenuBar::item:selected {\n"
"    background-color: #eaeef2;\n"
"    color: #1a73e8;\n"
"}\n"
"QMenuBar::item:pressed {\n"
"    background-color: #d0d7de;\n"
"}\n"
"\n"
"QMenu {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #d0d7de;\n"
"    border-radius: 8px;\n"
"    padding: 4px 0px;\n"
"}\n"
"QMenu::item {\n"
"    padding: 8px 24px;\n"
"    border-radius: 4px;\n"
"    color: #2c3e50;\n"
"}\n"
"QMenu::item:selected {\n"
"    background-color: #e1eaf0;\n"
"    color: #1a73e8;\n"
"}\n"
"QMenu::separator {\n"
"    height: "
                        "1px;\n"
"    background-color: #d0d7de;\n"
"    margin: 4px 8px;\n"
"}\n"
"\n"
"/* ========== \u72b6\u6001\u680f ========== */\n"
"QStatusBar {\n"
"    background-color: #eaeef2;\n"
"    color: #4a5a6e;\n"
"    border-top: 1px solid #d0d7de;\n"
"    padding: 4px 8px;\n"
"}\n"
"\n"
"/* ========== \u6309\u94ae ========== */\n"
"QPushButton {\n"
"    background-color: #3498db;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 8px 16px;\n"
"    min-width: 80px;\n"
"    font-weight: 500;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #2980b9;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #1c6ea4;\n"
"}\n"
"QPushButton:flat {\n"
"    background-color: transparent;\n"
"    color: #2c3e50;\n"
"}\n"
"QPushButton:flat:hover {\n"
"    background-color: #eaeef2;\n"
"}\n"
"\n"
"/* \u7279\u5b9a\u6309\u94ae\u6837\u5f0f\uff08\u53ef\u9009\uff0c\u6839\u636e\u9700\u8981\u8c03\u6574\uff09 */\n"
"QPushButton#btn_pd {\n"
"    background-color: #e67e22;\n"
"}\n"
"QPushButto"
                        "n#btn_pd:hover {\n"
"    background-color: #d35400;\n"
"}\n"
"QPushButton#btn_rf {\n"
"    background-color: #27ae60;\n"
"}\n"
"QPushButton#btn_rf:hover {\n"
"    background-color: #229954;\n"
"}\n"
"\n"
"/* ========== \u7ec4\u5408\u6846 ========== */\n"
"QComboBox {\n"
"    border: 1px solid #d0d7de;\n"
"    border-radius: 6px;\n"
"    padding: 6px 12px;\n"
"    background-color: #ffffff;\n"
"    min-height: 20px;\n"
"}\n"
"QComboBox:hover {\n"
"    border-color: #8a9aa8;\n"
"    background-color: #fafbfc;\n"
"}\n"
"QComboBox:focus {\n"
"    border-color: #3498db;\n"
"    outline: none;\n"
"}\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: center right;\n"
"    width: 24px;\n"
"    border-left: 1px solid #d0d7de;\n"
"    border-top-right-radius: 6px;\n"
"    border-bottom-right-radius: 6px;\n"
"    background-color: #f6f8fa;\n"
"}\n"
"QComboBox::drop-down:hover {\n"
"    background-color: #eaeef2;\n"
"}\n"
"QComboBox QAbstractItemView {\n"
"    border: 1px solid #d0"
                        "d7de;\n"
"    border-radius: 6px;\n"
"    background-color: #ffffff;\n"
"    selection-background-color: #e1eaf0;\n"
"    outline: none;\n"
"    padding: 4px 0px;\n"
"}\n"
"QComboBox QAbstractItemView::item {\n"
"    padding: 6px 12px;\n"
"    min-height: 20px;\n"
"}\n"
"QComboBox QAbstractItemView::item:hover {\n"
"    background-color: #f1f5f9;\n"
"}\n"
"\n"
"/* ========== \u8868\u683c ========== */\n"
"QTableWidget {\n"
"    border: 1px solid #d0d7de;\n"
"    border-radius: 6px;\n"
"    background-color: #ffffff;\n"
"    gridline-color: #eaeef2;\n"
"}\n"
"QTableWidget::item {\n"
"    padding: 6px;\n"
"    border-bottom: 1px solid #eaeef2;\n"
"}\n"
"QTableWidget::item:selected {\n"
"    background-color: #e1eaf0;\n"
"    color: #1a73e8;\n"
"}\n"
"QHeaderView::section {\n"
"    background-color: #f6f8fa;\n"
"    padding: 8px;\n"
"    border: none;\n"
"    border-bottom: 1px solid #d0d7de;\n"
"    font-weight: 600;\n"
"    color: #2c3e50;\n"
"}\n"
"QHeaderView::section:horizontal {\n"
"    border-right: 1px so"
                        "lid #d0d7de;\n"
"}\n"
"QHeaderView::section:vertical {\n"
"    border-right: 1px solid #d0d7de;\n"
"}\n"
"\n"
"/* ========== \u6587\u672c\u7f16\u8f91\u6846 ========== */\n"
"QTextEdit {\n"
"    border: 1px solid #d0d7de;\n"
"    border-radius: 6px;\n"
"    padding: 8px;\n"
"    background-color: #ffffff;\n"
"    selection-background-color: #e1eaf0;\n"
"}\n"
"QTextEdit:hover {\n"
"    border-color: #8a9aa8;\n"
"    background-color: #fafbfc;\n"
"}\n"
"QTextEdit:focus {\n"
"    border-color: #3498db;\n"
"    outline: none;\n"
"}\n"
"\n"
"/* ========== \u6807\u7b7e ========== */\n"
"QLabel {\n"
"    color: #2c3e50;\n"
"    background-color: transparent;\n"
"    padding: 2px 4px;\n"
"}\n"
"QLabel#notification_label {\n"
"    font-weight: 600;\n"
"    color: #1a73e8;\n"
"}\n"
"QLabel#showtime_label {\n"
"    font-weight: 600;\n"
"    color: #e67e22;\n"
"}\n"
"\n"
"/* ========== \u8fdb\u5ea6\u6761 ========== */\n"
"QProgressBar {\n"
"    border: 1px solid #d0d7de;\n"
"    border-radius: 4px;\n"
"    background-color"
                        ": #ffffff;\n"
"    text-align: center;\n"
"    color: #2c3e50;\n"
"}\n"
"QProgressBar::chunk {\n"
"    background-color: #3498db;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"/* ========== \u5e03\u5c40\u5bb9\u5668\uff08\u53ef\u9009\uff0c\u4e00\u822c\u4e0d\u7528\uff09 ========== */\n"
"QWidget#centralwidget {\n"
"    background-color: transparent;  /* \u7ee7\u627f\u4e3b\u7a97\u53e3\u80cc\u666f */\n"
"}")
        self.action_6 = QAction(MainWindow)
        self.action_6.setObjectName(u"action_6")
        font = QFont()
        self.action_6.setFont(font)
        self.action_7 = QAction(MainWindow)
        self.action_7.setObjectName(u"action_7")
        self.action_8 = QAction(MainWindow)
        self.action_8.setObjectName(u"action_8")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.showtext_label = QLabel(self.centralwidget)
        self.showtext_label.setObjectName(u"showtext_label")

        self.gridLayout.addWidget(self.showtext_label, 2, 4, 1, 1)

        self.textEdit_output = QTextEdit(self.centralwidget)
        self.textEdit_output.setObjectName(u"textEdit_output")
        self.textEdit_output.setReadOnly(True)

        self.gridLayout.addWidget(self.textEdit_output, 6, 4, 1, 3)

        self.input_combobox = QComboBox(self.centralwidget)
        self.input_combobox.setObjectName(u"input_combobox")

        self.gridLayout.addWidget(self.input_combobox, 3, 4, 1, 2)

        self.showlog_btn = QPushButton(self.centralwidget)
        self.showlog_btn.setObjectName(u"showlog_btn")

        self.gridLayout.addWidget(self.showlog_btn, 2, 5, 1, 1)

        self.btn_pca = QPushButton(self.centralwidget)
        self.btn_pca.setObjectName(u"btn_pca")

        self.gridLayout.addWidget(self.btn_pca, 0, 4, 2, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 5, 4, 1, 1)

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout.addWidget(self.pushButton, 0, 0, 1, 1)

        self.btn_pd = QPushButton(self.centralwidget)
        self.btn_pd.setObjectName(u"btn_pd")
        font1 = QFont()
        font1.setPointSize(13)
        font1.setWeight(QFont.Medium)
        self.btn_pd.setFont(font1)

        self.gridLayout.addWidget(self.btn_pd, 2, 6, 2, 1)

        self.table_selector = QComboBox(self.centralwidget)
        self.table_selector.addItem("")
        self.table_selector.setObjectName(u"table_selector")

        self.gridLayout.addWidget(self.table_selector, 0, 1, 1, 2)

        self.btn_rf = QPushButton(self.centralwidget)
        self.btn_rf.setObjectName(u"btn_rf")

        self.gridLayout.addWidget(self.btn_rf, 0, 5, 2, 2)

        self.showinput_tableWidget = QTableWidget(self.centralwidget)
        self.showinput_tableWidget.setObjectName(u"showinput_tableWidget")

        self.gridLayout.addWidget(self.showinput_tableWidget, 4, 4, 1, 3)

        self.showdata_tableWidget = QTableWidget(self.centralwidget)
        self.showdata_tableWidget.setObjectName(u"showdata_tableWidget")

        self.gridLayout.addWidget(self.showdata_tableWidget, 1, 0, 6, 3)


        self.verticalLayout.addLayout(self.gridLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.showtext_label_2 = QLabel(self.centralwidget)
        self.showtext_label_2.setObjectName(u"showtext_label_2")
        self.showtext_label_2.setMinimumSize(QSize(60, 0))
        self.showtext_label_2.setMaximumSize(QSize(80, 16777215))
        font2 = QFont()
        font2.setPointSize(11)
        self.showtext_label_2.setFont(font2)

        self.horizontalLayout.addWidget(self.showtext_label_2)

        self.notification_label = QLabel(self.centralwidget)
        self.notification_label.setObjectName(u"notification_label")
        self.notification_label.setMinimumSize(QSize(180, 20))
        self.notification_label.setMaximumSize(QSize(16777215, 16777215))
        font3 = QFont()
        font3.setWeight(QFont.DemiBold)
        self.notification_label.setFont(font3)

        self.horizontalLayout.addWidget(self.notification_label)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMinimumSize(QSize(120, 0))
        self.progressBar.setMaximumSize(QSize(120, 20))
        font4 = QFont()
        font4.setPointSize(10)
        self.progressBar.setFont(font4)
        self.progressBar.setValue(24)

        self.horizontalLayout.addWidget(self.progressBar)

        self.showtime_label = QLabel(self.centralwidget)
        self.showtime_label.setObjectName(u"showtime_label")
        self.showtime_label.setMinimumSize(QSize(140, 0))
        self.showtime_label.setMaximumSize(QSize(100, 16777215))
        self.showtime_label.setFont(font3)

        self.horizontalLayout.addWidget(self.showtime_label)


        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 825, 37))
        self.menu = QMenu(self.menuBar)
        self.menu.setObjectName(u"menu")
        font5 = QFont()
        font5.setFamilies([u"MingLiU_HKSCS-ExtB"])
        self.menu.setFont(font5)
        self.menu_2 = QMenu(self.menuBar)
        self.menu_2.setObjectName(u"menu_2")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menu.menuAction())
        self.menuBar.addAction(self.menu_2.menuAction())
        self.menu.addAction(self.action_6)
        self.menu.addSeparator()
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

