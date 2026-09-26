import sys, math, random, os, webbrowser
import ctypes
if sys.platform == "darwin":
    os.environ['QT_MAC_WANTS_LAYER'] = '1'
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QAction
from PyQt5.QtGui import QMovie, QPixmap, QPainter, QColor, QTransform, QPainterPath, QBrush
from PyQt5.QtCore import Qt, QPoint, QTimer, QTime

QApplication.setAttribute(Qt.AA_DisableHighDpiScaling)


# ---------------------- 彩带粒子窗口类 ----------------------
class ConfettiWindow(QWidget):
    def __init__(self, on_finished):
        super().__init__()
        self.on_finished = on_finished
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus |
            Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        screen = QApplication.primaryScreen()
        geo = screen.availableGeometry()
        self.setGeometry(geo)
        self.screen_width = geo.width()
        self.screen_height = geo.height()
        self.confetti_list = []
        self.spawn_remain = 180
        self.colors = [
            QColor(255, 80, 80),
            QColor(255, 200, 60),
            QColor(80, 220, 120),
            QColor(80, 170, 255),
            QColor(220, 120, 255),
            QColor(255, 130, 180)
        ]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_confetti)
        self.timer.start(25)

    def update_confetti(self):
        if self.spawn_remain > 0:
            add_num = min(4, self.spawn_remain)
            for _ in range(add_num):
                self.confetti_list.append({
                    "x": random.randint(0, self.screen_width),
                    "y": random.randint(-self.screen_height, -10),
                    "w": random.randint(5, 10),
                    "h": random.randint(12, 24),
                    "vx": random.uniform(-1.4, 1.4),
                    "vy": random.uniform(14, 20),
                    "color": random.choice(self.colors),
                    "life": 170
                })
            self.spawn_remain -= add_num

        for c in self.confetti_list:
            c["x"] += c["vx"]
            c["y"] += c["vy"]
            c["life"] -= 1

        self.confetti_list = [
            c for c in self.confetti_list
            if c["life"] > 0 and c["y"] < self.screen_height
        ]
        self.update()

        if self.spawn_remain <= 0 and len(self.confetti_list) == 0:
            self.timer.stop()
            self.close()
            if self.on_finished:
                self.on_finished()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        for c in self.confetti_list:
            painter.fillRect(int(c["x"]), int(c["y"]), c["w"], c["h"], c["color"])
        painter.end()


