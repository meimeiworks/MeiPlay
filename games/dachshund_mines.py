import random
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class DachshundMinesGame(QDialog):

  def __init__(self, parent=None, get_balance=None, change_balance=None):
    super().__init__(parent)
    self.setWindowTitle("Такса-Сапёр: Охота за сосисками")
    self.setFixedSize(460, 540)
    self.get_balance = get_balance
    self.change_balance = change_balance

    self.bet = 25
    self.active = False
    self.mines = set()
    self.opened = 0

    self.setStyleSheet("""
            QDialog { background-color: #14141E; color: #F0F0F5; font-family: 'Segoe UI', Arial; }
            QPushButton#Tile {
                background-color: #222232; border: 1px solid #383850; border-radius: 8px;
                font-size: 16px; font-weight: bold; min-height: 58px;
            }
            QPushButton#Tile:hover { background-color: #2E2E44; }
            QPushButton#CtrlBtn {
                background-color: #FF4D94; color: white; border: none;
                border-radius: 8px; padding: 10px 16px; font-weight: bold;
            }
            QPushButton#CtrlBtn:hover { background-color: #FF6BA6; }
        """)

    l = QVBoxLayout(self)
    l.setSpacing(12)

    top = QHBoxLayout()
    self.bal_lbl = QLabel(f"Баланс: {self.get_balance()} монет")
    self.bal_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
    self.win_lbl = QLabel("Выигрыш: 0")
    self.win_lbl.setStyleSheet(
        "color: #4DFF88; font-weight: bold; font-size: 14px;"
    )
    top.addWidget(self.bal_lbl)
    top.addStretch()
    top.addWidget(self.win_lbl)
    l.addLayout(top)

    grid = QGridLayout()
    self.tiles = []
    for i in range(25):
      btn = QPushButton("?", objectName="Tile")
      btn.clicked.connect(lambda _, idx=i: self.click_tile(idx))
      grid.addWidget(btn, i // 5, i % 5)
      self.tiles.append(btn)
    l.addLayout(grid)

    ctrls = QHBoxLayout()
    self.start_btn = QPushButton(
        f"Играть (Ставка {self.bet})", objectName="CtrlBtn"
    )
    self.cash_btn = QPushButton("Забрать выигрыш", objectName="CtrlBtn")
    self.cash_btn.setEnabled(False)
    self.start_btn.clicked.connect(self.start_round)
    self.cash_btn.clicked.connect(self.cash_out)
    ctrls.addWidget(self.start_btn)
    ctrls.addWidget(self.cash_btn)
    l.addLayout(ctrls)

  def current_prize(self):
    if self.opened == 0:
      return 0
    return int(self.bet * (1.28**self.opened))

  def start_round(self):
    if self.get_balance() < self.bet:
      QMessageBox.warning(self, "Мало монет", "Не хватает монет для ставки!")
      return
    self.change_balance(-self.bet)
    self.bal_lbl.setText(f"Баланс: {self.get_balance()} монет")
    self.mines = set(random.sample(range(25), 5))
    self.opened = 0
    self.active = True
    self.win_lbl.setText("Выигрыш: 0")
    self.cash_btn.setEnabled(False)
    for b in self.tiles:
      b.setText("?")
      b.setEnabled(True)
      b.setStyleSheet("")

  def click_tile(self, idx):
    if not self.active:
      return
    btn = self.tiles[idx]
    btn.setEnabled(False)
    if idx in self.mines:
      self.active = False
      self.cash_btn.setEnabled(False)
      for i, b in enumerate(self.tiles):
        if i in self.mines:
          b.setText("БОМБА")
          b.setStyleSheet("background-color: #A82038; color: white;")
      self.win_lbl.setText("БАБАХ! Проигрыш")
    else:
      self.opened += 1
      btn.setText("СОСИСКА")
      btn.setStyleSheet("background-color: #246B43; color: white;")
      self.win_lbl.setText(f"Выигрыш: {self.current_prize()}")
      self.cash_btn.setEnabled(True)

  def cash_out(self):
    if not self.active or self.opened == 0:
      return
    prize = self.current_prize()
    self.active = False
    self.cash_btn.setEnabled(False)
    self.change_balance(prize)
    self.bal_lbl.setText(f"Баланс: {self.get_balance()} монет")
    QMessageBox.information(self, "Победа!", f"Ты забрал {prize} монет!")
