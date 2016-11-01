from Tkinter import Tk, Canvas, Toplevel

# NOTE - this will overwrite (but remember) existing drawings

class Grid:
  def __init__(self, width, height, side=25, title='Grid', background='grey'):
    tk = Tk()
    tk.withdraw()
    top = Toplevel(tk)
    top.wm_title(title)
    top.protocol('WM_DELETE_WINDOW', top.destroy)

    self.width = width
    self.height = height
    self.canvas = Canvas(top, width=self.width, height=self.height, background=background)
    self.canvas.pack()
    self.side = side
    self.cells = {}

  def transform_x(self, x):
    return self.side*x + self.width/2.

  def transform_y(self, y):
    return self.height - (self.side*y + self.height/2.) # Zero y is at the top

  def draw(self, (x, y), color='white'):
    self.delete((x, y))
    transformed_x = self.transform_x(x)
    transformed_y = self.transform_y(y)
    self.cells[(x, y)] = self.canvas.create_rectangle(transformed_x-self.side/2., transformed_y-self.side/2.,
                                                      transformed_x+self.side/2., transformed_y+self.side/2.,
                                                      fill=color, outline='black', width=2)

  def draw_vector(self, (x1, y1), (x2, y2), color='black'):
    #return self.canvas.create_line(self.transform_x(x1), self.transform_y(y1),
    #                               self.transform_x(x2), self.transform_y(y2),
    #                               tags=('arrow',), arrow='last', fill=color, width=2) # Tags let you change all elements at once
    return self.canvas.create_line((self.transform_x(x1) + self.transform_x(x2))/2, (self.transform_y(y1)+self.transform_y(y2))/2,
                                   self.transform_x(x2), self.transform_y(y2),
                                   tags=('arrow',), arrow='last', fill=color, width=2) # Tags let you change all elements at once

  def delete(self, (x, y)):
    if (x, y) in self.cells:
      self.canvas.delete(self.cells[(x, y)])

  def clear(self):
    self.canvas.delete('all')
