import sys
import httpx
import trio
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QGuiApplication
import pandas as pd
from PyQt6.QtCore import Qt, QSize, QRunnable, pyqtSlot, QThreadPool, pyqtSignal, QObject
from PyQt6.QtWidgets import QLineEdit, QPushButton, QMainWindow, QVBoxLayout, QWidget, QApplication, QHBoxLayout, \
    QLabel, QTableView, QToolBar, QDialog

class QSSLoader:
    def __init__(self):
        pass

    @staticmethod
    def read_qss_file(qss_file_name):
        with open(qss_file_name, 'r',  encoding='UTF-8') as file:
            return file.read()

# 自定义信号
class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    info = pyqtSignal(object)
    progress = pyqtSignal(int)

# 数据模型
class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    # 数据行的添加
    def addData(self,data):
        self._data.loc[len(self._data)] = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

        # 给视图显示颜色
        if role == Qt.ItemDataRole.BackgroundRole:
            value = self._data.iloc[index.row(),1]
            if value == 200:
                return QtGui.QColor("#CCFF99")
            else: return QtGui.QColor("#FF3030")

    def getdata(self,row,coloum):
        return self._data.iloc[row,coloum]

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])

# 新开线程，运行主要请求网址程序
class MainWorker(QRunnable):
    def __init__(self,url="baidu.com",*args,**kwargs):
        super(MainWorker, self).__init__()
        self.DUrl = url
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self._running = False
        self.finshedIndex = 0


    def setUrl(self,url):
        result = []
        with open("links.txt","r",encoding="utf8") as file:
            l = file.readlines()
            for i in l:
                i = i.replace("\n","")
                i = i.replace("***",url)
                result.append(i)
        return result

    async def main(self):
        async with httpx.AsyncClient() as client:
            result = self.setUrl(self.DUrl)
            self.signals.info.emit(str("0"+"/"+str(len(result))))
            for i in result:
                if self._running:
                    self.finshedIndex += 1
                    try:
                        response = await client.get(i)
                        self.signals.result.emit([i,response.status_code])
                        self.signals.info.emit(str(str(self.finshedIndex) + "/" + str(len(result))))
                    except:
                        pass
                else:
                    break
    def stop(self):
        self._running = False

    @pyqtSlot()
    def run(self) -> None:
        print("running")
        self._running = True
        trio.run(self.main)

# 使用说明的dialog组件
class CustomDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用说明")
        self.VBox = QVBoxLayout()
        message = {}
        message["message1"] = QLabel("程序说明：")
        message["message2"] = QLabel("外链工具只是网站推广的辅助工具，一般适用于短时间内无法建设大量外链的新站，新站应坚持每天做一到两次为宜，大约一周左右能看到效果。老站不建议使用此类工具，老站应以优质内容建设为主，辅以交换优质的友情链接和高权重站点发布软文来建立外链方为上策。")

        message["message3"] = QLabel("软件下载：")
        message["message4"] = QLabel("吾爱破解")

        message["message5"] = QLabel("工具原理：")
        message["message6"] = QLabel("可能很多第一次使用外链工具的站长朋友们都会担心同一个问题，就是会不会被百度K站、降权等风险？其实大家只要了解此类工具批量增加外链的原理就不会担心这个问题。")
        message["message7"] = QLabel("此类工具的原理其实非常简单，网络上几乎所有的网站查询工具（例如爱站网、去查网和Chinaz站长工具）都会留下查询网站的外链。你要是把网络上的每一个工具站都去查询一遍，就能为查询的网站建设大量的外链。")
        message["message8"] = QLabel("外链工具正是利用这个原理，免除你手动去访问每一个工具站查询，利用收集到的工具站列表，在线自动为你的网站查询。这种方法建设的外链是正规有效的，所以不必担心被K站和降权的风险。")
        message["message7"] = QLabel("作者：")
        message["message8"] = QLabel("iheng")

        for i in message.values():
            i.adjustSize()
            i.setFixedWidth(400)
            i.setWordWrap(True)
            self.VBox.addWidget(i)
        self.setLayout(self.VBox)

# 主程序的界面线程
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(QSize(600, 400))
        self.setWindowTitle("SEO提升软件")

        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        button_action = QAction("使用说明", self)
        button_action.triggered.connect(self.tellMe)
        toolbar.addAction(button_action)

        self.threadpool = QThreadPool()
        self.worker = None

        HBox = QHBoxLayout()
        HBox2 = QHBoxLayout()
        VBox = QVBoxLayout()

        httplabel = QLabel("http(s)//")
        HBox.addWidget(httplabel)

        self.UrlLine = QLineEdit()
        self.UrlLine.setPlaceholderText("提示： 不要加https://,域名后面不加/,效果更佳")
        HBox.addWidget(self.UrlLine)

        startButton = QPushButton("开始推广",clicked=self.start,objectName="startbutton")
        stopButton = QPushButton("停止")
        # startButton.clicked.connect(self.start)
        stopButton.clicked.connect(self.stop)
        HBox.addWidget(startButton)
        HBox.addWidget(stopButton)

        URLTAP = QLabel("网址（默认：baidu.com）:")
        URLTAP.setLineWidth(150)
        self.Slabel = QLabel()
        HBox2.addWidget(URLTAP)
        HBox2.addWidget(self.Slabel)
        COMPLETEDTAP = QLabel("完成度：")
        self.Clabel = QLabel()
        HBox2.addWidget(COMPLETEDTAP)
        HBox2.addWidget(self.Clabel)


        self.table = QTableView()
        data = pd.DataFrame(columns=["链接","结果"])

        self.model = TableModel(data)
        self.table.setModel(self.model)
        self.table.setColumnWidth(0,460)
        self.table.setColumnWidth(1, 80)
        self.table.clicked.connect(self.copydata)

        VBox.addLayout(HBox)
        VBox.addLayout(HBox2)
        VBox.addWidget(self.table)

        widget = QWidget()
        widget.setLayout(VBox)
        self.setCentralWidget(widget)
        self.statusBar().setStyleSheet("")
        self.statusBar().show()
        self.show()

    # 软件使用说明插槽
    def tellMe(self):
        dlg = CustomDialog(self)
        dlg.exec()

    # 点击链接复制
    def copydata(self):
        indexes = self.table.selectedIndexes()
        p = indexes.copy()
        if indexes:
            index = indexes[0]
            row = index.row()
            coloum = index.column()
            text = self.model.getdata(row,coloum)
            # 创建截切板实例
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)
            self.statusBar().showMessage("已复制链接",2000)

    # 开始推广链接插槽
    def start(self):
        if not self.worker:
            url = self.UrlLine.text()
            if url:
                self.Slabel.setText(url)
                self.worker = MainWorker(url=url)
            else:
                self.worker = MainWorker()
                self.Slabel.setText("baidu.com")
            self.threadpool.start(self.worker)
            self.worker.signals.result.connect(self.dataChange)
            self.worker.signals.info.connect(self.infoChanged)

    # 推广时，界面显示
    def dataChange(self,result):
        if result:
            self.model.addData(result)
            self.model.layoutChanged.emit()
    def infoChanged(self,info):
        if info:
            self.Clabel.setText(info)

    def stop(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
            self.statusBar().showMessage("已停止",2000)

# qss的载入，未写
styleSheet = """

"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(styleSheet)
    window = MainWindow()
    window.show()
    app.exec()

