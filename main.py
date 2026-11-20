import importlib, os, sys
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QFont
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# Список всех 8 игр: (id, название, описание, цена, модуль, класс, тип_коллбэка)
GAMES_INFO = [
    (
        "jump",
        "Прыгающая Такса",
        "Прыгай от лавы, уворачивайся от пил и шипов!",
        150,
        "games.dachshund_jump",
        "DachshundJumpGame",
        "fin",
    ),
    (
        "drop",
        "Такса-Дроп",
        "Открывай карточки такс, продавай или улучшай с шансом.",
        250,
        "games.dachshund_drop",
        "DachshundDropGame",
        "bal",
    ),
    (
        "mines",
        "Такса-Сапёр",
        "Умножай ставку, собирая сосиски на поле 5x5.",
        100,
        "games.dachshund_mines",
        "DachshundMinesGame",
        "bal",
    ),
    (
        "sniffe",
        "Sausage Sniffe",
        "Собери 10 сосисок на поле 16x16 и обойди 15 костей!",
        200,
        "games.sausage_sniffe",
        "SausageSniffeGame",
        "fin",
    ),
    (
        "dash",
        "Dachshund Dash",
        "Беги, прыгай через кактусы и пригибайся от ворон!",
        120,
        "games.dachshund_dash",
        "DachshundDashGame",
        "fin",
    ),
    (
        "catch",
        "Ловец Сосисок",
        "Лови сосиски и шоколадки Милка, уклоняйся от колючек.",
        130,
        "games.sausage_catcher",
        "SausageCatcherGame",
        "fin",
    ),
    (
        "long",
        "Длинная Такса",
        "Ретро-змейка: расти таксу до невероятных размеров!",
        140,
        "games.long_dachshund",
        "LongDachshundGame",
        "fin",
    ),
    (
        "pong",
        "Такса-Арканоид",
        "Отбивай мяч таксой и разбивай неоновые блоки.",
        160,
        "games.dachshund_pong",
        "DachshundPongGame",
        "fin",
    ),
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


class DiscDriveDialog(QDialog):

  def __init__(self, parent, launch_cb):
    super().__init__(parent)
    self.setWindowTitle("Привод MeiPlay UMD / DVD")
    self.setFixedSize(420, 320)
    self.launch_cb = launch_cb
    self.sec = 10
    self.l = QVBoxLayout(self)
    self.lbl = QLabel(
        "Вставьте диск с играми в привод...", alignment=Qt.AlignCenter
    )
    self.lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
    self.pbar = QProgressBar(range=(0, 10), value=0)
    self.l.addStretch()
    self.l.addWidget(self.lbl)
    self.l.addWidget(self.pbar)
    self.l.addStretch()
    self.t = QTimer(self)
    self.t.timeout.connect(self.tick)
    self.t.start(1000)

  def tick(self):
    self.sec -= 1
    self.pbar.setValue(10 - self.sec)
    if self.sec > 0:
      self.lbl.setText(f"Чтение диска... Осталось {self.sec} сек.")
    else:
      self.t.stop()
      self.show_menu()

  def show_menu(self):
    while self.l.count():
      w = self.l.takeAt(0).widget()
      if w:
        w.deleteLater()
    self.l.addWidget(
        QLabel(
            "Диск: «Такса-Сборник 8 в 1»",
            font=QFont("Segoe UI", 13, QFont.Bold),
            styleSheet="color:#FF4D94;",
        )
    )
    scroll = QScrollArea()
    cont = QWidget()
    cl = QVBoxLayout(cont)
    for g in GAMES_INFO:
      btn = QPushButton(f"Запустить: {g[1]}", objectName="ActionBtn")
      btn.clicked.connect(lambda _, gid=g[0]: (self.accept(), self.launch_cb(gid)))
      cl.addWidget(btn)
    scroll.setWidget(cont)
    scroll.setWidgetResizable(True)
    self.l.addWidget(scroll)
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
    disc_btn.clicked.connect(
        lambda: DiscDriveDialog(self, self.launch_game).exec()
    )
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
      il.addWidget(QLabel(g[1], font=QFont("Segoe UI", 14, QFont.Bold)))
      il.addWidget(QLabel(g[2], styleSheet="color:#B0B0C8;"))
      btn = QPushButton(f"Купить за {g[3]}", objectName="ActionBtn")
      btn.clicked.connect(lambda _, game=g, b=btn: self.buy_game(game, b))
      cl.addLayout(il)
      cl.addStretch()
      cl.addWidget(btn)
      l.addWidget(card)
    l.addStretch()
    scroll.setWidget(cont)
    return scroll

  def buy_game(self, g, btn):
    if self.balance >= g[3]:
      self.change_bal(-g[3])
      self.owned.add(g[0])
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
      if g[0] in self.owned:
        card = QFrame(objectName="GameCard")
        cl = QHBoxLayout(card)
        cl.addWidget(QLabel(g[1], font=QFont("Segoe UI", 14, QFont.Bold)))
        btn = QPushButton("Играть", objectName="ActionBtn")
        btn.clicked.connect(lambda _, gid=g[0]: self.launch_game(gid))
        cl.addStretch()
        cl.addWidget(btn)
        self.gl.addWidget(card)
    self.gl.addStretch()

  def launch_game(self, gid):
    g = next((x for x in GAMES_INFO if x[0] == gid), None)
    if not g:
      return
    try:
      mod = importlib.import_module(g[4])
      cls = getattr(mod, g[5])
      if g[6] == "fin":
        cls(self, on_finish=self.change_bal).exec()
      else:
        cls(
            self,
            get_balance=lambda: self.balance,
            change_balance=self.change_bal,
        ).exec()
    except Exception as e:
      QMessageBox.critical(
          self, "Ошибка запуска", f"Не удалось открыть {g[1]}:\n{e}"
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
