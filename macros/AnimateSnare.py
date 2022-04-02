# -*- coding: utf-8 -*-

import os
import glob
import FreeCAD
from PIL import Image
from pathlib import Path
from PySide import QtCore

timer = QtCore.QTimer()

def msg(message):
  App.Console.PrintMessage(str(message) + '\n')

def log(message):
  App.Console.PrintLog(str(message) + '\n')

def get_spreadsheet(spreadsheet_label):
  return App.ActiveDocument.getObjectsByLabel(spreadsheet_label)[0]

def get_spreadsheet_value(spreadsheet_label, cell_key):
  return get_spreadsheet(spreadsheet_label).get(cell_key)

def update_spreadsheet_value(spreadsheet_label, cell_key, cell_value):
  sheet = get_spreadsheet(spreadsheet_label)
  sheet.set(cell_key, str(cell_value))
  sheet.recompute()
  App.ActiveDocument.recompute()
  if not gif_mode:
    Gui.updateGui()

def rotate_snare_knob(angle):
  log('rotating snare knob to: ' + str(angle))
  update_spreadsheet_value('snare common', 'KnobCamAngle', angle)

def resolve_image_path(suffix = ''):
  project_path = Path(App.ActiveDocument.FileName)
  return project_path.parent.joinpath(
    'export', 'frames', (str(project_path.stem) + suffix + '.png')
  )

def capture_image(path):
  view = Gui.activeDocument().activeView()
  view.saveImage(
     str(path), 1562, 958, 'Current'
  )

def create_animation_frames(frames_dir):
  log('using frame images directory: ' + str(frames_dir))
  frames = []
  # collect all pngs from the frame images directory
  imgs = glob.glob(str(frames_dir / '*.png'))
  # append two lists - for backward and forward motion, to make a loopable gif
  imgs = sorted(imgs) + sorted(imgs, reverse=True)
  log('using frame images:')
  log(imgs)
  for i in imgs:
    new_frame = Image.open(i)
    frames.append(new_frame)
  return frames

def to_animated_gif(frames_dir):
  msg('creating an aminated gif...')
  frames = create_animation_frames(frames_dir)
  output_file = str(frames_dir.parent / 'cajon-snare-mechanism.gif')
  log('saving animated gif to: ' + str(output_file))
  frames[0].save(
    output_file,
    format='GIF',
    append_images=frames[1:],
    save_all=True,
    duration=40, # 40ms = 25fps
    loop=0, # loop forever
  )
  msg('animated gif saved to: ' + str(output_file))

def sig_int():
  if FreeCAD.ActiveDocument.Comment == 'p':
    msg('snare animation paused')
    return 1

  if FreeCAD.ActiveDocument.Comment == 's':
    timer.stop()
    msg('snare animation stopped')
    return 2

  return 0

def tick():
  global angle, gif_mode

  if sig_int():
    return

  snare_knob_angle = 360 - abs(angle - rotation_range)
  rotate_snare_knob(snare_knob_angle)

  if (gif_mode):
    snare_frame_image_path = resolve_image_path('-snare-frame-' + str(snare_knob_angle))
    capture_image(snare_frame_image_path)
    if (snare_knob_angle == 360):
      to_animated_gif(snare_frame_image_path.parent)
      timer.stop()

  angle = (angle + 10) % (rotation_range * 2)

def init_timer():
  timer.timeout.connect(tick)
  timer.start(40)
  msg('snare animation started')

def prepare_env():
  global angle, rotation_range, gif_mode

  gif_mode = False
  rotation_range = 240
  angle = get_spreadsheet_value('snare common', 'KnobCamAngle')

  if FreeCAD.ActiveDocument.Comment == 'gif':
    msg('gif mode')
    gif_mode = True
    angle = 0

  FreeCAD.ActiveDocument.Comment = ''

def main():
  prepare_env()
  init_timer()

main()
