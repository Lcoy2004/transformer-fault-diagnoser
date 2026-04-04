# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'aboutme.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QSizePolicy, QTextBrowser,
    QWidget)

class Ui_Dialog_aboutme(object):
    def setupUi(self, Dialog_aboutme):
        if not Dialog_aboutme.objectName():
            Dialog_aboutme.setObjectName(u"Dialog_aboutme")
        Dialog_aboutme.resize(400, 250)
        Dialog_aboutme.setMinimumSize(QSize(400, 250))
        Dialog_aboutme.setMaximumSize(QSize(400, 250))
        Dialog_aboutme.setStyleSheet(u"\n"
"/* ================================================\n"
"   \u5173\u4e8e\u5bf9\u8bdd\u6846 - \u73b0\u4ee3\u5316\u7b80\u7ea6\u98ce\u683c\n"
"   \u8bbe\u8ba1\u7406\u5ff5\uff1a\u4e13\u4e1a\u3001\u7b80\u6d01\u3001\u6241\u5e73\u5316\n"
"   \u4e3b\u8272\u8c03\uff1a\u6df1\u84dd\u7070 (#1E293B)\n"
"   \u5f3a\u8c03\u8272\uff1a\u79d1\u6280\u84dd (#3B82F6)\n"
"   ================================================ */\n"
"\n"
"QDialog {\n"
"    background-color: #F8FAFC;\n"
"}\n"
"\n"
"QTextBrowser {\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 10px;\n"
"    padding: 20px 24px;\n"
"    selection-background-color: #DBEAFE;\n"
"    color: #334155;\n"
"    font-family: \"Microsoft YaHei\", \"Segoe UI\", Arial, sans-serif;\n"
"    font-size: 13px;\n"
"    line-height: 1.7;\n"
"}\n"
"")
        self.textEdit = QTextBrowser(Dialog_aboutme)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(0, 0, 401, 281))
        self.textEdit.setReadOnly(True)
        self.textEdit.setOpenExternalLinks(True)

        self.retranslateUi(Dialog_aboutme)

        QMetaObject.connectSlotsByName(Dialog_aboutme)
    # setupUi

    def retranslateUi(self, Dialog_aboutme):
        Dialog_aboutme.setWindowTitle(QCoreApplication.translate("Dialog_aboutme", u"\u5173\u4e8e", None))
    # retranslateUi

