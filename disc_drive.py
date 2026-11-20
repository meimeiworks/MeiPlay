from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

DISCS = [
    {
        "title": "Диск 1: Такса-Классика 2007",
        "games": [
            ("jump", "Прыгающая Такса"),
            ("dash", "Dachshund Dash"),
            ("pong", "Такса-Арканоид"),
        ],
    },
    {
        "title": "Диск 2: Сосисочный Беспредел",
        "games": [
            ("sniffe", "Sausage Sniffe 16x16"),
            ("catch", "Ловец Сосисок"),
            ("long", "Длинная Такса"),
        ],
    },
    {
        "title": "Диск 3: Азартные Таксы",
        "games": [("drop", "Такса-Дроп"), ("mines", "Такса-Сапёр")],
    },
]


class DiscDriveDialog(QDialog):

  def __init__(self, parent, launch_cb, owned_ids=None, all_games=None):
    super().__init__(parent)
    self.setWindowTitle("Привод MeiPlay UMD / DVD")
    self.setFixedSize(440, 340)
    self.launch_cb = launch_cb
    self.owned_ids = owned_ids or set()
    self.all_games = all_games or []
    self.burned_disc = None

    self.l = QVBoxLayout(self)
    self.l.setSpacing(12)
    self.show_tray()

  def clear_ui(self):
    while self.l.count():
      w = self.l.takeAt(0).widget()
      if w:
        w.deleteLater()

  def show_tray(self):
    self.clear_ui()
    lbl = QLabel("Лоток привода открыт. Выберите диск:", alignment=Qt.AlignCenter)
    lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
    self.l.addWidget(lbl)

    for disc in DISCS:
      btn = QPushButton(f"Вставить: {disc['title']}", objectName="ActionBtn")
      btn.clicked.connect(lambda _, d=disc: self.start_reading(d))
      self.l.addWidget(btn)

    if self.burned_disc:
      b_btn = QPushButton(
          f"Вставить: {self.burned_disc['title']}", objectName="ActionBtn"
      )
      b_btn.clicked.connect(lambda: self.start_reading(self.burned_disc))
      self.l.addWidget(b_btn)

    burn_btn = QPushButton("Записать свою болванку CD-R (из купленных игр)")
    burn_btn.setStyleSheet(
        "background:#252538; border:1px solid #FF4D94; padding:8px;"
        " border-radius:8px;"
    )
    burn_btn.clicked.connect(self.burn_cdr)
    self.l.addSpacing(8)
    self.l.addWidget(burn_btn)

  def burn_cdr(self):
    if not self.owned_ids:
      QMessageBox.warning(
          self, "Пусто", "Сначала купи хотя бы одну игру в Магазинчике!"
      )
      return
    my_list = [(g, g) for g in self.all_games if g in self.owned_ids]
    self.burned_disc = {
        "title": "CD-R: Мой Сборник MeiPlay",
        "games": my_list,
    }
    QMessageBox.information(
        self,
        "Запись завершена!",
        "Твой личный диск CD-R записан и готов к вставке!",
    )
    self.show_tray()

  def start_reading(self, disc):
    self.clear_ui()
    self.sec = 10
    self.current_disc = disc

    self.lbl = QLabel(
        f"Раскрутка привода: {disc['title']}...", alignment=Qt.AlignCenter
    )
    self.lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
    self.lbl.setWordWrap(True)
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
      self.lbl.setText(f"Чтение секторов диска... Осталось {self.sec} сек.")
    else:
      self.t.stop()
      self.show_disc_games()

  def show_disc_games(self):
    self.clear_ui()
    title = QLabel(self.current_disc["title"], alignment=Qt.AlignCenter)
    title.setFont(QFont("Segoe UI", 14, QFont.Bold))
    title.setStyleSheet("color:#FF4D94;")
    self.l.addWidget(title)

    for gid, gname in self.current_disc["games"]:
      btn = QPushButton(f"Запустить: {gname}", objectName="ActionBtn")
      btn.clicked.connect(lambda _, i=gid: (self.accept(), self.launch_cb(i)))
      self.l.addWidget(btn)

    eject = QPushButton("Извлечь диск")
    eject.clicked.connect(self.show_tray)
    self.l.addSpacing(10)
    self.l.addWidget(eject)