# ---------------------- 爱心粒子窗口类 ----------------------
class HeartKissWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus |
            Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.kiss_pix = QPixmap()
        self.resize(400, 400)
        self.hearts = []
        self.pet = None 

        # 基础尺寸（400×400 下的原始坐标）
        self.base_size = 400
        self.base_start_x = 400 * 0.28
        self.base_start_y = 400 * 0.70
        self.base_mid_x = 400 * 0.20
        self.base_mid_y = 400 * 0.38
        self.base_end_x = 400 * 0.14
        self.base_end_y = 400 * 0.11
        self.base_start_heart_size = 32
        self.base_end_heart_size = 16

        # 当前缩放系数（默认 1.0）
        self.scale_factor = 1.0
        self.start_x = int(self.base_start_x)
        self.start_y = int(self.base_start_y)
        self.mid_x = int(self.base_mid_x)
        self.mid_y = int(self.base_mid_y)
        self.end_x = int(self.base_end_x)
        self.end_y = int(self.base_end_y)
        self.start_size = self.base_start_heart_size
        self.end_size = self.base_end_heart_size

        self.max_hearts_per_wave = 4
        self.wave_interval = 900
        self.color_list = {
            "鹅黄色": QColor(255, 230, 120),
            "深黄色": QColor(255, 200, 50),
            "奶油色": QColor(255, 245, 210),
            "浅粉色": QColor(255, 205, 220),
            "粉色": QColor(255, 170, 190),
            "深粉色": QColor(185, 25, 80)
        }
        self.current_color = self.color_list["深粉色"]
        self.is_spawning = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_hearts)
        self.timer.start(25)

        self.wave_timer = QTimer(self)
        self.wave_timer.timeout.connect(self.spawn_wave)
        self.wave_timer.start(self.wave_interval)
    def wheelEvent(self, event):
        if self.pet is not None:
            self.pet.wheelEvent(event)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if self.pet is not None:
            self.pet.mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.pet is not None:
            self.pet.mouseMoveEvent(event)
        else:
            super().mouseMoveEvent(event)

    def set_scale_factor(self, factor):
        """根据窗口实际缩放比例，重新计算轨迹坐标与爱心大小，
        并把已经在飘的爱心也按比例缩放，避免错位"""
        old_factor = self.scale_factor if self.scale_factor > 0 else 1.0
        ratio = factor / old_factor

        self.scale_factor = factor
        self.start_x = int(round(self.base_start_x * factor))
        self.start_y = int(round(self.base_start_y * factor))
        self.mid_x = int(round(self.base_mid_x * factor))
        self.mid_y = int(round(self.base_mid_y * factor))
        self.end_x = int(round(self.base_end_x * factor))
        self.end_y = int(round(self.base_end_y * factor))
        self.start_size = self.base_start_heart_size * factor
        self.end_size = self.base_end_heart_size * factor

        # 把当前正在飘的爱心，位置和大小都按缩放比例同步调整
        for h in self.hearts:
            h["x"] *= ratio
            h["y"] *= ratio
            h["size"] *= ratio

    def set_scale_factor_xy(self, fx, fy):
        """x、y 方向分别缩放，让爱心坐标和矩形窗口一一对应"""
        self.scale_factor = (fx + fy) / 2.0

        self.start_x = self.base_start_x * fx
        self.start_y = self.base_start_y * fy
        self.mid_x = self.base_mid_x * fx
        self.mid_y = self.base_mid_y * fy
        self.end_x = self.base_end_x * fx
        self.end_y = self.base_end_y * fy

        heart_scale = (fx + fy) / 2.0
        self.start_size = self.base_start_heart_size * heart_scale
        self.end_size = self.base_end_heart_size * heart_scale

    def reset_heart_scene(self):
        self.hearts.clear()
        self.is_spawning = True
        self.wave_timer.start(self.wave_interval)
        self.timer.start(25)     

    def closeEvent(self, event):
        self.timer.stop()
        self.wave_timer.stop()
        self.hearts.clear()
        self.hide()
        event.ignore()

    def draw_heart(self, painter, cx, cy, size):
        path = QPainterPath()
        s = size
        top_y = cy - 0.55 * s
        bottom_y = cy + 0.45 * s
        left_x = cx - 0.5 * s
        right_x = cx + 0.5 * s
        middle_y = cy - 0.05 * s

        path.moveTo(cx, bottom_y)
        path.cubicTo(left_x - 0.15 * s, middle_y - 0.3 * s,
                     left_x, top_y + 0.1 * s,
                     left_x + 0.12 * s, top_y)
        path.cubicTo(left_x + 0.28 * s, top_y - 0.12 * s,
                     cx - 0.05 * s, middle_y - 0.2 * s,
                     cx, middle_y + 0.05 * s)
        path.cubicTo(cx + 0.05 * s, middle_y - 0.2 * s,
                     right_x - 0.28 * s, top_y - 0.12 * s,
                     right_x - 0.12 * s, top_y)
        path.cubicTo(right_x, top_y + 0.1 * s,
                     right_x + 0.15 * s, middle_y - 0.3 * s,
                     cx, bottom_y)
        painter.drawPath(path)

    def spawn_wave(self):
        if not self.is_spawning:
            return
        for i in range(self.max_hearts_per_wave):
            offset_x = random.randint(-2, 2) * self.scale_factor
            offset_y = random.randint(-2, 2) * self.scale_factor
            self.hearts.append({
                "x": self.start_x + offset_x,
                "y": self.start_y + offset_y,
                "size": self.start_size + random.randint(-2, 2) * self.scale_factor,
                "life": 140,
                "max_life": 140,
                "color": self.current_color,
                "phase": random.uniform(0, math.pi * 2)
            })

    def update_hearts(self):
        for h in self.hearts:
            progress = 1 - h["life"] / h["max_life"]
            if progress < 0.45:
                t = progress / 0.45
                h["x"] = self.start_x + (self.mid_x - self.start_x) * t
                h["y"] = self.start_y + (self.mid_y - self.start_y) * t
            else:
                t = (progress - 0.45) / 0.55
                h["x"] = self.mid_x + (self.end_x - self.mid_x) * t
                h["y"] = self.mid_y + (self.end_y - self.mid_y) * t
            h["x"] += math.sin(h["phase"] + progress * 6) * 0.3 * self.scale_factor
            h["size"] = self.start_size + (self.end_size - self.start_size) * progress
            h["life"] -= 1

        self.hearts = [h for h in self.hearts if h["life"] > 0]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        for h in self.hearts:
            alpha = max(0, int(255 * h["life"] / h["max_life"]))
            c = QColor(h["color"])
            c.setAlpha(alpha)
            painter.setBrush(QBrush(c))
            painter.setPen(Qt.NoPen)
            self.draw_heart(painter, h["x"], h["y"], h["size"])
        painter.end()


