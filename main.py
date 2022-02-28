import websocket
import time
import threading


class Base:
    # 对长连接情况，涉及到的基类进行重写的方法，这里通信是on open的过程需要发送这样一串bytes来进行开始
    @staticmethod
    def on_open(wsapp):
        wsapp.sock.send_binary(b'e\x00p\x00\x00\x00\x00\x00<\n\x02\xd0\x02\xd0\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')


device_list = ["xxserial"]


class ScrcpyLauncher:
    def __init__(self, serial_model):
        self.base_equip = serial_model
        self.wsapp_list = [websocket.WebSocketApp(f"ws://10.23.27.196:8000/?action=proxy-adb&remote=tcp%3A8886&udid={d}",
                                   on_open=Base.on_open,) for d in device_list]
        [threading.Thread(target=w.run_forever).start() for w in self.wsapp_list]
        # 两秒给设备做一个缓冲
        time.sleep(2)

    def broadcast(self, message: bytes):
        # 叫他broad是因为他是一种广播的形式，但不是广播的通信。借用一下名字，通过join来确保所有设备的并发过程都已完成
        # 目前使用的是统一的message，但message中一定是对特定设备进行操作的，需要在初始化的时候指定设备型号作为基础设备，再进行算法转换
        # 嗯 至于怎么转换，就是另一个功能了
        t_broad = [threading.Thread(target=w.sock.send_binary, args=(message,)) for w in self.wsapp_list]
        [t.start() for t in t_broad]
        [t.join() for t in t_broad]

    def teardown(self):
        [w.close() for w in self.wsapp_list]


a = ScrcpyLauncher("vivo x20")
# 这两个包测试的是延迟情况，虽然理论上讲没有区别
a.broadcast(b"\x02\x00\x00\x00"
            b"\x00\x00\x00\x00"
            b"\x00\x00\x00\x00"
            b"\x00\x37\x00\x00"
            b"\x01\x4d\x01\x60"
            b"\x02\xd0\xff\xff"
            b"\x00\x00\x00\x01\x00")
a.broadcast(b"\x02\x01\x00\x00"
            b"\x00\x00\x00\x00"
            b"\x00\x00\x00\x00"
            b"\x00\x37\x00\x00"
            b"\x01\x4d\x01\x60"
            b"\x02\xd0\x00\x00"
            b"\x00\x00\x00\x00\x00")

a.teardown()
