import importlib, os, sys
from disc_drive import DiscDriveDialog
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
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

GAMES_INFO = [
    {
        "id": "jump",
        "title": "Прыгающая Такса",
        "desc": "Прыгай от лавы, уворачивайся от пил и шипов!",
        "price": 150,
        "mod": "games.dachshund_jump",
        "cls": "DachshundJumpGame",
        "mode": "fin",
    },
    {
        "id": "drop",
        "title": "Такса-Дроп",
        "desc": "Открывай карточки такс, продавай или улучшай с шансом.",
        "price": 250,
        "mod": "games.dachshund_drop",
        "cls": "DachshundDropGame",
        "mode": "bal",
    },
    {
        "id": "mines",
        "title": "Такса-Сапёр",
        "desc": "Умножай ставку, собирая сосиски на поле 5x5.",
        "price": 100,
        "mod": "games.dachshund_mines",
        "cls": "DachshundMinesGame",
        "mode": "bal",
    },
    {
        "id": "sniffe",
        "title": "Sausage Sniffe",
        "desc": "Собери 10 сосисок на поле 16x16 и обойди 15 костей!",
        "price": 200,
        "mod": "games.sausage_sniffe",
        "cls": "SausageSniffeGame",
        "mode": "fin",
    },
    {
        "id": "dash",
        "title": "Dachshund Dash",
        "desc": "Беги, прыгай через кактусы и пригибайся от ворон!",
        "price": 120,
        "mod": "games.dachshund_dash",
        "cls": "DachshundDashGame",
        "mode": "fin",
    },
    {
        "id": "catch",
        "title": "Ловец Сосисок",
        "desc": "Лови сосиски и шоколадки Милка, уклоняйся от колючек.",
        "price": 130,
        "mod": "games.sausage_catcher",
        "cls": "SausageCatcherGame",
        "mode": "fin",
    },
    {
        "id": "long",
        "title": "Длинная Такса",
        "desc": "Ретро-змейка: расти таксу до невероятных размеров!",
        "price": 140,
        "mod": "games.long_dachshund",
        "cls": "LongDachshundGame",
        "mode": "fin",
    },
    {
        "id": "pong",
        "title": "Такса-Арканоид",
        "desc": "Отбивай мяч таксой и разбивай неоновые блоки.",
        "price": 160,
        "mod": "games.dachshund_pong",
        "cls": "DachshundPongGame",
        "mode": "fin",
    },
]

