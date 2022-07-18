#
# 参考:  https://github.com/ashokfernandez/wxPython-Rectangle-Selector-Panel/blob/master/RectangleSelectorPanel.py
#
# Use the wxPython backend of matplotlib
import matplotlib       
matplotlib.use('WXAgg')

# Matplotlib elements used to draw the bounding rectangle
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

# wxPython stuff for the demo
import wx

# Used to determine the size of an image
from PIL import Image

# --------------------------------------------------------------------------------------------------------------------
# CLASSES
# --------------------------------------------------------------------------------------------------------------------

class TopPanel(wx.Panel):
    ''' Panel that contains an image that allows the users to select an area of the image with the mouse. The user clicks and
    holds the mouse to create a dotted rectangle, and when the mouse is released the rectangles origin, width and height can be
    read. The dimensions of these readings are always relative to the original image, so even if the image is scaled up larger
    to fit the panel the measurements will always refer to the original image.'''

    #def __init__(self, parent, pathToImage=None):
    def __init__(self, parent, in_objMain, pathToImage=None):
        #↑ 変更： Class TopからBottomに情報受け渡しできるようにするため、Mainを介する。
        ''' Initialise the panel. Setting an initial image is optional.'''
        
        # Initialise the parent
        wx.Panel.__init__(self, parent)

        #Class TopからBottomに情報受け渡しできるようにするため、Mainを介する。
        self.objMain = in_objMain

        # Intitialise the matplotlib figure
        self.figure = plt.figure()

        # Create an axes, turn off the labels and add them to the figure
        self.axes = plt.Axes(self.figure,[0,0,1,1])      
        self.axes.set_axis_off() 
        self.figure.add_axes(self.axes) 

        # Add the figure to the wxFigureCanvas
        self.canvas = FigureCanvas(self, -1, self.figure)

        # Initialise the rectangle
        self.rect = Rectangle((0,0), 1, 1, facecolor='None', edgecolor='green')
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.axes.add_patch(self.rect)
        
        # Sizer to contain the canvas
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 3, wx.ALL)
        self.SetSizer(self.sizer)
        self.Fit()
        
        # Connect the mouse events to their relevant callbacks
        self.canvas.mpl_connect('button_press_event', self._onPress)
        self.canvas.mpl_connect('button_release_event', self._onRelease)
        self.canvas.mpl_connect('motion_notify_event', self._onMotion)
        
        # Lock to stop the motion event from behaving badly when the mouse isn't pressed
        self.pressed = False

        # If there is an initial image, display it on the figure
        if pathToImage is not None:
            self.setImage(pathToImage)


    def _onPress(self, event):
        ''' Callback to handle the mouse being clicked and held over the canvas'''

        # Check the mouse press was actually on the canvas
        if event.xdata is not None and event.ydata is not None:

            # Upon initial press of the mouse record the origin and record the mouse as pressed
            self.pressed = True
            self.rect.set_linestyle('dashed')
            self.x0 = event.xdata
            self.y0 = event.ydata


    def _onRelease(self, event):
        '''Callback to handle the mouse being released over the canvas'''

        # Check that the mouse was actually pressed on the canvas to begin with and this isn't a rouge mouse 
        # release event that started somewhere else
        if self.pressed:

            # Upon release draw the rectangle as a solid rectangle
            self.pressed = False
            self.rect.set_linestyle('solid')

            # Check the mouse was released on the canvas, and if it wasn't then just leave the width and 
            # height as the last values set by the motion event
            if event.xdata is not None and event.ydata is not None:
                self.x1 = event.xdata
                self.y1 = event.ydata

            # Set the width and height and origin of the bounding rectangle
            self.boundingRectWidth =  self.x1 - self.x0
            self.boundingRectHeight =  self.y1 - self.y0
            self.bouningRectOrigin = (self.x0, self.y0)

            # Draw the bounding rectangle
            self.rect.set_width(self.boundingRectWidth)
            self.rect.set_height(self.boundingRectHeight)
            self.rect.set_xy((self.x0, self.y0))
            self.canvas.draw()

            #-start- myk TopPanelビューのマウス選択範囲座標を, BottomPanelのGUIのテキストフォームに座標値表示する
            print("[DEBUG]01 Top - onRelease")
            self.objMain.func_Main_setGUIBottomText01(self.x0, self.y0, self.x1, self.y1)
            #-end- myk

    def _onMotion(self, event):
        '''Callback to handle the motion event created by the mouse moving over the canvas'''

        # If the mouse has been pressed draw an updated rectangle when the mouse is moved so 
        # the user can see what the current selection is
        if self.pressed:

            # Check the mouse was released on the canvas, and if it wasn't then just leave the width and 
            # height as the last values set by the motion event
            if event.xdata is not None and event.ydata is not None:
                self.x1 = event.xdata
                self.y1 = event.ydata
            
            # Set the width and height and draw the rectangle
            self.rect.set_width(self.x1 - self.x0)
            self.rect.set_height(self.y1 - self.y0)
            self.rect.set_xy((self.x0, self.y0))
            self.canvas.draw()


    def setImage(self, pathToImage):
        '''Sets the background image of the canvas'''
        
        # Load the image into matplotlib and PIL
        image = matplotlib.image.imread(pathToImage) 
        imPIL = Image.open(pathToImage) 

        # Save the image's dimensions from PIL
        self.imageSize = imPIL.size
        
        # Add the image to the figure and redraw the canvas. Also ensure the aspect ratio of the image is retained.
        self.axes.imshow(image,aspect='equal') 
        self.canvas.draw()

