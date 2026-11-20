import random
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

RARITIES = [
    ("Обычная Такса", "#A0A0B8", 15, 55, 25),
    ("Редкая Такса", "#4DA6FF", 45, 27, 18),
    ("Эпическая Кибер-Такса", "#B84DFF", 130, 12, 12),
    ("Легендарная Такса Милка", "#FFAA00", 400, 5, 8),
    ("МИФИЧЕСКАЯ ЗОЛОТАЯ ТАКСА", "#FF4D94", 1500, 1, 0),
]


class DachshundDropGame(QDialog):

  def __init__(self, parent=None, get_balance=None, change_balance=None):
    super().__init__(parent)
    self.setWindowTitle("Такса-Дроп: Карточки и Крафт")
    self.setFixedSize(500, 560)
    self.get_balance = get_balance
    self.change_balance = change_balance
    self.inventory = []

    self.setStyleSheet("""
            QDialog { background-color: #14141E; color: #F0F0F5; font-family: 'Segoe UI', Arial; }
            QListWidget { background-color: #1E1E2A; border: 1px solid #323246; border-radius: 10px; padding: 6px; font-size: 14px; }
            QPushButton { background-color: #FF4D94; color: white; border: none; border-radius: 8px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #FF6BA6; }
        """)

    l = QVBoxLayout(self)
    l.setSpacing(12)

    self.bal_lbl = QLabel(f"Баланс: {self.get_balance()} монет")
    self.bal_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
    l.addWidget(self.bal_lbl)

    self.drop_lbl = QLabel("Нажми кнопку ниже, чтобы открыть коробку с таксой!")
    self.drop_lbl.setAlignment(Qt.AlignCenter)
    self.drop_lbl.setStyleSheet(
        "background:#1E1E2A; padding:14px; border-radius:10px;"
        " font-weight:bold;"
    )
    l.addWidget(self.drop_lbl)

    open_btn = QPushButton("Открыть дроп за 30 монет")
    open_btn.clicked.connect(self.open_box)
    l.addWidget(open_btn)

    l.addWidget(QLabel("Твои карточки такс:"))
    self.inv_list = QListWidget()
    l.addWidget(self.inv_list)

    btns = QHBoxLayout()
    sell_btn = QPushButton("Продать выбранную")
    up_btn = QPushButton("Улучшить (Шанс!)")
    sell_btn.clicked.connect(self.sell_card)
    up_btn.clicked.connect(self.upgrade_card)
    btns.addWidget(sell_btn)
    btns.addWidget(up_btn)
    l.addLayout(btns)

  def update_ui(self):
    self.bal_lbl.setText(f"Баланс: {self.get_balance()} монет")
    self.inv_list.clear()
    for r_idx in self.inventory:
      name, color, price, _, chance = RARITIES[r_idx]
      txt = f"{name}  |  Цена: {price}  |  Шанс апгрейда: {chance}%"
      item = QListWidgetItem(txt)
      item.setForeground(QColor(color))
      self.inv_list.addItem(item)

  def open_box(self):
    if self.get_balance() < 30:
      QMessageBox.warning(self, "Мало монет", "Нужно 30 монет для дропа!")
      return
    self.change_balance(-30)
    weights = [r[3] for r in RARITIES]
    r_idx = random.choices(range(len(RARITIES)), weights=weights, k=1)[0]
    self.inventory.append(r_idx)
    name, color, _, _, _ = RARITIES[r_idx]
    self.drop_lbl.setText(f"Выпала: {name}!")
    self.drop_lbl.setStyleSheet(
        f"background:#1E1E2A; color:{color}; padding:14px; border-radius:10px;"
        " font-size:15px; font-weight:bold;"
    )
    self.update_ui()

  def sell_card(self):
    row = self.inv_list.currentRow()
    if row < 0:
      return
    r_idx = self.inventory.pop(row)
    price = RARITIES[r_idx][2]
    self.change_balance(price)
    self.update_ui()

  def upgrade_card(self):
    row = self.inv_list.currentRow()
    if row < 0:
      return
    r_idx = self.inventory[row]
    chance = RARITIES[r_idx][4]
    if chance == 0:
      QMessageBox.information(
          self, "Максимум", "Это уже максимальная редкость!"
      )
      return
    if random.randint(1, 100) <= chance:
      self.inventory[row] = r_idx + 1
      new_name = RARITIES[r_idx + 1][0]
      QMessageBox.information(
          self, "УСПЕХ!", f"Карточка улучшена до: {new_name}!"
      )
    else:
      self.inventory.pop(row)
      QMessageBox.warning(
          self, "Неудача...", "Улучшение сорвалось, карточка сгорела!"
      )
    self.update_ui()
