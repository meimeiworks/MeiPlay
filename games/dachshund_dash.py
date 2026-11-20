import random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QDialog


class DachshundDashGame(QDialog):

  def __init__(self, parent=None, on_finish=None):
    super().__init__(parent)
    self.setWindowTitle("Dachshund Dash 2007")
    self.setFixedSize(640, 320)
    self.on_finish = on_finish
    self.reset()

    self.timer = QTimer(self)
    self.timer.timeout.connect(self.tick)
    self.timer.start(16)

  def reset(self):
    self.y = 220.0
    self.vy = 0.0
    self.duck = False
    self.score = 0
    self.speed = 6.5
    self.alive = True
    self.obs = [
        {"x": 650.0, "w": 24, "h": 38, "bird": False},
        {"x": 950.0, "w": 34, "h": 24, "bird": True},
    ]

  def keyPressEvent(self, e):
    if not self.alive and e.key() == Qt.Key_R:
      self.reset()
      return
    if e.key() in (Qt.Key_Space, Qt.Key_Up, Qt.Key_W) and self.y >= 220:
      self.vy = -11.5
    elif e.key() in (Qt.Key_Down, Qt.Key_S):
      self.duck = True

  def keyReleaseEvent(self, e):
    if e.key() in (Qt.Key_Down, Qt.Key_S):
      self.duck = False

  def tick(self):
    if not self.alive:
      return
    self.score += 1
    self.speed = 6.5 + min(self.score / 500, 7.0)

    self.vy += 0.65
    self.y = min(220.0, self.y + self.vy)

    dh = 12 if self.duck else 22
    dy = self.y + (22 - dh)
    dx, dw = 60, 52

    for o in self.obs:
      o["x"] -= self.speed
      if o["x"] < -50:
        o["x"] = 660.0 + random.randint(0, 220)
        is_bird = random.random() < 0.35 and self.score > 200
        o["bird"] = is_bird
        o["w"] = 34 if is_bird else random.randint(20, 32)
        o["h"] = 22 if is_bird else random.randint(28, 44)

      oy = 192 if o["bird"] else (242 - o["h"])
      if (
          dx < o["x"] + o["w"] - 4
          and dx + dw > o["x"] + 4
          and dy < oy + o["h"] - 4
          and dy + dh > oy + 4
      ):
        self.alive = False
        if self.on_finish:
          self.on_finish(max(5, self.score // 40))

    self.update()

  def paintEvent(self, e):
    qp = QPainter(self)
    qp.fillRect(self.rect(), QColor("#14141E"))

    qp.setPen(QColor("#FF4D94"))
    qp.drawLine(0, 244, 640, 244)

    dh = 12 if self.duck else 22
    dy = int(self.y + (22 - dh))
    qp.setBrush(QColor("#8B4513"))
    qp.setPen(Qt.NoPen)
    qp.drawRoundedRect(60, dy, 52, dh, 6, 6)
    qp.drawEllipse(100, dy - 6, 18, 15)

    for o in self.obs:
      oy = 192 if o["bird"] else (242 - o["h"])
      qp.setBrush(QColor("#FFAA00") if o["bird"] else QColor("#FF3B5C"))
      qp.drawRoundedRect(int(o["x"]), int(oy), o["w"], o["h"], 5, 5)

    qp.setPen(QColor("#FFFFFF"))
    qp.setFont(QFont("Segoe UI", 13, QFont.Bold))
    qp.drawText(20, 30, f"Дистанция: {self.score}")

    if not self.alive:
      qp.fillRect(self.rect(), QColor(0, 0, 0, 170))
      qp.setPen(QColor("#FF4D94"))
      qp.setFont(QFont("Segoe UI", 20, QFont.Bold))
      qp.drawText(210, 140, "ВРЕЗАЛСЯ!")
      qp.setPen(QColor("#FFFFFF"))
      qp.setFont(QFont("Segoe UI", 13))
      qp.drawText(
          195, 175, f"Награда: +{max(5, self.score // 40)} монет (R - заново)"
      )