STYLE = """
QMainWindow, QDialog { background-color: #121218; color: #F0F0F5; font-family: 'Segoe UI', Arial; }
QFrame#Sidebar { background-color: #1A1A24; border-right: 1px solid #2C2C3A; }
QFrame#TopBar { background-color: #16161E; border-bottom: 1px solid #2C2C3A; }
QPushButton#NavBtn { background: transparent; border: none; border-radius: 10px; padding: 12px; text-align: left; font-size: 14px; font-weight: bold; color: #A0A0B8; }
QPushButton#NavBtn:hover { background: #252535; color: #FFF; }
QPushButton#NavBtn[active="true"] { background: #FF4D94; color: #FFF; }
QPushButton#DiscBtn { background: #252538; border: 1px solid #FF4D94; border-radius: 10px; padding: 12px; text-align: left; font-size: 14px; font-weight: bold; color: #FF85B8; }
QPushButton#DiscBtn:hover { background: #FF4D94; color: #FFF; }
QFrame#GameCard { background: #1E1E2A; border: 1px solid #323246; border-radius: 12px; padding: 12px; }
QPushButton#ActionBtn { background: #FF4D94; color: white; border: none; border-radius: 8px; padding: 8px 14px; font-weight: bold; }
QPushButton#ActionBtn:hover { background: #FF6BA6; }
QPushButton#ActionBtn:disabled { background: #2E8B57; }
QListWidget, QScrollArea { background: transparent; border: none; }
QListWidget { background: #1A1A24; border: 1px solid #2C2C3A; border-radius: 10px; padding: 6px; }
"""
class MeiPlayWindow(QMainWindow):

  def __init__(self):
    super().__init__()
    self.setWindowTitle("MeiPlay OS - PC Edition")
    self.resize(1050, 650)
    self.setStyleSheet(STYLE)
    self.balance, self.owned = 600, set()

    cw = QWidget()
    self.setCentralWidget(cw)
    ml = QVBoxLayout(cw)
    ml.setContentsMargins(0, 0, 0, 0)
    ml.setSpacing(0)

    top = QFrame(objectName="TopBar", fixedHeight=55)
    tl = QHBoxLayout(top)
    tl.addWidget(
        QLabel(
            "MeiPlay OS",
            font=QFont("Segoe UI", 16, QFont.Bold),
            styleSheet="color:#FF4D94;",
        )
    )
    tl.addStretch()
    self.bal_lbl = QLabel(
        f"Баланс: {self.balance} монет",
        styleSheet=(
            "background:#252535; padding:6px 14px; border-radius:12px;"
            " font-weight:bold;"
        ),
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

    disc_btn = QPushButton("Вставить диск", objectName="DiscBtn")
    disc_btn.clicked.connect(self.open_disc_drive)
    sl.addSpacing(15)
    sl.addWidget(disc_btn)
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

  def open_disc_drive(self):
    tuples_list = [(g["id"], g["title"]) for g in GAMES_INFO]
    DiscDriveDialog(self, self.launch_game, self.owned, tuples_list).exec()

  def change_bal(self, d):
    self.balance += d
    self.bal_lbl.setText(f"Баланс: {self.balance} монет")

  def switch_tab(self, idx):
    self.pages.setCurrentIndex(idx)
    for i, b in enumerate(self.nav_btns):
      b.setProperty("active", i == idx)
      b.style().unpolish(b)
      b.style().polish(b)

  def page_shop(self):
    scroll = QScrollArea(widgetResizable=True)
    cont = QWidget()
    l = QVBoxLayout(cont)
    for g in GAMES_INFO:
      card = QFrame(objectName="GameCard")
      cl = QHBoxLayout(card)
      il = QVBoxLayout()
      il.addWidget(QLabel(g["title"], font=QFont("Segoe UI", 14, QFont.Bold)))
      il.addWidget(QLabel(g["desc"], styleSheet="color:#B0B0C8;"))
      btn = QPushButton(f"Купить за {g['price']}", objectName="ActionBtn")
      btn.clicked.connect(lambda _, game=g, b=btn: self.buy_game(game, b))
      cl.addLayout(il)
      cl.addStretch()
      cl.addWidget(btn)
      l.addWidget(card)
    l.addStretch()
    scroll.setWidget(cont)
    return scroll

  def buy_game(self, g, btn):
    if self.balance >= g["price"]:
      self.change_bal(-g["price"])
      self.owned.add(g["id"])
      btn.setText("Куплено")
      btn.setEnabled(False)
      self.refresh_games()
    else:
      QMessageBox.warning(
          self, "Мало монет", "Заработай больше монет в играх!"
      )

  def page_games(self):
    scroll = QScrollArea(widgetResizable=True)
    cont = QWidget()
    self.gl = QVBoxLayout(cont)
    self.gl.addWidget(QLabel("Купи игры в магазине или вставь диск с играми!"))
    self.gl.addStretch()
    scroll.setWidget(cont)
    return scroll

  def refresh_games(self):
    while self.gl.count():
      w = self.gl.takeAt(0).widget()
      if w:
        w.deleteLater()
    for g in GAMES_INFO:
      if g["id"] in self.owned:
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
    g = next((x for x in GAMES_INFO if x["id"] == gid), None)
    if not g:
      return
    try:
      mod = importlib.import_module(g["mod"])
      cls = getattr(mod, g["cls"])
      if g["mode"] == "fin":
        cls(self, on_finish=self.change_bal).exec()
      else:
        cls(
            self,
            get_balance=lambda: self.balance,
            change_balance=self.change_bal,
        ).exec()
    except Exception as e:
      QMessageBox.critical(
          self, "Ошибка запуска", f"Не удалось открыть {g['title']}:\n{e}"
      )

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
    d = QFileDialog.getExistingDirectory(self, "Папка с музыкой")
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
