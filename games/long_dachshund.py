import random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QDialog

COLS, ROWS, CELL = 24, 24, 20


class LongDachshundGame(QDialog):

  def __init__(self, parent=None, on_finish=None):
    super().__init__(parent)
    self.setWindowTitle("Длинная Такса (Long Dachshund)")
    self.setFixedSize(COLS * CELL, ROWS * CELL + 40)
    self.on_finish = on_finish
    self.reset()

    self.timer = QTimer(self)
    self.timer.timeout.connect(self.tick)
    self.timer.start(105)

  def reset(self):
    self.snake = [(12, 12), (11, 12), (10, 12)]
    self.dir = (1, 0)
    self.next_dir = (1, 0)
    self.score = 0
    self.alive = True
    self.spawn_food()

  def spawn_food(self):
    free = [
        (x, y)
        for x in range(COLS)
        for y in range(ROWS)
        if (x, y) not in self.snake
    ]
    self.food = random.choice(free)
    self.golden = random.random() < 0.25

  def keyPressEvent(self, e):
    if not self.alive and e.key() == Qt.Key_R:
      self.reset()
      return
    k = e.key()
    if k in (Qt.Key_Up, Qt.Key_W) and self.dir != (0, 1):
      self.next_dir = (0, -1)
    elif k in (Qt.Key_Down, Qt.Key_S) and self.dir != (0, -1):
      self.next_dir = (0, 1)
    elif k in (Qt.Key_Left, Qt.Key_A) and self.dir != (1, 0):
      self.next_dir = (-1, 0)
    elif k in (Qt.Key_Right, Qt.Key_D) and self.dir != (-1, 0):
      self.next_dir = (1, 0)

  def tick(self):
    if not self.alive:
      return
    self.dir = self.next_dir
    hx, hy = self.snake[0]
    nx, ny = hx + self.dir[0], hy + self.dir[1]

    if not (0 <= nx < COLS and 0 <= ny < ROWS) or (nx, ny) in self.snake:
      self.alive = False
      if self.on_finish:
        self.on_finish(max(5, self.score * 3))
      self.update()
      return

    self.snake.insert(0, (nx, ny))
    if (nx, ny) == self.food:
      self.score += 3 if self.golden else 1
      self.spawn_food()
    else:
      self.snake.pop()

    self.update()

  def paintEvent(self, e):
    qp = QPainter(self)
    qp.fillRect(self.rect(), QColor("#14141E"))

    # Верхняя панель счёта
    qp.setPen(QColor("#FFFFFF"))
    qp.setFont(QFont("Segoe UI", 12, QFont.Bold))
    qp.drawText(12, 26, f"Длина таксы: {len(self.snake)}   |   Очки: {self.score}")

    # Граница поля
    qp.setPen(QColor("#323246"))
    qp.drawRect(0, 40, COLS * CELL - 1, ROWS * CELL - 1)
    qp.setPen(Qt.NoPen)

    # Еда
    fx, fy = self.food
    qp.setBrush(QColor("#FFAA00") if self.golden else QColor("#FF4D94"))
    qp.drawEllipse(fx * CELL + 3, fy * CELL + 43, CELL - 6, CELL - 6)

    # Тело и голова таксы
    for i, (sx, sy) in enumerate(self.snake):
      qp.setBrush(QColor("#A0522D") if i == 0 else QColor("#8B4513"))
      qp.drawRoundedRect(
          sx * CELL + 1, sy * CELL + 41, CELL - 2, CELL - 2, 5, 5
      )

    if not self.alive:
      qp.fillRect(0, 40, COLS * CELL, ROWS * CELL, QColor(0, 0, 0, 175))
      qp.setPen(QColor("#FF4D94"))
      qp.setFont(QFont("Segoe UI", 20, QFont.Bold))
      qp.drawText(155, 250, "ВРЕЗАЛСЯ!")
      qp.setPen(QColor("#FFFFFF"))
      qp.setFont(QFont("Segoe UI", 13))
      qp.drawText(
          115, 285, f"Награда: +{max(5, self.score * 3)} монет (R - заново)"
      )
