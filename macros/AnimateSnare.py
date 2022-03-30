# -*- coding: utf-8 -*-

from PySide import QtCore
import FreeCAD

timer = QtCore.QTimer()

def log(message):
  App.Console.PrintMessage(str(message) + '\n')

def get_spreadsheet(spreadsheet_label):
  return App.ActiveDocument.getObjectsByLabel(spreadsheet_label)[0]

def get_spreadsheet_value(spreadsheet_label, cell_key):
  return get_spreadsheet(spreadsheet_label).get(cell_key)

def update_spreadsheet_value(spreadsheet_label, cell_key, cell_value):
  sheet = get_spreadsheet(spreadsheet_label)
  sheet.set(cell_key, str(cell_value))
  sheet.recompute()
  App.ActiveDocument.recompute()
  Gui.updateGui()

def rotate_snare_knob(angle):
  update_spreadsheet_value('snare common', 'KnobCamAngle', angle)

def sig_int():
  if FreeCAD.ActiveDocument.Comment == 'p':
    log('snare animation paused')
    return 1

  if FreeCAD.ActiveDocument.Comment == 's':
    timer.stop()
    log('snare animation stopped')
    return 2

  return 0

def tick():
  if sig_int():
    return

  global angle
  angle = (angle + 10) % (rotation_range * 2)
  snare_knob_angle = 360 - abs(angle - rotation_range)

  rotate_snare_knob(snare_knob_angle)

def init_timer():
  timer.timeout.connect(tick)
  timer.start(40)
  log('snare animation started')

def prepare_env():
  global angle, rotation_range
  angle = get_spreadsheet_value('snare common', 'KnobCamAngle')
  rotation_range = 240
  FreeCAD.ActiveDocument.Comment = ''

def main():
  prepare_env()
  init_timer()

main()