class BottomPanel(wx.Panel):
    def __init__(self, parent, top):
        wx.Panel.__init__(self, parent=parent)

        # GUI配置
        self.graph = top

        #self.buttonPlot01 = wx.Button(self, -1, "Run Prot", pos=(10, 10))
        #self.buttonPlot01.Bind(wx.EVT_BUTTON, self.SetButtonPlot01_image)

        labelVal1 = wx.StaticText(self, -1, "filepath", pos=(10, 10))
        self.textboxVal1 = wx.TextCtrl(self, -1, "", pos=(50, 10), size=(200, 20))
        self.buttonSelect01 = wx.Button(self, -1, "select file", pos=(260, 10), size=(100,20))
        self.buttonSelect01.Bind(wx.EVT_BUTTON, self.func_ButtonSelect01_clicked)

        # topフォームのイメージビューでマウス選択された座標を表示する
        labelVal2 = wx.StaticText(self, -1, "view selected xy ", pos=(10, 50), size=(100,20))
        #self.buttonPlot02 = wx.Button(self, -1, "XY selected View", pos=(110, 50))
        #self.buttonPlot02.Bind(wx.EVT_BUTTON, self.SetButtonPlot02_getGraphSelect)
        self.textboxVal2 = wx.TextCtrl(self, -1, "0, 0, 0, 0", pos=(120, 50), size=(200,20))

    # 　GUIフォームに紐づけた関数指定
    #def SetButtonPlot01_image(self, event):
    #    self.graph.setImage('test.png')
    #    cb = event.GetEventObject()
    #    print("[DEBUG]SetButtonPlot01_graphLinear: %s is clicked" % (cb.GetLabel()))

    def SetButtonPlot02_getGraphSelect(self, event):
        tmpstr = "%.2f,.%.2f, %.2f, %.2f" % (self.graph.x0, self.graph.ｙ0, self.graph.x1, self.graph.y1)
        self.textboxVal2.SetValue(tmpstr)
        cb = event.GetEventObject()
        print("[DEBUG]SetButtonPlot02_getGraphSelect: %s is clicked" % (cb.GetLabel()))

    def func_ButtonSelect01_clicked(self, event):
        #ファイル選択して
        dialog = wx.FileDialog(self,"ファイルを選択",wildcard="画像ファイル|*.jpg;*.png|すべての形式|*.*",style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal()==wx.ID_OK:
            path01 = dialog.GetPath()
            self.textboxVal1.SetValue(path01)
            self.graph.setImage(path01)
            #↓テキストファイルを読み込む場合の処理
            #openfile = open(path,"r",encoding="UTF-8",errors="ignore")
            #self.textctrl.SetValue(openfile.read())
            #openfile.close()


class Main(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="GUI matplotlib", size=(600, 600))

        splitter = wx.SplitterWindow(self)
        #top = TopPanel(splitter)
        top = TopPanel(splitter, self) #変更 Class TopからBottomに情報受け渡しできるようにするため、Mainを介する。
        bottom = BottomPanel(splitter, top)
        splitter.SplitHorizontally(top, bottom)
        splitter.SetMinimumPaneSize(400)
        top.setImage('test_none.jpg')

        #-start- 変更 Class TopからBottomに情報受け渡しできるようにするため、Mainを介する。
        self.objBottom = bottom
        self.objTop = top
        # -end- 変更 Class TopからBottomに情報受け渡しできるようにするため

    def func_Main_test(self):
        print("[DEBUG]01 Main\n")
        self.objBottom.textboxVal1.SetValue("test_from_Main")

    def func_Main_setGUIBottomText01(self, x0, y0, x1, y1):
        # Class:TopPanelのビューでマウス選択された座標を、Class:BottomPanel テキストフォームに表示する。
        print("[DEBUG]01 Main\n")
        tmpstr = "%.2f,.%.2f, %.2f, %.2f" % (x0, ｙ0, x1, y1)
        self.objBottom.textboxVal2.SetValue(tmpstr)


# --------------------------------------------------------------------------------------------------------------------
# DEMO
# --------------------------------------------------------------------------------------------------------------------        

if __name__ == "__main__":

    # Create an demo application
    app = wx.App()

    # Create a frame and a RectangleSelectorPanel
    #fr = wx.Frame(None, title='test')
    fr = Main()
    #panel = TopPanel(fr)
    
    # Set the image in the panel
    #panel.setImage('images/Lenna.png')
    #panel.setImage('test.png')
    
    # Start the demo app
    fr.Show()
    app.MainLoop()