# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainui.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QProgressBar, QSizePolicy,
    QWidget)

class Ui_widget(object):
    def setupUi(self, widget):
        if not widget.objectName():
            widget.setObjectName(u"widget")
        widget.resize(818, 608)
        self.notification_label = QLabel(widget)
        self.notification_label.setObjectName(u"notification_label")
        self.notification_label.setGeometry(QRect(430, 460, 331, 41))
        font = QFont()
        font.setBold(True)
        self.notification_label.setFont(font)
        self.progressBar = QProgressBar(widget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(460, 530, 118, 23))
        self.progressBar.setValue(24)

        self.retranslateUi(widget)

        QMetaObject.connectSlotsByName(widget)
    # setupUi

    def retranslateUi(self, widget):
        widget.setWindowTitle(QCoreApplication.translate("widget", u"Form", None))
        self.notification_label.setText(QCoreApplication.translate("widget", u"TextLabel", None))
    # retranslateUi

