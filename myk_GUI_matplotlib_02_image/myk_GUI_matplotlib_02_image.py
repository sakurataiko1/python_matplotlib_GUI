import wx
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

matplotlib.use('WXAgg')
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

# Used to determine the size of an image
from PIL import Image

# ===================================
# ボタン押下で、画像ファイル読み込み　
#
# 参考
#    GUI配置、基本グラフ描画
#        コード-Github  https://github.com/nickredsox/youtube/tree/master/Arduino_Python_serial/Video2
#        動画-Youtube https://www.youtube.com/watch?v=KpTfdC5CILY&pp=ugMICgJqYRABGAE%3D
#
#    イメージ表示
#        コード： matplotlibのみ　https://qiita.com/ceptree/items/c547116bda4a5db11596　matplotlibだけで画像からマウスで指定した領域を抜き出す
# 　　　　　コード:  GUI wx+ matplotlib https://github.com/ashokfernandez/wxPython-Rectangle-Selector-Panel/blob/master/RectangleSelectorPanel.py
#
# ===================================

data = []


class TopPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.axes.set_xlabel("Time")
        self.axes.set_ylabel("A/D Counts")

    # LOOK AT THIS
    def draw(self, x, y):
        # -start- org-OK
        self.axes.clear()
        self.axes.plot(x, y)
        self.canvas.draw()
        # -end- org-OK

    def changeAxes(self, min, max):
        self.axes.set_ylim(float(min), float(max))
        self.canvas.draw()

    def setImage(self, pathToImage):
        '''Sets the background image of the canvas'''

        # Load the image into matplotlib and PIL
        image = matplotlib.image.imread(pathToImage)
        imPIL = Image.open(pathToImage)

        # Save the image's dimensions from PIL
        self.imageSize = imPIL.size

        # Add the image to the figure and redraw the canvas. Also ensure the aspect ratio of the image is retained.
        self.axes.imshow(image, aspect='equal')
        self.canvas.draw()

class BottomPanel(wx.Panel):
    def __init__(self, parent, top):
        wx.Panel.__init__(self, parent=parent)

        # GUI配置
        self.graph = top

        labelVal1 = wx.StaticText(self, -1, "value ", pos=(110, 10))
        self.textboxVal1 = wx.TextCtrl(self, -1, "1", pos=(150, 10))

        self.buttonPlot01 = wx.Button(self, -1, "test_Plot01", pos=(10, 10))
        self.buttonPlot01.Bind(wx.EVT_BUTTON, self.SetButtonPlot01_image)

    # 　GUIフォームに紐づけた関数指定
    def SetButtonPlot01_graphLinear(self, event):
        val1 = self.textboxVal1.GetValue()  # テキストボックスから値取得
        self.x = np.arange(0, 3, 0.01)
        self.y = self.x * int(val1);
        self.graph.draw(self.x, self.y)
        self.graph.changeAxes(0, 20)  # 軸固定する。　デフォルト動作で軸は描画グラフ最小・最大数値になってくれるが、グラフ変化をわかりやすくするため軸固定する。
        cb = event.GetEventObject()
        print("[DEBUG]SetButtonPlot01_graphLinear: %s is clicked" % (cb.GetLabel()))

    def SetButtonPlot01_image(self, event):
        self.graph.setImage('test.png')
        print("[DEBUG]SetButtonPlot01_graphLinear: %s is clicked" % (cb.GetLabel()))


class Main(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="GUI matplotlib", size=(600, 600))

        splitter = wx.SplitterWindow(self)
        top = TopPanel(splitter)
        bottom = BottomPanel(splitter, top)
        splitter.SplitHorizontally(top, bottom)
        splitter.SetMinimumPaneSize(400)
        top.draw([0], [0])


if __name__ == "__main__":
    app = wx.App()
    frame = Main()
    frame.Show()
    app.MainLoop()
