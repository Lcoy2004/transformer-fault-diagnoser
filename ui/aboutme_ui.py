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
        Dialog_aboutme.resize(400, 200)
        Dialog_aboutme.setMinimumSize(QSize(400, 200))
        Dialog_aboutme.setMaximumSize(QSize(400, 200))
        Dialog_aboutme.setStyleSheet(u"\n"
"/* ================================================\n"
"   \u5173\u4e8e\u5bf9\u8bdd\u6846 - \u73b0\u4ee3\u5316\u7b80\u7ea6\u98ce\u683c\n"
"   \u8bbe\u8ba1\u7406\u5ff5\uff1a\u4e13\u4e1a\u3001\u7b80\u6d01\u3001\u6e05\u6670\n"
"   ================================================ */\n"
"\n"
"QDialog#Dialog_aboutme {\n"
"    background-color: #f0f4f8;\n"
"    border: 1px solid #dde2e8;\n"
"    border-radius: 12px;\n"
"}\n"
"\n"
"/* \u6587\u672c\u7f16\u8f91\u6846 - \u4e3b\u5185\u5bb9\u533a */\n"
"QTextBrowser#textEdit {\n"
"    background-color: #ffffff;\n"
"    border: none;\n"
"    border-radius: 10px;\n"
"    padding: 20px 24px;\n"
"    selection-background-color: #bbdefb;\n"
"    color: #334155;\n"
"    font-family: \"Microsoft YaHei\", \"Segoe UI\", Arial, sans-serif;\n"
"    font-size: 13px;\n"
"    line-height: 1.7;\n"
"}\n"
"\n"
"/* \u6807\u9898\u6837\u5f0f - \u4f7f\u7528 HTML */\n"
"QTextBrowser#textEdit strong {\n"
"    color: #1e3a5f;\n"
"    font-size: 15px;\n"
"}\n"
"\n"
"/* \u94fe\u63a5\u6837\u5f0f"
                        " */\n"
"QTextBrowser#textEdit a {\n"
"    color: #1e88e5;\n"
"    text-decoration: none;\n"
"}\n"
"\n"
"QTextBrowser#textEdit a:hover {\n"
"    color: #1976d2;\n"
"    text-decoration: underline;\n"
"}\n"
"\n"
"")
        self.textEdit = QTextBrowser(Dialog_aboutme)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(0, 0, 400, 200))
        self.textEdit.setMinimumSize(QSize(400, 200))
        self.textEdit.setMaximumSize(QSize(400, 200))
        self.textEdit.setStyleSheet(u"QDialog#Dialog_aboutme {\n"
"        background-color: #f8fafc;\n"
"        border: 1px solid #d0d7de;\n"
"        border-radius: 12px;\n"
"    }\n"
"    QTextBrowser#textEdit {\n"
"        background-color: #ffffff;\n"
"        border: none;\n"
"        border-radius: 8px;\n"
"        padding: 16px;\n"
"        selection-background-color: #e1eaf0;\n"
"        color: #1e293b;\n"
"    }")
        self.textEdit.setReadOnly(True)
        self.textEdit.setOpenExternalLinks(True)

        self.retranslateUi(Dialog_aboutme)

        QMetaObject.connectSlotsByName(Dialog_aboutme)
    # setupUi

    def retranslateUi(self, Dialog_aboutme):
        Dialog_aboutme.setWindowTitle(QCoreApplication.translate("Dialog_aboutme", u"Dialog", None))
    # retranslateUi

