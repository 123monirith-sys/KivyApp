from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.lang import Builder
from kivy.core.window import Window

import time, socket, json, threading


# Load KV file
Builder.load_file("my.kv")


def normalize_joystick(value):
    return int((value )/327.67) 
    


class x5_lite:
    def __init__(self, send_callback):
        self.send_callback = send_callback
        self.data ={
            'rx': 0.0,
            'ry': 0.0,
            'lx': 0.0,
            'ly': 0.0,
            'btn': 0x00000000000000000,
            'btnM': 0x0000000000000,
            
        }
        Window.bind(on_joy_axis=self.on_joy_axis)
        Window.bind(on_joy_button_down=self.on_button_down)
        Window.bind(on_joy_button_up=self.on_button_up)
        Window.bind(on_joy_hat=self.on_hat)
    def on_joy_axis(self, win, stickid, axisid, value):
        val= normalize_joystick( value);
        if axisid == 0: self.data['lx'] = val
        elif axisid == 1: self.data['ly'] = -val
        elif axisid == 2: self.data['rx'] = val
        elif axisid == 3: self.data['ry'] = -val
        
        self.send_callback(self.data)

    def on_button_down(self, win, stickid, buttonid):
        self.data['btn'] |= (1 << buttonid)
        #print(f"Button {buttonid} down")
        self.send_callback(self.data)

    def on_button_up(self, win, stickid, buttonid):
        self.data['btn'] &= ~(1 << buttonid)
        self.send_callback(self.data)

    def on_hat(self, win, stickid, hatid, value):
        x, y = value
        for bit in [2, 5, 12, 15]:  # Clear directional bits
            self.data['btn'] &= ~(1 << bit)
        if y == 1:   # Up
            self.data['btn'] |= (1 << 2)
        elif y == -1:  # Down
            self.data['btn'] |= (1 << 5)
        if x == -1:  # Left
            self.data['btn'] |= (1 << 12)
        elif x == 1:  # Right
            self.data['btn'] |= (1 << 15)
        
        self.send_callback(self.data)


# UDP helper class
class UDP:
    def __init__(self, ip, port, portrx):
        self.ip = ip
        self.port = int(port)
        self.portrx = int(portrx)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.portrx))
        self.sock.setblocking(False)

    def send(self, data):
        try:
            
            json_data = json.dumps(data).encode('utf-8')
            self.sock.sendto(json_data, (self.ip, self.port))
        except Exception as e:
            print(f"[ERROR] {e}")
        #print(f"[SENT] Data sent to {self.ip}:{self.port}")
    def receive(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            return json.loads(data.decode('utf-8')), addr
        except BlockingIOError:
            return None
    def close(self):
        self.sock.close()


# Main widget
class Widgets(FloatLayout):
    #ip_text = StringProperty("192.168.123.23")
    #ip_text ="192.168.123.23"
    ip_text = StringProperty("10.168.180.124")
    #ip_text = StringProperty("10.55.14.90")
    port_text = StringProperty("8888")
    port_receive=StringProperty("9999")
    Latency= NumericProperty(0)

    button_state = ListProperty([0] * 13)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.udp =UDP(self.ip_text, self.port_text, self.port_receive)
        self.controller = x5_lite(self.send_data)
        self.send_ts = None

        threading.Thread(target=self.receive_loop, daemon=True).start()
    def btn(self):
        show_popup(self)

    def button(self, index):
        self.button_state[index] ^= 1
        self.send_button_data()
        
    def send_button_data(self):
        controller_data = self.controller.data.copy()
        self.send_data(controller_data)
        
    def send_data(self, controller_data):
        # Convert Kivy property to plain list
        button_state_list = list(self.button_state)
        btnM_value = int(''.join(str(x) for x in button_state_list), 2)
        data = controller_data.copy()
        data['btnM'] = btnM_value
        #print(f"[DATA] {data}")
        self.send_ts=time.time()
        self.udp.send(data)
        
    def receive_loop(self):
         while True:
            result = self.udp.receive()
            if result:
                data, addr = result
                if self.send_ts:
                    recv_ts = time.time()
                    self.Latency = (recv_ts - self.send_ts) * 500
                    #print(f"[LATENCY] Round-trip: {self.Latency:.2f} ms")
                    self.send_ts = None  # Reset after ping pong

# Popup for IP/Port
class P(FloatLayout):
    def __init__(self, parent_widget, **kwargs):
        super().__init__(**kwargs)
        self.parent_widget = parent_widget

    def save(self):
        ip = self.ids.ip_input.text
        port = self.ids.port_input.text

        if ip:
            self.parent_widget.ip_text = ip
        if port:
            self.parent_widget.port_text = port
        try:
            self.parent_widget.udp.close()
        except:
            pass
        
        self.parent_widget.udp = UDP(self.parent_widget.ip_text, self.parent_widget.port_text, self.parent_widget.port_receive)
        threading.Thread(
        target=self.parent_widget.receive_loop,
        daemon=True
        ).start()

        if hasattr(self.parent_widget, "popup_window"):
                    self.parent_widget.popup_window.dismiss()


def show_popup(parent_widget):
    show = P(parent_widget)
    show.ids.ip_input.text = parent_widget.ip_text
    show.ids.port_input.text = parent_widget.port_text

    popupWindow = Popup(title="IP Address and Port", content=show,pos_hint ={"center_x": 0.5, "center_y": 0.75},
                        size_hint=(0.4, 0.5), size=(400, 400))
    parent_widget.popup_window = popupWindow
    popupWindow.open()


class MyApp(App):
    color6 = (152 / 255, 166 / 255, 80 / 255, 1)
    color4 = (42 / 255, 113 / 255, 56 / 255, 1)
    color2 = (41 / 255, 82 / 255, 16 / 255, 1)
    def build(self):
        return Widgets()


if __name__ == "__main__":
    MyApp().run()