import os, sys
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

STYLE = """
QMainWindow { background-color: #121218; }
QWidget { color: #F0F0F5; font-family: 'Segoe UI', Arial; }
QFrame#Sidebar { background-color: #1A1A24; border-right: 1px solid #2C2C3A; }
QFrame#TopBar { background-color: #16161E; border-bottom: 1px solid #2C2C3A; }
QPushButton#NavBtn { background: transparent; border: none; border-radius: 10px; padding: 14px; text-align: left; font-size: 15px; font-weight: bold; color: #A0A0B8; }
QPushButton#NavBtn:hover { background: #252535; color: #FFF; }
QPushButton#NavBtn[active="true"] { background: #FF4D94; color: #FFF; }
QFrame#GameCard { background: #1E1E2A; border: 1px solid #323246; border-radius: 14px; padding: 16px; }
QPushButton#ActionBtn { background: #FF4D94; color: white; border: none; border-radius: 8px; padding: 10px 18px; font-weight: bold; }
QPushButton#ActionBtn:hover { background: #FF6BA6; }
QPushButton#ActionBtn:disabled { background: #2E8B57; }
QListWidget { background: #1A1A24; border: 1px solid #2C2C3A; border-radius: 10px; padding: 6px; }
"""


class MeiPlayWindow(QMainWindow):

  def __init__(self):
    super().__init__()
    self.setWindowTitle("MeiPlay OS")
    self.resize(1050, 650)
    self.setStyleSheet(STYLE)
    self.balance, self.owned_games = 500, set()

    cw = QWidget()
    self.setCentralWidget(cw)
    ml = QVBoxLayout(cw)
    ml.setContentsMargins(0, 0, 0, 0)
    ml.setSpacing(0)

    top = QFrame(objectName="TopBar", fixedHeight=55)
    tl = QHBoxLayout(top)
    tl.addWidget(
        QLabel(
            "MeiPlay",
            font=QFont("Segoe UI", 16, QFont.Bold),
            styleSheet="color:#FF4D94;",
        )
    )
    tl.addStretch()
    self.bal_lbl = QLabel(
        f"Баланс: {self.balance} монет",
        styleSheet="background:#252535; padding:6px 14px; border-radius:12px;",
    )
    tl.addWidget(self.bal_lbl)
    ml.addWidget(top)

    bl = QHBoxLayout()
    side = QFrame(objectName="Sidebar", fixedWidth=210)
    sl = QVBoxLayout(side)
    self.nav_btns = [
        QPushButton(t, objectName="NavBtn")
        for t in ("Магазинчик", "Мои игры", "Музыка", "Видео")
    ]
    for i, b in enumerate(self.nav_btns):
      b.clicked.connect(lambda _, idx=i: self.switch_tab(idx))
      sl.addWidget(b)
    sl.addStretch()
    bl.addWidget(side)

    self.pages = QStackedWidget()
    for p in (
        self.page_shop(),
        self.page_games(),
        self.page_music(),
        self.page_video(),
    ):
      self.pages.addWidget(p)
    bl.addWidget(self.pages)
    ml.addLayout(bl)
    self.switch_tab(0)

  def switch_tab(self, idx):
    self.pages.setCurrentIndex(idx)
    for i, b in enumerate(self.nav_btns):
      b.setProperty("active", i == idx)
      b.style().unpolish(b)
      b.style().polish(b)

  def page_shop(self):
    p = QWidget()
    l = QVBoxLayout(p)
    self.catalog = [
        {
            "id": "dachshund_jump",
            "title": "Прыгающая Такса",
            "desc": "Прыгай от лавы, уворачивайся от пил и шипов!",
            "price": 150,
        },
        {
            "id": "dachshund_drop",
            "title": "Такса-Дроп",
            "desc": "Открывай карточки такс, продавай или улучшай с шансом.",
            "price": 250,
        },
    ]
    for g in self.catalog:
      card = QFrame(objectName="GameCard")
      cl = QHBoxLayout(card)
      il = QVBoxLayout()
      il.addWidget(QLabel(g["title"], font=QFont("Segoe UI", 15, QFont.Bold)))
      il.addWidget(QLabel(g["desc"], styleSheet="color:#B0B0C8;"))
      btn = QPushButton(f"Купить за {g['price']}", objectName="ActionBtn")
      btn.clicked.connect(lambda _, game=g, b=btn: self.buy_game(game, b))
      cl.addLayout(il)
      cl.addStretch()
      cl.addWidget(btn)
      l.addWidget(card)
    l.addStretch()
    return p

  def buy_game(self, g, btn):
    if self.balance >= g["price"]:
      self.balance -= g["price"]
      self.owned_games.add(g["id"])
      self.bal_lbl.setText(f"Баланс: {self.balance} монет")
      btn.setText("В библиотеке")
      btn.setEnabled(False)
      self.refresh_games()
    else:
      QMessageBox.warning(self, "Ошибка", "Недостаточно монет!")

  def page_games(self):
    p = QWidget()
    self.gl = QVBoxLayout(p)
    self.gl.addWidget(QLabel("Пока пусто! Купи первую игру в Магазинчике."))
    self.gl.addStretch()
    return p

  def refresh_games(self):
    while self.gl.count():
      w = self.gl.takeAt(0).widget()
      if w:
        w.deleteLater()
    for g in self.catalog:
      if g["id"] in self.owned_games:
        card = QFrame(objectName="GameCard")
        cl = QHBoxLayout(card)
        cl.addWidget(QLabel(g["title"], font=QFont("Segoe UI", 14, QFont.Bold)))
        btn = QPushButton("Играть", objectName="ActionBtn")
        btn.clicked.connect(lambda _, gid=g["id"]: self.launch_game(gid))
        cl.addStretch()
        cl.addWidget(btn)
        self.gl.addWidget(card)
    self.gl.addStretch()

  def launch_game(self, gid):
    QMessageBox.information(self, "Запуск", f"Запускаем {gid}!")

  def page_music(self):
    p = QWidget()
    l = QVBoxLayout(p)
    btn = QPushButton("Выбрать папку с музыкой", objectName="ActionBtn")
    btn.clicked.connect(self.load_music)
    l.addWidget(btn)
    self.tlist = QListWidget()
    self.tlist.itemDoubleClicked.connect(self.play_track)
    l.addWidget(self.tlist)
    self.mp = QMediaPlayer()
    self.ma = QAudioOutput()
    self.mp.setAudioOutput(self.ma)
    pbtn = QPushButton("Пауза / Играть", objectName="ActionBtn")
    pbtn.clicked.connect(
        lambda: self.mp.pause()
        if self.mp.playbackState() == QMediaPlayer.PlayingState
        else self.mp.play()
    )
    l.addWidget(pbtn)
    self.mfiles = []
    return p

  def load_music(self):
    d = QFileDialog.getExistingDirectory(self, "Папка")
    if d:
      self.tlist.clear()
      self.mfiles = [
          os.path.join(d, f)
          for f in sorted(os.listdir(d))
          if f.lower().endswith((".mp3", ".wav", ".ogg", ".flac"))
      ]
      for f in self.mfiles:
        self.tlist.addItem(os.path.basename(f))

  def play_track(self):
    r = self.tlist.currentRow()
    if 0 <= r < len(self.mfiles):
      self.mp.setSource(QUrl.fromLocalFile(self.mfiles[r]))
      self.mp.play()

  def page_video(self):
    p = QWidget()
    l = QVBoxLayout(p)
    btn = QPushButton("Открыть видео", objectName="ActionBtn")
    btn.clicked.connect(self.open_vid)
    l.addWidget(btn)
    vw = QVideoWidget()
    l.addWidget(vw, 1)
    self.vp = QMediaPlayer()
    self.va = QAudioOutput()
    self.vp.setAudioOutput(self.va)
    self.vp.setVideoOutput(vw)
    pbtn = QPushButton("Пауза / Играть", objectName="ActionBtn")
    pbtn.clicked.connect(
        lambda: self.vp.pause()
        if self.vp.playbackState() == QMediaPlayer.PlayingState
        else self.vp.play()
    )
    l.addWidget(pbtn)
    return p

  def open_vid(self):
    f, _ = QFileDialog.getOpenFileName(
        self, "Видео", "", "Видео (*.mp4 *.avi *.mkv *.mov)"
    )
    if f:
      self.mp.pause()
      self.vp.setSource(QUrl.fromLocalFile(f))
      self.vp.play()


if __name__ == "__main__":
  app = QApplication(sys.argv)
  w = MeiPlayWindow()
  w.show()
  sys.exit(app.exec())
