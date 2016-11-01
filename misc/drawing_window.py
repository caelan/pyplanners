from Tkinter import Tk, Canvas, Toplevel

class DrawingWindow:
    def __init__(self, width, height, x_min, x_max, y_min, y_max, title, parent=None):
      self.title = title
      if parent:
        self.parent = parent
        self.top = parent.getWindow(title)
      else:
        self.tk = Tk()
        self.tk.withdraw()
        self.top = Toplevel(self.tk)
        self.top.wm_title(title)
        self.top.protocol('WM_DELETE_WINDOW', self.top.destroy)
      self.window_width = width
      self.window_height = height
      self.canvas = Canvas(self.top, width=self.window_width, height=self.window_height, background="white")
      self.canvas.pack()

      self.x_scale = width / float(x_max - x_min) # multiply an input value by this to get pixels
      self.y_scale = height / float(y_max - y_min)

      self.x_min = x_min
      self.y_min = y_min
      self.x_max = x_max
      self.y_max = y_max

    def scale_x(self, x):
      return self.x_scale * (x - self.x_min)

    def scale_y(self, y):
      return self.window_height - self.y_scale * (y - self.y_min)

    def draw_point(self, x, y, color="blue", radius=1):
      window_x = self.scale_x(x)
      window_y = self.scale_y(y)
      return self.canvas.create_rectangle(window_x-radius, window_y-radius, window_x+radius,
                                   window_y+radius, fill=color, outline=color)

    def draw_text(self, x, y, label):
      return self.canvas.create_text(self.scale_x(x), self.scale_y(y), text=label)
      # font="Arial 20",fill="#ff0000"

    def draw_poly(self, verts, color="black", outline="black"):
      return self.canvas.create_polygon([(self.scale_x(point.x), self.scale_y(point.y)) for point in verts],
                                          fill=color,
                                          outline=outline)

    def draw_rect(self, (x1,y1), (x2,y2), color="black"):
      return self.canvas.create_rectangle(self.scale_x(x1), self.scale_y(y1),
                                          self.scale_x(x2), self.scale_y(y2),
                                          fill=color)

    def draw_oval(self, (x1,y1), (x2,y2), color="black"):
      return self.canvas.create_oval(self.scale_x(x1), self.scale_y(y1),
                                     self.scale_x(x2), self.scale_y(y2),
                                     fill=color)

    def draw_line_seg(self, x1, y1, x2, y2, color="black", width=2):
      return self.canvas.create_line(self.scale_x(x1),self.scale_y(y1),
                                     self.scale_x(x2),self.scale_y(y2),
                                     fill=color,
                                     width=width)

    def draw_unscaled_line_seg(self, x1, y1, xproj, yproj, color="black", width=1):
      return self.canvas.create_line(self.scale_x(x1),self.scale_y(y1),
                                     self.scale_x(x1)+xproj,self.scale_y(y1)-yproj,
                                     fill=color,
                                     width=width)

    def draw_unscaled_rect(self, x1, y1, xproj, yproj, color="black"):
      return self.canvas.create_rectangle(self.scale_x(x1)-xproj,
                                          self.scale_y(y1)+yproj,
                                          self.scale_x(x1)+xproj,
                                          self.scale_y(y1)-yproj,
                                          fill=color)

    def draw_line(self, (a,b,c), color="black"):
      if abs(b) < 0.001:
        start_x = self.scale_x(-c/a)
        start_y = self.scale_y(self.y_min)
        end_x = self.scale_x(-c/a)
        end_y = self.scale_y(self.y_max)
      else:
        start_x = self.scale_x(self.x_min)
        start_y = self.scale_y(- (a * self.x_min + c) / b)
        end_x = self.scale_x(self.x_max)
        end_y = self.scale_y(- (a * self.x_max + c) / b)
      return self.canvas.create_line(start_x, start_y, end_x, end_y, fill = color)

    def delete(self, thing):
      self.canvas.delete(thing)

    def clear(self):
      self.canvas.delete("all")
