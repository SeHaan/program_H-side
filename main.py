"""
ver 1.0.5. - 20220322
============================================================
                       업데이트 내역
------------------------------------------------------------
ver. 1.0.5. 자소검색 와일드카드 문자(*) 오류 수정
ver. 1.0.4. 에러 핸들링: QMessageBox 20220322
ver. 1.0.3. 판다스 데이터프레임을 딕셔너리로 변환 20220322
ver. 1.0.2. 자소검색 기능 추가 20220322
ver. 1.0.1. 검색 스트링을 첫가끝으로 변환 20220317
ver. 1.0.0. Initial Setting 20220309
============================================================
"""
#%%
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, \
    QFileDialog, QLineEdit, QWidget, QPushButton, QTextEdit, QHBoxLayout, \
    QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtGui import QIcon
from searching import searchForWord, PUAtoUni, seperation
import pickle

with open('dict/dict_0_TOTAL.pickle', 'rb') as f:
    dict_0_TOTAL = pickle.load(f)
with open('dict/dict_0_ONSET.pickle', 'rb') as fo:
    dict_0_ONSET = pickle.load(fo)
with open('dict/dict_0_PEAK.pickle', 'rb') as fp:
    dict_0_PEAK = pickle.load(fp)
with open('dict/dict_0_CODA.pickle', 'rb') as fc:
    dict_0_CODA = pickle.load(fc)

class Search(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # setting widgets
        direcLable = QLabel('direc')
        direcLine = QLineEdit()
        findBtn = QPushButton(text="find dir")

        targetLabel = QLabel('target word')
        targetWord = QLineEdit()
        searchBtn = QPushButton(text='search')

        findRes = QTextEdit()

        # style
        font_init = direcLine.font()
        font_init.setPointSize(15)
        font_init.setFamilies(['Times New Roman', 'Malgun Gothic'])

        direcLable.setFont(font_init)
        direcLine.setFont(font_init)
        findBtn.setFont(font_init)

        targetLabel.setFont(font_init)
        targetWord.setFont(font_init)
        searchBtn.setFont(font_init)

        findRes.setFont(font_init)

        # setting box
        hbox_1 = QHBoxLayout()
        hbox_1.addWidget(direcLable)
        hbox_1.addWidget(direcLine)
        hbox_1.addWidget(findBtn)

        hbox_2 = QHBoxLayout()
        hbox_2.addWidget(targetLabel)
        hbox_2.addWidget(targetWord)
        hbox_2.addWidget(searchBtn)

        hbox_3 = QHBoxLayout()
        hbox_3.addWidget(findRes)
        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox_1)
        vbox.addLayout(hbox_2)
        vbox.addLayout(hbox_3)

        self.setLayout(vbox)
        

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        wg = Search()
        self.setCentralWidget(wg)
        """
        0   <PyQt5.QtWidgets.QVBoxLayout object at 0x0000020CB3F358B0>
        1   <PyQt5.QtWidgets.QLabel object at 0x0000020CB3F351F0> 'direc'
        2   <PyQt5.QtWidgets.QLineEdit object at 0x0000020CB3F35280> directory line
        3   <PyQt5.QtWidgets.QPushButton object at 0x0000020CB3F35310> 'find dir'
        4   <PyQt5.QtWidgets.QLabel object at 0x0000020CB3F353A0> 'target word'
        5   <PyQt5.QtWidgets.QLineEdit object at 0x0000020CB3F35430> target word line
        6   <PyQt5.QtWidgets.QPushButton object at 0x0000020CB3F355E0> 'search'
        7   <PyQt5.QtWidgets.QTextEdit object at 0x0000020CB3F35670> result text box
        """

        self.statusBar().showMessage('준비됨')

        # Action #
        openBtn = self.centralWidget().children()[3]
        openBtn.clicked.connect(self.folderOpen)
        searchBtn = self.centralWidget().children()[6]
        searchBtn.clicked.connect(self.searchWord)

        # 윈도우 #
        self.setWindowTitle("Historical Linguistics for Middle Korean (ver. 1.1.0)")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(800, 800)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def folderOpen(self):
        self.statusBar().showMessage('디렉토리 설정')
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.centralWidget().children()[2].setText(folder)
        self.statusBar().showMessage('디렉토리 설정 완료')

    def searchWord(self):
        self.centralWidget().children()[7].clear()
        dir = self.centralWidget().children()[2].text()

        ## 디렉토리 확인 ##
        if dir == '':
            self.statusBar().showMessage('오류: 빈 디렉토리')
            msgBox = QMessageBox.critical(self, 'Warning', '디렉토리를 설정해야 합니다!')
            return
        else:
            dir += "/"
        target = self.centralWidget().children()[5].text()

        if target == '':
            self.statusBar().showMessage('오류: 빈 검색 문자열')
            msgBox = QMessageBox.critical(self, 'Warning', '빈 문자열은 검색할 수 없습니다!')
        else:
            target = PUAtoUni(target, dict_0_TOTAL)
            target = seperation(target, dict_0_ONSET, dict_0_PEAK, dict_0_CODA)

            if target == '!!error!!':
                self.statusBar().showMessage('오류: 잘못된 검색 문자열')
                msgBox = QMessageBox.critical(self, 'Warning', '잘못된 입력입니다!')
                return

            result_line, iter = searchForWord(dir, target)

            if result_line == '':
                msgBox = QMessageBox.critical(self, 'Warning', '검색 결과가 없습니다 ㅜㅡㅜ')
            else:
                msgBox = QMessageBox.critical(self, 'Completed', '총 ' + str(iter) + '개가 검색되었습니다.')
            self.centralWidget().children()[7].append(result_line)
            self.statusBar().showMessage('열심히 검색 완료: 총 {0}개의 검색 결과'.format(str(iter)))

## 메인 ##
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainApp()
    sys.exit(app.exec_())