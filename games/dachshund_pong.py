import random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QDialog


class DachshundPongGame(QDialog):

  def __init__(self, parent=None, on_finish=None):
    super().__init__(parent)
    self.setWindowTitle("Такса-Арканоид (Dachshund Pong)")
    self.setFixedSize(520, 560)
    self.on_finish = on_finish
    self.keys = set()
    self.reset()

    self.timer = QTimer(self)
    self.timer.timeout.connect(self.tick)
    self.timer.start(16)

  def reset(self):
    self.px = 210.0
    self.bx, self.by = 260.0, 420.0
    self.vx = random.choice([-4.0, 4.0])
    self.vy = -4.5
    self.score = 0
    self.alive = True
    self.won = False

    # Сетка блоков: [x, y, w, h, color]
    colors = ["#FF4D94", "#9B5DE5", "#4DA6FF", "#FFAA00"]
    self.blocks = []
    for r in range(5):
      for c in range(8):
        self.blocks.append([22 + c * 60, 55 + r * 28, 54, 20, colors[r % 4]])

  def keyPressEvent(self, e):
    self.keys.add(e.key())
    if (not self.alive or self.won) and e.key() == Qt.Key_R:
      self.reset()

  def keyReleaseEvent(self, e):
    self.keys.discard(e.key())

  def tick(self):
    if not self.alive or self.won:
      return

    if Qt.Key_Left in self.keys or Qt.Key_A in self.keys:
      self.px = max(10, self.px - 8.0)
    if Qt.Key_Right in self.keys or Qt.Key_D in self.keys:
      self.px = min(410, self.px + 8.0)

    self.bx += self.vx
    self.by += self.vy

    if self.bx <= 8 or self.bx >= 512:
      self.vx *= -1
    if self.by <= 35:
      self.vy *= -1

    # Отскок от спины таксы
    if (
        self.vy > 0
        and 495 <= self.by + 8 <= 515
        and self.px - 5 <= self.bx <= self.px + 105
    ):
      self.vy = -abs(self.vy)
      offset = (self.bx - (self.px + 50)) / 50.0
      self.vx = offset * 6.0

    # Разбивание блоков
    for b in self.blocks[:]:
      if (
          b <= self.bx <= b + b
          and b <= self.by <= b + b
      ):
        self.blocks.remove(b)
        self.vy *= -1
        self.score += 10
        break

    if not self.blocks:
      self.won = True
      if self.on_finish:
        self.on_finish(self.score // 2 + 50)

    if self.by > 565:
      self.alive = False
      if self.on_finish:
        self.on_finish(max(5, self.score // 4))

    self.update()

  def paintEvent(self, e):
    qp = QPainter(self)
    qp.fillRect(self.rect(), QColor("#14141E"))

    qp.setPen(QColor("#FFFFFF"))
    qp.setFont(QFont("Segoe UI", 13, QFont.Bold))
    qp.drawText(15, 26, f"Очки: {self.score}   |   Блоков осталось: {len(self.blocks)}")

    qp.setPen(Qt.NoPen)
    for bx, by, bw, bh, col in self.blocks:
      qp.setBrush(QColor(col))
      qp.drawRoundedRect(bx, by, bw, bh, 5, 5)

    # Длинная такса-ракетка
    qp.setBrush(QColor("#8B4513"))
    qp.drawRoundedRect(int(self.px), 505, 100, 16, 8, 8)
    qp.drawEllipse(int(self.px + 85), 495, 22, 16)

    # Мячик
    qp.setBrush(QColor("#4DFF88"))
    qp.drawEllipse(int(self.bx - 8), int(self.by - 8), 16, 16)

    if not self.alive or self.won:
      qp.fillRect(self.rect(), QColor(0, 0, 0, 175))
      qp.setPen(QColor("#4DFF88") if self.won else QColor("#FF4D94"))
      qp.setFont(QFont("Segoe UI", 22, QFont.Bold))
      qp.drawText(165, 270, "ПОБЕДА!" if self.won else "МЯЧ УЛЕТЕЛ!")
      qp.setPen(QColor("#FFFFFF"))
      qp.setFont(QFont("Segoe UI", 13))
      reward = (self.score // 2 + 50) if self.won else max(5, self.score // 4)
      qp.drawText(145, 305, f"Награда: +{reward} монет (R - заново)")
