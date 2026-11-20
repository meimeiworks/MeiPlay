import random
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

GRID_SIZE = 16
CELL = 34
BONES_COUNT = 15
SAUSAGES_GOAL = 10


class SniffeCanvas(QWidget):

  def __init__(self, on_hud, on_win):
    super().__init__()
    self.setFixedSize(GRID_SIZE * CELL, GRID_SIZE * CELL)
    self.on_hud = on_hud
    self.on_win = on_win
    self.reset()

  def reset(self):
    cells = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
    picked = random.sample(cells, BONES_COUNT + SAUSAGES_GOAL)
    self.bones = set(picked[:BONES_COUNT])
    self.sausages = set(picked[BONES_COUNT:])
    self.found = set()
    self.opened = set()
    self.flags = set()
    self.over = False
    self.update()
    self.on_hud()

  def neighbors(self, x, y):
    for dx in (-1, 0, 1):
      for dy in (-1, 0, 1):
        nx, ny = x + dx, y + dy
        if (dx or dy) and 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
          yield (nx, ny)

  def bones_around(self, x, y):
    return sum(1 for n in self.neighbors(x, y) if n in self.bones)

  def nearest_dist(self, x, y):
    rem = self.sausages - self.found
    return min(abs(x - sx) + abs(y - sy) for sx, sy in rem) if rem else 0

  def reveal(self, x, y):
    stack = [(x, y)]
    while stack:
      cx, cy = stack.pop()
      if (cx, cy) in self.opened or (cx, cy) in self.flags:
        continue
      self.opened.add((cx, cy))
      if (cx, cy) in self.sausages:
        self.found.add((cx, cy))
      elif self.bones_around(cx, cy) == 0:
        for nx, ny in self.neighbors(cx, cy):
          if (nx, ny) not in self.opened and (nx, ny) not in self.bones:
            stack.append((nx, ny))

  def mousePressEvent(self, e):
    if self.over:
      return
    x, y = int(e.position().x() // CELL), int(e.position().y() // CELL)
    if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
      return

    if e.button() == Qt.RightButton:
      if (x, y) not in self.opened:
        self.flags.symmetric_difference_update({(x, y)})
      self.update()
      return

    if (x, y) in self.flags or (x, y) in self.opened:
      return

    if (x, y) in self.bones:
      self.over = True
      self.opened.update(self.bones)
      self.update()
      self.on_hud(lost=True)
      return

    self.reveal(x, y)
    dist = self.nearest_dist(x, y)
    self.update()

    if len(self.found) >= SAUSAGES_GOAL:
      self.over = True
      self.on_hud(dist=0)
      self.on_win()
    else:
      self.on_hud(dist=dist)

  def paintEvent(self, e):
    qp = QPainter(self)
    qp.setFont(QFont("Segoe UI", 12, QFont.Bold))
    for x in range(GRID_SIZE):
      for y in range(GRID_SIZE):
        rx, ry = x * CELL, y * CELL
        pos = (x, y)
        if pos in self.opened:
          if pos in self.bones:
            qp.fillRect(rx, ry, CELL - 2, CELL - 2, QColor("#C82333"))
            qp.setPen(QColor("#FFFFFF"))
            qp.drawText(rx + 10, ry + 23, "К")
          elif pos in self.sausages:
            qp.fillRect(rx, ry, CELL - 2, CELL - 2, QColor("#28A745"))
            qp.setPen(QColor("#FFFFFF"))
            qp.drawText(rx + 10, ry + 23, "С")
          else:
            qp.fillRect(rx, ry, CELL - 2, CELL - 2, QColor("#1A1A26"))
            cnt = self.bones_around(x, y)
            if cnt > 0:
              qp.setPen(QColor("#FF85B8"))
              qp.drawText(rx + 11, ry + 23, str(cnt))
        else:
          qp.fillRect(rx, ry, CELL - 2, CELL - 2, QColor("#2B2B3E"))
          if pos in self.flags:
            qp.setPen(QColor("#FFCC00"))
            qp.drawText(rx + 12, ry + 23, "!")


class SausageSniffeGame(QDialog):

  def __init__(self, parent=None, on_finish=None):
    super().__init__(parent)
    self.setWindowTitle("Sausage Sniffe")
    self.setFixedSize(575, 625)
    self.on_finish = on_finish
    self.setStyleSheet(
        "QDialog { background:#121218; color:#F0F0F5; font-family:'Segoe UI'; }"
        " QPushButton { background:#FF4D94; color:white; border:none;"
        " border-radius:8px; padding:8px 14px; font-weight:bold; }"
    )

    l = QVBoxLayout(self)
    top = QHBoxLayout()
    self.info_lbl = QLabel("Сосиски: 0/10 | Костей: 15")
    self.info_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
    self.radar_lbl = QLabel("Нюх: кликни клетку")
    self.radar_lbl.setStyleSheet("color:#4DFF88; font-weight:bold;")
    restart_btn = QPushButton("Заново")
    top.addWidget(self.info_lbl)
    top.addStretch()
    top.addWidget(self.radar_lbl)
    top.addWidget(restart_btn)
    l.addLayout(top)

    self.canvas = SniffeCanvas(self.update_hud, self.handle_win)
    l.addWidget(self.canvas, alignment=Qt.AlignCenter)
    restart_btn.clicked.connect(self.canvas.reset)

  def update_hud(self, dist=None, lost=False):
    if not hasattr(self, "canvas"):
      return
    self.info_lbl.setText(
        f"Сосиски: {len(self.canvas.found)}/{SAUSAGES_GOAL} | Костей:"
        f" {BONES_COUNT}"
    )
    if lost:
      self.radar_lbl.setText("ОЙ! Наступил на кость!")
      self.radar_lbl.setStyleSheet("color:#FF4D6D; font-weight:bold;")
    elif dist is not None:
      self.radar_lbl.setText(f"До сосиски: {dist} кл.")
      self.radar_lbl.setStyleSheet("color:#4DFF88; font-weight:bold;")

  def handle_win(self):
    if self.on_finish:
      self.on_finish(150)
    QMessageBox.information(
        self, "ПОБЕДА!", "Sausage Sniffe пройден! Награда: +150 монет!"
    )