# ---------------------- 桌面宠物主类 ----------------------
class RanDesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus |
            Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.drag_position = None
        self.file_list = {
            "idle": "shineranGIF-ezgif.com-crop.gif",
            "cheer": "ran_cheer.png",
            "kiss": "ran_kiss.png",
            "reminder": "ran_reminder.png"
        }
        self.current_movie = None
        self.current_state = "idle"
        self.pix = QPixmap()

        self.meal_periods = [
            {"start": QTime(7, 30), "end": QTime(9, 30)},
            {"start": QTime(12, 0), "end": QTime(13, 30)},
            {"start": QTime(18, 0), "end": QTime(20, 0)}
        ]
        self.has_eaten_this_meal = False

        self.shake_timer = QTimer(self)
        self.shake_timer.timeout.connect(self.update_shake)
        self.shake_timer.start(30)
        self.shake_angle = 0
        self.shake_speed = 0.04
        self.shake_high_speed = 0.08
        self.is_shaking = False
        self.highshake_duration = 300 * 1000
        self.highshake_timer = QTimer(self)
        self.highshake_timer.timeout.connect(self.trigger_high_shake)
        self.highshake_timer.start(30 * 1000)

        self.check_time_timer = QTimer(self)
        self.check_time_timer.timeout.connect(self.check_in_meal_window)
        self.check_time_timer.start(1000)

        self.confetti_window = None
        self.heart_kiss_window = HeartKissWindow()
        self.heart_kiss_window.pet = self

        # 滚轮缩放配置
        self.scale = 1.0
        self.min_scale = 0.3
        self.max_scale = 3.5
        self.scale_step = 0.04

        self.original_pix_w = 0
        self.original_pix_h = 0
                # Mac 上每隔一段时间重新置顶一次，避免被其他窗口盖住
        self.top_timer = QTimer(self)
        self.top_timer.timeout.connect(self.keep_on_top)
        self.top_timer.start(1000)
    
        self.switch_state("idle")

    def force_heart_on_top(self):
        """强制把爱心窗口钉在最顶层。Windows 用 Win32 API，Mac 用 Qt raise_"""
        if not self.heart_kiss_window.isVisible():
            return
        self.heart_kiss_window.raise_()

        if sys.platform != "win32":
            return  # Mac / Linux 只靠 raise_()，不调 Win32 API

        try:
            hwnd = int(self.heart_kiss_window.winId())
            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )
        except Exception:
            pass

    def keep_on_top(self):
        self.raise_()
        if self.heart_kiss_window.isVisible():
            self.force_heart_on_top()
        if self.confetti_window is not None and self.confetti_window.isVisible():
            self.confetti_window.raise_()

    def open_birthday_card(self, filename):
        full_path = os.path.abspath(filename)
        webbrowser.open("file://" + full_path)

    def time_in_range(self, now: QTime, s: QTime, e: QTime):
        return s <= now <= e

    def check_in_meal_window(self):
        now = QTime.currentTime()
        in_meal = False
        for p in self.meal_periods:
            if self.time_in_range(now, p["start"], p["end"]):
                in_meal = True
                break

        if in_meal:
            if not self.has_eaten_this_meal:
                if self.current_state != "reminder":
                    self.switch_state("reminder")
                self.is_shaking = True
            else:
                self.is_shaking = False
        else:
            self.has_eaten_this_meal = False
            self.is_shaking = False
            if self.current_state == "reminder":
                pass

    def trigger_high_shake(self):
        if not self.is_shaking:
            return
        self.shake_speed = self.shake_high_speed
        QTimer.singleShot(self.highshake_duration, lambda: setattr(self, "shake_speed", 0.04))

    def update_shake(self):
        if not self.is_shaking:
            self.shake_angle = 0
        else:
            self.shake_angle += self.shake_speed
        self.update()

    def switch_state(self, state_name):
        self.current_state = state_name
        fp = self.file_list[state_name]

        if self.current_movie is not None:
            self.current_movie.stop()
            self.current_movie = None

        if fp.endswith(".gif"):
            self.current_movie = QMovie(fp)
            self.current_movie.jumpToFrame(0)
            self.pix = self.current_movie.currentPixmap()
            self.pix.setDevicePixelRatio(1.0)   
            self.current_movie.frameChanged.connect(self.on_gif_frame)
            self.current_movie.start()
        else:
            self.pix = QPixmap(fp)
            self.pix.setDevicePixelRatio(1.0)   

        self.original_pix_w = max(1, self.pix.width())
        self.original_pix_h = max(1, self.pix.height())

        new_w = int(round(self.original_pix_w * self.scale))
        new_h = int(round(self.original_pix_h * self.scale))
        self.resize(new_w, new_h)

        self.update()

        if state_name == "kiss":
            self.raise_()
            self.heart_kiss_window.reset_heart_scene()
            self.heart_kiss_window.show()
            self.sync_heart_window_geometry()
            self.force_heart_on_top()
        else:
            self.heart_kiss_window.hide()
            self.raise_()    

    def on_gif_frame(self):
        self.pix = self.current_movie.currentPixmap()
        self.pix.setDevicePixelRatio(1.0)
        if self.pix.width() > 0 and self.pix.height() > 0:
            self.original_pix_w = self.pix.width()
            self.original_pix_h = self.pix.height()

            new_w = int(round(self.original_pix_w * self.scale))
            new_h = int(round(self.original_pix_h * self.scale))

            if self.width() != new_w or self.height() != new_h:
                self.resize(new_w, new_h)

        self.update()

    def on_eaten(self):
        self.has_eaten_this_meal = True
        self.is_shaking = False
        if self.confetti_window is None:
            def on_confetti_finished():
                self.confetti_window = None
                self.switch_state("kiss")

            self.confetti_window = ConfettiWindow(on_finished=on_confetti_finished)
            self.confetti_window.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        painter.fillRect(self.rect(), Qt.transparent)

        if self.pix.isNull() or self.original_pix_w == 0 or self.original_pix_h == 0:
            return

        scaled_w = int(round(self.original_pix_w * self.scale))
        scaled_h = int(round(self.original_pix_h * self.scale))

        draw_x = (self.width() - scaled_w) // 2
        draw_y = (self.height() - scaled_h) // 2

        rot = 8 * math.sin(self.shake_angle)
        cx = draw_x + scaled_w / 2
        cy = draw_y + scaled_h / 2

        transform = QTransform()
        transform.translate(cx, cy)
        transform.rotate(rot)
        transform.translate(-cx, -cy)
        painter.setTransform(transform)

        painter.drawPixmap(draw_x, draw_y, scaled_w, scaled_h, self.pix)
        painter.end()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        step = delta / 120 * self.scale_step
        new_scale = self.scale + step
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))

        if abs(new_scale - self.scale) < 1e-6:
            event.accept()
            return

        self.scale = new_scale

        if self.original_pix_w > 0 and self.original_pix_h > 0:
            new_w = int(round(self.original_pix_w * self.scale))
            new_h = int(round(self.original_pix_h * self.scale))
            self.resize(new_w, new_h)

        self.raise_()     

        if self.heart_kiss_window.isVisible():
            self.sync_heart_window_geometry()
            self.heart_kiss_window.raise_()
            QTimer.singleShot(50, self.force_heart_on_top)
  
        self.update()
        event.accept()

    def reset_scale(self):
        self.scale = 1.0
        if self.original_pix_w > 0 and self.original_pix_h > 0:
            self.resize(self.original_pix_w, self.original_pix_h)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.current_state == "kiss":
                if self.heart_kiss_window.is_spawning:
                    self.heart_kiss_window.is_spawning = False
                    self.heart_kiss_window.wave_timer.stop()
                else:
                    self.heart_kiss_window.reset_heart_scene()

            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def moveEvent(self, event):
        if self.heart_kiss_window.isVisible():
            self.sync_heart_window_geometry()
            self.heart_kiss_window.raise_()

    def sync_heart_window_geometry(self):
        """爱心窗口与宠物窗口尺寸、位置完全重合，坐标系统一，缩放不漂移"""
        if not self.original_pix_w or not self.original_pix_h:
            return

        pet_w = int(round(self.original_pix_w * self.scale))
        pet_h = int(round(self.original_pix_h * self.scale))
        pet_w = max(60, pet_w)
        pet_h = max(60, pet_h)

        # 爱心窗口和宠物窗口尺寸完全一致
        self.heart_kiss_window.resize(pet_w, pet_h)

        # x、y 方向分别按宽高比缩放，坐标系和宠物窗口一一对应
        self.heart_kiss_window.set_scale_factor_xy(pet_w / 400.0, pet_h / 400.0)

        # 左上角完全重合，不做任何屏幕边界限制
        self.heart_kiss_window.move(self.x(), self.y())

        self.force_heart_on_top()
        # ====================================================================================
    def contextMenuEvent(self, event):
        self.top_timer.stop()   
        now = QTime.currentTime()
        in_meal_time = False
        for p in self.meal_periods:
            if self.time_in_range(now, p["start"], p["end"]):
                in_meal_time = True
                break

        menu = QMenu()
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowStaysOnTopHint)

        act_idle = QAction("待机(新兰)", self)
        act_idle.triggered.connect(lambda: self.switch_state("idle"))
        menu.addAction(act_idle)

        act_cheer = QAction("鼓励 cheer", self)
        act_cheer.triggered.connect(lambda: self.switch_state("cheer"))
        menu.addAction(act_cheer)

        kiss_color_submenu = QMenu()
        color_data = [
            ("鹅黄", QColor(255, 230, 120)),
            ("深黄", QColor(255, 200, 50)),
            ("奶油", QColor(255, 245, 210)),
            ("浅粉", QColor(255, 205, 220)),
            ("粉黛", QColor(255, 170, 190)),
            ("深粉", QColor(185, 25, 80))
        ]
        for name, color in color_data:
            act_color = QAction(name, self)

            def set_color(checked, nm=name, c=color):
                self.heart_kiss_window.current_color = c
                self.switch_state("kiss")

            act_color.triggered.connect(set_color)
            kiss_color_submenu.addAction(act_color)

        act_kiss_root = QAction("爱心 kiss", self)
        act_kiss_root.triggered.connect(lambda: self.switch_state("kiss"))
        act_kiss_root.setMenu(kiss_color_submenu)
        menu.addAction(act_kiss_root)

        act_remind = QAction("吃饭提醒", self)
        act_remind.triggered.connect(lambda: self.switch_state("reminder"))
        menu.addAction(act_remind)

        card_menu = menu.addMenu("🎂生日贺卡集")

        act_card25 = QAction("2025 生日贺卡", self)
        act_card25.triggered.connect(
            lambda: self.open_birthday_card("birthcard20250925.html")
        )
        card_menu.addAction(act_card25)

        act_card26 = QAction("2026 生日贺卡", self)
        act_card26.triggered.connect(
            lambda: self.open_birthday_card("birthday20260926.html")
        )
        card_menu.addAction(act_card26)

        if in_meal_time:
            act_eaten = QAction("✅ 吃过啦！", self)
            act_eaten.triggered.connect(self.on_eaten)
            menu.addAction(act_eaten)

        menu.addSeparator()

        act_reset_size = QAction("重置宠物大小", self)
        act_reset_size.triggered.connect(self.reset_scale)
        menu.addAction(act_reset_size)

        act_exit = QAction("退出", self)
        act_exit.triggered.connect(QApplication.quit)
        menu.addAction(act_exit)

        menu.exec_(event.globalPos()) 
        self.top_timer.start(1000)
        event.accept()


if __name__ == "__main__":
    try:
        # ============ macOS 兼容：设置辅助应用模式，不抢焦点 ============
        if sys.platform == "darwin":
            try:
                from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
                NSApplication.sharedApplication().setActivationPolicy_(
                    NSApplicationActivationPolicyAccessory
                )
                print("[macOS] 已设置为辅助应用模式，不会抢占焦点")
            except ImportError:
                print("[macOS] 警告：未找到 pyobjc，无法设置辅助应用模式")
                print("[macOS] 请在打包前执行: pip3 install pyobjc")
        # =============================================================

        app = QApplication(sys.argv)
        pet = RanDesktopPet()
        pet.show()
        sys.exit(app.exec_())
    except Exception as err:
        print("启动报错：", err)
        input("按回车关闭窗口")