# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'guide.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QSizePolicy,
    QTextEdit, QWidget)

class Ui_Dialog_guide(object):
    def setupUi(self, Dialog_guide):
        if not Dialog_guide.objectName():
            Dialog_guide.setObjectName(u"Dialog_guide")
        Dialog_guide.resize(722, 600)
        Dialog_guide.setMinimumSize(QSize(600, 600))
        Dialog_guide.setStyleSheet(u"\n"
"/* ================================================\n"
"   \u64cd\u4f5c\u8bf4\u660e\u5bf9\u8bdd\u6846 - \u73b0\u4ee3\u5316\u5de5\u4e1a\u98ce\u683c\n"
"   \u8bbe\u8ba1\u7406\u5ff5\uff1a\u7b80\u6d01\u3001\u4e13\u4e1a\u3001\u4fe1\u606f\u5c42\u6b21\u6e05\u6670\n"
"   \u4e3b\u8272\u8c03\uff1a\u6df1\u84dd\u7070 (#1E293B)\n"
"   \u5f3a\u8c03\u8272\uff1a\u79d1\u6280\u84dd (#3B82F6)\n"
"   ================================================ */\n"
"\n"
"QDialog {\n"
"    background-color: #F8FAFC;\n"
"}\n"
"\n"
"QTextEdit {\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 10px;\n"
"    padding: 20px;\n"
"    selection-background-color: #DBEAFE;\n"
"    color: #334155;\n"
"    font-family: \"Microsoft YaHei\", \"Segoe UI\", Arial, sans-serif;\n"
"    font-size: 13px;\n"
"    line-height: 1.8;\n"
"}\n"
"")
        self.gridLayout = QGridLayout(Dialog_guide)
        self.gridLayout.setObjectName(u"gridLayout")
        self.textEdit = QTextEdit(Dialog_guide)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.textEdit, 0, 0, 1, 1)


        self.retranslateUi(Dialog_guide)

        QMetaObject.connectSlotsByName(Dialog_guide)
    # setupUi

    def retranslateUi(self, Dialog_guide):
        Dialog_guide.setWindowTitle(QCoreApplication.translate("Dialog_guide", u"\u64cd\u4f5c\u8bf4\u660e", None))
        self.textEdit.setDocumentTitle(QCoreApplication.translate("Dialog_guide", u"\u64cd\u4f5c\u8bf4\u660e", None))
    # retranslateUi

