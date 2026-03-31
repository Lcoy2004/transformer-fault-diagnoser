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
        Dialog_guide.setWindowTitle(QCoreApplication.translate("Dialog_guide", u"Dialog", None))
        self.textEdit.setDocumentTitle(QCoreApplication.translate("Dialog_guide", u"\u64cd\u4f5c\u8bf4\u660e", None))
    # retranslateUi

