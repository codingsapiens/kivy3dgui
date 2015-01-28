"""
The MIT License (MIT)
Copyright (c) 2015 Karel Piorno Charchabal
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from kivy.uix.floatlayout import FloatLayout
import kivy3dgui.canvas3d
from kivy3dgui.canvas3d import Canvas3D
import kivy3dgui.effectwidget
from kivy3dgui.effectwidget import BlurEffectWidget
from kivy3dgui.node import Node
from kivy.properties import BooleanProperty
from kivy.graphics import *


class Layout3D(FloatLayout):
    canvas3d = None
    post_processing = BooleanProperty(False)
    shadow = BooleanProperty(True)
    _nodes = []
    _init_request = [False, False]

    def __init__(self, **kwargs):
        super(Layout3D, self).__init__(**kwargs)
        #kivy3dgui.canvas3d.PICKING_BUFFER_SIZE = kwargs.get("canvas_size", (640, 480))
        #kivy3dgui.effectwidget.C_SIZE = kwargs.get("effect_canvas_size", (640, 480))

        with self.canvas.before:
            Color(1.0, 1.0, 1.0, 1.0)
            ClearColor(1.0, 1.0, 1.0, 1.0)

        #if the layout was defined with the kivy lang 3d canvas should be created after
        self.create_canvas()
        self.effect_widget = BlurEffectWidget(mask_effect=self.canvas3d.picking_fbo,
                                              motion_effect=self.canvas3d.motion_blur_fbo)

        if self._init_request[0]:
            self.post_processing = not self._init_request[1]
            self.post_processing = self._init_request[1]
        self._init_request[0] = True
        from kivy3dgui.canvas3d import label, label_debug
        label.parent = None
        try:
            self.add_widget(label)
            self.add_widget(label_debug)
        except Exception as w:
            pass

    def walk(self, value, time):
        self.canvas3d.walk(value, time)

    def strafe(self, value, time):
        self.canvas3d.strafe(value, time)

    def up(self, value, time):
        self.canvas3d.up(value, time)

    def create_canvas(self, *args):
        if self.canvas3d is None:
            self.canvas3d = Canvas3D(shadow=True, picking=True, size_hint=(1, 1))
            self.add_widget(self.canvas3d)
            self.canvas3d.size = self.size
            self.canvas3d.size_hint = self.size_hint

    def add_node(self, *args):
        self.canvas3d.add_node(args[0])

    def on_post_processing(self, widget, value):
        if not self._init_request[0]:
            self._init_request[0] = True
            self._init_request[1] = value
            return

        for children in self.children[:]:
            if isinstance(children, Canvas3D) or isinstance(children, BlurEffectWidget):
                self.remove_widget(children)

        for children in self.effect_widget.children[:]:
            self.effect_widget.remove_widget(children)
        if value:
            self.effect_widget.add_widget(self.canvas3d)
            self.effect_widget.effect_mask = self.canvas3d.picking_fbo
            self.add_widget(self.effect_widget, 100000)
        else:
            self.add_widget(self.canvas3d, 100000)

    def add_widget(self, *largs):
        widget = largs[0]

        if isinstance(widget, Node):
            print(widget.fbo_widget)
            float_str = str(self.canvas3d.current_id)[0:4]
            self.canvas3d.fbo_list[float_str] = widget.fbo_widget
            widget.pick_id = self.canvas3d.current_id

            if widget._start_objs:
                self.add_node(widget)
            else:
                widget.parent = self.canvas3d
                try:
                    self._nodes.append(widget.__self__)
                    #Check kivy version
                except:
                    self._nodes.append(widget)

            self.canvas3d.add_widget(widget.fbo_widget)
            #self.add_widget(widget.fbo_widget)
            self.canvas3d.current_id += 0.02
            self.canvas3d.current_id = round(self.canvas3d.current_id, 2)
        else:
            ret = super(Layout3D, self).add_widget(*largs)
            return ret
