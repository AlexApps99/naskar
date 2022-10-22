from .gpt import complete
from .clean import clean
from .social import Social
from .render import Render
import json
import base64
import sys
from PIL.ImageQt import ImageQt
from PyQt6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QStatusBar, QLineEdit, QPlainTextEdit, QPushButton, QListView, QVBoxLayout, QWidget, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize

class MainWindow(QMainWindow):
  def __init__(self):
    super(MainWindow, self).__init__()
    self.setWindowTitle("Counterfeit Abhijit")

    with open("keys.json", "rb") as f:
      self.keys = json.load(f)

    layout = QVBoxLayout()

    self.title_box = QLineEdit()
    self.title_box.setPlaceholderText("Title")
    self.title_box.textChanged.connect(self.ready_to_generate)

    self.prompt_box = QPlainTextEdit()
    self.prompt_box.setPlaceholderText("Write a sonnet about mayonnaise:")
    self.prompt_box.setTabChangesFocus(True)
    self.prompt_box.textChanged.connect(self.ready_to_generate)

    self.gen_btn = QPushButton("Generate")
    self.gen_btn.setDisabled(True)
    self.gen_btn.clicked.connect(self.generate)

    self.img_row = QListWidget()
    self.img_row.setFlow(QListWidget.Flow.LeftToRight)
    self.img_row.setIconSize(QSize(256, 256))
    self.img_row.itemSelectionChanged.connect(self.ready_to_upload)

    self.up_btn = QPushButton("Upload")
    self.up_btn.setDisabled(True)
    self.up_btn.clicked.connect(self.upload)

    layout.addWidget(self.title_box)
    layout.addWidget(self.prompt_box)
    layout.addWidget(self.gen_btn)
    layout.addWidget(self.img_row)
    layout.addWidget(self.up_btn)

    widget = QWidget()
    widget.setLayout(layout)
    self.setCentralWidget(widget)

    self.title = ""
    self.prompt = ""
    self.gpt = None
    self.sonnets = []
    self.render = Render("templates.json")
    self.social = Social(self.keys)
    self.idx = -1
    self.imgs = []

  def generate(self):
    self.title = self.title_box.text().strip()
    self.prompt = self.prompt_box.toPlainText().strip()
    if self.title and self.prompt:
      self.prompt += "\n\n"
      self.gpt = complete(self.prompt, self.keys["openai"])
      self.sonnets = clean(self.gpt)
      self.img_row.clear()
      self.imgs = [self.render.generate(self.title, sonnet) for sonnet in self.sonnets]
      for i, img in enumerate(self.imgs):
        w = QListWidgetItem(QIcon(QPixmap.fromImage(ImageQt(img))), str(i))
        self.img_row.addItem(w)

  def ready_to_generate(self):
    v = bool(self.title_box.text().strip()) and bool(self.prompt_box.toPlainText().strip())
    self.gen_btn.setEnabled(v)
    self.ready_to_upload()
    return v

  def ready_to_upload(self):
    idxs = self.img_row.selectedIndexes()
    v = False
    if len(idxs) == 1:
      self.idx = idxs[0].row()
      v = True
    self.up_btn.setEnabled(v)
    return v

  def upload(self):
    img = Render.encode(self.imgs[self.idx], "png")
    try:
      with open("log.json", "x") as f:
        f.write("[]")
    except FileExistsError:
      pass

    with open("log.json", "r+") as f:
      j = json.load(f)
      j.append({
        "title": self.title,
        "prompt": self.prompt,
        "gpt": self.gpt,
        "sonnets": self.sonnets,
        "idx": self.idx,
        # TODO this is bad for disk space
        "img": "data:image/png;base64," + base64.b64encode(img).decode("utf-8")
      })
      f.seek(0)
      json.dump(j, f, indent=2)
      f.truncate()

    self.social.upload(self.title, self.sonnets[self.idx], img)


if __name__ == "__main__":
  app = QApplication(sys.argv)
  w = MainWindow()
  w.show()
  app.exec()

