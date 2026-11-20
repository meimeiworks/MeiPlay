import math, random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPolygonF
from PySide6.QtWidgets import QDialog, QMessageBox


class DachshundJumpGame(QDialog):

  def __init__(self, parent=None, on_finish=None):
    super().__init__(parent)
    self.setWindowTitle("Прыгающая Такса")
    self.setFixedSize(460, 660)
    self.on_finish = on_finish
    self.keys = set()
    self.reset_game()

    self.timer = QTimer(self)
    self.timer.timeout.connect(self.update_game)
    self.timer.start(16)

  def reset_game(self):
    self.px, self.py = 200.0, 500.0
    self.vx, self.vy = 0.0, -11.0
    self.score, self.lava_y, self.angle = 0, 680.0, 0
    self.alive = True
    # [x, y, w, type: 0=обычная, 1=с шипами]
    self.plats = [[160, 560, 120, 0]]
    for i in range(1, 12):
      self.plats.append(
          [random.randint(20, 320), 560 - i * 65, 95, 1 if i % 4 == 0 else 0]
      )
    # [x, y, vx]
    self.saws = [[100, 260, 2.5], [300, 60, -3.0]]

  def keyPressEvent(self, e):
    self.keys.add(e.key())
    if not self.alive and e.key() == Qt.Key_R:
      self.reset_game()

  def keyReleaseEvent(self, e):
    self.keys.discard(e.key())

  def update_game(self):
    if not self.alive:
      return
    self.angle = (self.angle + 12) % 360

    # Движение влево-вправо
    if Qt.Key_Left in self.keys or Qt.Key_A in self.keys:
      self.vx = -6.5
    elif Qt.Key_Right in self.keys or Qt.Key_D in self.keys:
      self.vx = 6.5
    else:
      self.vx *= 0.8

    self.px = (self.px + self.vx) % 460
    self.vy += 0.42
    self.py += self.vy

    # Прыжки от платформ и проверка шипов
    if self.vy > 0:
      for p in self.plats:
        if p[0] - 35 < self.px < p[0] + p[2] and p[1] - 22 <= self.py <= p[1] + 8:
          if p[3] == 1 and p[0] + 25 < self.px + 20 < p[0] + p[2] - 25:
            self.game_over()
            return
          self.vy = -12.2

    # Камера поднимается вверх
    if self.py < 260:
      diff = 260 - self.py
      self.py = 260
      self.score += int(diff)
      self.lava_y += diff * 0.65
      for p in self.plats:
        p[1] += diff
      for s in self.saws:
        s[1] += diff

    # Генерация новых платформ и пил
    for p in self.plats:
      if p[1] > 670:
        p[0] = random.randint(20, 340)
        p[1] = min(pl[1] for pl in self.plats) - random.randint(58, 72)
        p[3] = 1 if random.random() < 0.25 else 0

    for s in self.saws:
      s[0] += s[2]
      if s[0] < 25 or s[0] > 435:
        s[2] *= -1
      if s[1] > 690:
        s[1] = -random.randint(80, 220)
        s[0] = random.randint(40, 420)
      if math.hypot(self.px + 22 - s[0], self.py + 10 - s[1]) < 26:
        self.game_over()
        return

    # Лава поднимается
    self.lava_y -= 1.15 + min(self.score / 5000, 1.5)
    if self.py + 20 >= self.lava_y or self.py > 660:
      self.game_over()

    self.update()

  def game_over(self):
    self.alive = False
    coins = max(5, self.score // 25)
    if self.on_finish:
      self.on_finish(coins)
    self.update()

  def paintEvent(self, e):
    qp = QPainter(self)
    qp.setRenderHint(QPainter.Antialiasing)
    qp.fillRect(self.rect(), QColor("#14141E"))

    # Платформы и шипы
    for x, y, w, ptype in self.plats:
      qp.setBrush(QColor("#3A3A52"))
      qp.setPen(Qt.NoPen)
      qp.drawRoundedRect(int(x), int(y), w, 12, 5, 5)
      if ptype == 1:
        qp.setBrush(QColor("#FF3B5C"))
        for sx in range(int(x) + 28, int(x) + w - 28, 12):
          qp.drawPolygon(
              [QPointF(sx, y), QPointF(sx + 6, y - 11), QPointF(sx + 12, y)]
          )

    # Пилы
    for sx, sy, _ in self.saws:
      qp.setBrush(QColor("#C8C8D8"))
      qp.drawEllipse(int(sx - 16), int(sy - 16), 32, 32)
      qp.setBrush(QColor("#FF4D94"))
      qp.drawEllipse(int(sx - 5), int(sy - 5), 10, 10)

    # Такса (длинное тело, голова, ухо, лапки)
    qp.setBrush(QColor("#8B4513"))
    qp.drawRoundedRect(int(self.px), int(self.py), 44, 16, 7, 7)
    qp.drawEllipse(int(self.px + 32), int(self.py - 8), 18, 16)
    qp.setBrush(QColor("#4E270B"))
    qp.drawEllipse(int(self.px + 30), int(self.py - 4), 8, 13)

    # Лава
    qp.setBrush(QColor(255, 65, 20, 210))
    qp.drawRect(0, int(self.lava_y), 460, 700)

    # Счёт
    qp.setPen(QColor("#FFFFFF"))
    qp.setFont(QFont("Segoe UI", 14, QFont.Bold))
    qp.drawText(15, 30, f"Высота: {self.score}")

    if not self.alive:
      qp.fillRect(self.rect(), QColor(0, 0, 0, 175))
      qp.setPen(QColor("#FF4D94"))
      qp.setFont(QFont("Segoe UI", 22, QFont.Bold))
      qp.drawText(120, 290, "ТАКСА ПОПАЛАСЬ!")
      qp.setPen(QColor("#FFFFFF"))
      qp.setFont(QFont("Segoe UI", 13))
      qp.drawText(115, 330, f"Награда: +{max(5, self.score // 25)} монет")
      qp.drawText(115, 360, "Нажми R чтобы сыграть снова")
