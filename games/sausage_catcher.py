import random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QDialog


class SausageCatcherGame(QDialog):

  def __init__(self, parent=None, on_finish=None):
    super().__init__(parent)
    self.setWindowTitle("Ловец Сосисок (Sausage Catcher)")
    self.setFixedSize(480, 580)
    self.on_finish = on_finish
    self.keys = set()
    self.reset()

    self.timer = QTimer(self)
    self.timer.timeout.connect(self.tick)
    self.timer.start(16)

  def reset(self):
    self.px = 210.0
    self.score = 0
    self.lives = 3
    self.alive = True
    # [x, y, speed, kind: 0=сосиска, 1=шоколад Милка, 2=колючка]
    self.items = []
    self.spawn_timer = 0

  def keyPressEvent(self, e):
    self.keys.add(e.key())
    if not self.alive and e.key() == Qt.Key_R:
      self.reset()

  def keyReleaseEvent(self, e):
    self.keys.discard(e.key())

  def tick(self):
    if not self.alive:
      return

    if Qt.Key_Left in self.keys or Qt.Key_A in self.keys:
      self.px = max(10, self.px - 7.5)
    if Qt.Key_Right in self.keys or Qt.Key_D in self.keys:
      self.px = min(410, self.px + 7.5)

    self.spawn_timer += 1
    if self.spawn_timer >= max(18, 40 - self.score // 5):
      self.spawn_timer = 0
      r = random.random()
      kind = 2 if r < 0.30 else (1 if r < 0.45 else 0)
      spd = 3.5 + min(self.score / 25, 5.0) + random.uniform(0, 1.5)
      self.items.append([random.randint(20, 440), -20.0, spd, kind])

    for it in self.items[:]:
      it += it
      # Проверка столкновения с таксой
      if (
          self.px - 15 < it < self.px + 65
          and 500 <= it <= 545
      ):
        if it == 2:
          self.lives -= 1
        elif it == 1:
          self.score += 3
        else:
          self.score += 1
        self.items.remove(it)
      elif it > 590:
        if it != 2:
          self.lives -= 1
        self.items.remove(it)

    if self.lives <= 0:
      self.alive = False
      if self.on_finish:
        self.on_finish(max(5, self.score * 2))

    self.update()

  def paintEvent(self, e):
    qp = QPainter(self)
    qp.fillRect(self.rect(), QColor("#14141E"))

    # Такса с миской
    qp.setBrush(QColor("#8B4513"))
    qp.setPen(Qt.NoPen)
    qp.drawRoundedRect(int(self.px), 520, 60, 18, 8, 8)
    qp.drawEllipse(int(self.px + 45), 510, 20, 16)

    # Падающие предметы
    for x, y, _, kind in self.items:
      if kind == 0:
        qp.setBrush(QColor("#FF6B6B"))
        qp.drawRoundedRect(int(x), int(y), 14, 24, 6, 6)
      elif kind == 1:
        qp.setBrush(QColor("#9B5DE5"))
        qp.drawRoundedRect(int(x), int(y), 20, 20, 4, 4)
      else:
        qp.setBrush(QColor("#FF3B5C"))
        qp.drawEllipse(int(x), int(y), 20, 20)

    qp.setPen(QColor("#FFFFFF"))
    qp.setFont(QFont("Segoe UI", 13, QFont.Bold))
    qp.drawText(15, 30, f"Очки: {self.score}   |   Жизни: {'♥ ' * max(0, self.lives)}")

    if not self.alive:
      qp.fillRect(self.rect(), QColor(0, 0, 0, 175))
      qp.setPen(QColor("#FF4D94"))
      qp.setFont(QFont("Segoe UI", 20, QFont.Bold))
      qp.drawText(150, 260, "ИГРА ОКОНЧЕНА!")
      qp.setPen(QColor("#FFFFFF"))
      qp.setFont(QFont("Segoe UI", 13))
      qp.drawText(130, 295, f"Награда: +{max(5, self.score * 2)} монет (R - заново)")
