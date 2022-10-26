from .guts import SonnetGuts

from PIL.ImageQt import ImageQt
from PyQt6.QtWidgets import (
  QLineEdit, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget, QListWidget, QListWidgetItem,
  QDialog, QDialogButtonBox, QProgressDialog, QComboBox, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QColorConstants
from PyQt6.QtCore import QSize, Qt
import threading

class MainWindow(QWidget):
  '''
  Sonnet generation/upload window
  '''

  def __init__(self, title="", prompt="Write a sonnet:", gen_on_open=False):
    super().__init__()
    self.guts = SonnetGuts()

    layout = QVBoxLayout()

    self.title_box = QLineEdit(title)
    self.title_box.setPlaceholderText("Dreaming of mayonnaise")
    self.title_box.textChanged.connect(self.check_buttons_enabled)

    self.prompt_box = QPlainTextEdit(prompt)
    self.prompt_box.setPlaceholderText("Write a sonnet about mayonnaise:")
    self.prompt_box.setTabChangesFocus(True)
    self.prompt_box.textChanged.connect(self.check_buttons_enabled)

    self.gen_btn = QPushButton("Generate")
    self.gen_btn.setDisabled(True)
    self.gen_btn.clicked.connect(self.generate)

    self.img_row = QListWidget()
    self.img_row.setFlow(QListWidget.Flow.LeftToRight)
    self.img_row.setIconSize(QSize(256, 256))
    self.img_row.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
    self.img_row.setHorizontalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
    self.img_row.setResizeMode(QListWidget.ResizeMode.Adjust)
    self.img_row.setWrapping(True)
    self.img_row.itemSelectionChanged.connect(self.check_buttons_enabled)
    self.img_row.itemDoubleClicked.connect(self.edit_sonnet)
    self.dirty_col = QColorConstants.Red

    self.up_btn = QPushButton("Upload")
    self.up_btn.setDisabled(True)
    self.up_btn.clicked.connect(self.upload)

    layout.addWidget(self.title_box)
    layout.addWidget(self.prompt_box)
    layout.addWidget(self.gen_btn)
    layout.addWidget(self.img_row)
    layout.addWidget(self.up_btn)

    self.setLayout(layout)

    self.data = None
    self.idx = -1

    if gen_on_open:
      self.generate()

  def generate(self):
    '''
    Generate and render a new set of sonnets
    '''
    prompt = self.prompt_box.toPlainText()
    title = self.title_box.text()
    def blop_fn():
      # TODO bugs could lurk here
      self.data = self.guts.gen_sonnets(title, prompt)
    blop = BlockingOp(self, "Generating sonnets", blop_fn)
    blop.exec()
    if blop.exception:
      err = ExceptionPopup(self, exception=blop.exception)
      err.exec()
    elif self.data:
      self.refresh_images()
      return True
    return False

  def refresh_images(self):
    '''
    Re-render the image row
    '''

    self.guts.render_sonnets(self.data)
    self.idx = -1
    self.img_row.clear()
    for sonnet in self.data["sonnets"]:
      w = QListWidgetItem(QIcon(QPixmap.fromImage(ImageQt(sonnet["image"]))), None)
      w.setToolTip(sonnet["text"])
      if not sonnet["clean"]:
        w.setBackground(self.dirty_col)
      self.img_row.addItem(w)

  def check_buttons_enabled(self):
    '''
    Enables buttons when the input data seems valid
    '''
    v1 = bool(self.title_box.text().strip()) and bool(self.prompt_box.toPlainText().strip())
    self.gen_btn.setEnabled(v1)

    idxs = self.img_row.selectedIndexes()
    v2 = False
    if len(idxs) == 1:
      self.idx = idxs[0].row()
      v2 = True
    self.up_btn.setEnabled(v2)

    return (v1, v2)

  def upload(self):
    '''
    Uploads the selected sonnet from the image row
    '''
    def blop_fn():
      return self.guts.upload_sonnet(self.data, self.idx)
    blop = BlockingOp(self, "Uploading sonnet", blop_fn)
    blop.exec()
    if blop.return_v or blop.exception:
      if blop.return_v:
        err = ExceptionPopup(self, "Upload errors", "\n\n".join([f"{name}:\n{e}" for name, e in blop.return_v]))
      else:
        err = ExceptionPopup(self, "Upload errors", exception=blop.exception)
      err.exec()

  def edit_sonnet(self):
    '''
    Runs the sonnet editor for the currently selected sonnet
    '''
    se = SonnetEditor(self, self.idx)
    se.exec()

class SonnetEditor(QDialog):
  '''
  Sonnet editing dialog
  '''

  def __init__(self, parent, idx):
    '''
    Parent (MainWindow) and index of sonnet being edited
    '''
    super().__init__(parent)

    self.parent_ob = parent
    self.idx = idx
    self.setWindowTitle("Sonnet Editor")

    self.title_box = QLineEdit(parent.data["sonnets"][idx]["title"])

    self.text = QPlainTextEdit(parent.data["sonnets"][idx]["text"])
    self.text.setTabChangesFocus(True)

    self.templates = QComboBox()
    for templ in parent.guts.templates:
      self.templates.addItem(templ)
    self.templates.setCurrentText(parent.data["sonnets"][idx]["template"])

    self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Cancel)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    self.button_box.clicked.connect(self.click_evt)
    self.accepted.connect(self.apply_changes)

    self.layout = QVBoxLayout()
    self.layout.addWidget(self.title_box)
    self.layout.addWidget(self.text)
    self.layout.addWidget(self.templates)
    self.layout.addWidget(self.button_box)
    self.setLayout(self.layout)

  def apply_changes(self):
    '''
    Apply the changes to the parent
    '''
    self.parent_ob.data["sonnets"][self.idx]["title"] = self.title_box.text()
    self.parent_ob.data["sonnets"][self.idx]["text"] = self.text.toPlainText()
    self.parent_ob.data["sonnets"][self.idx]["template"] = self.templates.currentText()
    self.parent_ob.refresh_images()

  def click_evt(self, btn):
    '''
    Apply button
    '''
    if self.button_box.buttonRole(btn) == QDialogButtonBox.ButtonRole.ApplyRole:
      self.apply_changes()

class BlockingOp(QProgressDialog):
  '''
  Run blocking operation without freezing Qt
  '''

  def __init__(self, parent, label, fn, *args, **kwargs):
    self.exception = None
    self.return_v = None
    super().__init__(label, None, 0, 0, parent)
    def new_fn():
      try:
        self.return_v = fn(*args, **kwargs)
        print(self.return_v)
      except Exception as e:
        self.exception = e
      self.reset()
    self.thread = threading.Thread(target=new_fn)
    self.thread.start()

class ExceptionPopup(QMessageBox):
  '''
  Show error as a popup
  '''

  def __init__(self, parent, text="", info="", exception=None):
    super().__init__(QMessageBox.Icon.Critical, "Error", "", parent=parent)
    self.setTextFormat(Qt.TextFormat.PlainText)
    if exception:
      self.setText(text if text else "Exception occured")
      self.setInformativeText(info if info else str(exception))
    else:
      self.setText(text)
      self.setInformativeText(info)

