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

    def __init__(self, parent, pathToImage=None):
        ''' Initialise the panel. Setting an initial image is optional.'''
        
        # Initialise the parent
        wx.Panel.__init__(self, parent)

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
        cb = event.GetEventObject()
        print("[DEBUG]SetButtonPlot01_graphLinear: %s is clicked" % (cb.GetLabel()))


class Main(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="GUI matplotlib", size=(600, 600))

        splitter = wx.SplitterWindow(self)
        top = TopPanel(splitter)
        bottom = BottomPanel(splitter, top)
        splitter.SplitHorizontally(top, bottom)
        splitter.SetMinimumPaneSize(400)
        top.setImage('test_none.jpg')

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