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
from PySide6.QtWidgets import (QApplication, QDialog, QSizePolicy, QTextEdit,
    QWidget)

class Ui_Dialog_aboutme(object):
    def setupUi(self, Dialog_aboutme):
        if not Dialog_aboutme.objectName():
            Dialog_aboutme.setObjectName(u"Dialog_aboutme")
        Dialog_aboutme.resize(400, 200)
        Dialog_aboutme.setMinimumSize(QSize(400, 200))
        Dialog_aboutme.setMaximumSize(QSize(400, 200))
        self.textEdit = QTextEdit(Dialog_aboutme)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(0, 0, 400, 200))
        self.textEdit.setMinimumSize(QSize(400, 200))
        self.textEdit.setMaximumSize(QSize(400, 200))
        self.textEdit.setStyleSheet(u"QDialog#Dialog_aboutme {\n"
"        background-color: #f8fafc;\n"
"        border: 1px solid #d0d7de;\n"
"        border-radius: 12px;\n"
"    }\n"
"    QTextEdit#textEdit {\n"
"        background-color: #ffffff;\n"
"        border: none;\n"
"        border-radius: 8px;\n"
"        padding: 16px;\n"
"        selection-background-color: #e1eaf0;\n"
"        color: #1e293b;\n"
"    }")
        self.textEdit.setReadOnly(True)

        self.retranslateUi(Dialog_aboutme)

        QMetaObject.connectSlotsByName(Dialog_aboutme)
    # setupUi

    def retranslateUi(self, Dialog_aboutme):
        Dialog_aboutme.setWindowTitle(QCoreApplication.translate("Dialog_aboutme", u"Dialog", None))
    # retranslateUi

