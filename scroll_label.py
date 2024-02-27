from PyQt5 import QtWidgets, QtCore, QtGui


class ScrollLabel(QtWidgets.QScrollArea):

    def __init__(self, *arg, **kwargs):
        QtWidgets.QScrollArea.__init__(self, *arg, **kwargs)
        self.setWidgetResizable(True)
        content = QtWidgets.QWidget(self)
        self.setWidget(content)
        self.label = QtWidgets.QLabel(content)
        self.label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setFont(QtGui.QFont("Times", 14, QtGui.QFont.Bold))
        lay = QtWidgets.QVBoxLayout(content)
        lay.addWidget(self.label)

    def change_pos(self, n):
        self.verticalScrollBar().setSliderPosition(n)

    def setText(self, text1, text2):
        text = '''<font color="red">{text1}</font>
                <font color="black">{text2}</font>'''.format(text1=text1,
                                                             text2=text2)
        self.label.setText(text)

    def setPixmap(self, image):
        oImage = QtGui.QImage(image)
        sImage = oImage.scaled(QtCore.QSize(self.width(), self.height()))
        palette = QtGui.QPalette()
        palette.setBrush(10, QtGui.QBrush(sImage))
        self.setPalette(palette)
