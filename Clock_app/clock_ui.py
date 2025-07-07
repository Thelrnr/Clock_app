import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.audio import SoundLoader
from kivy.clock import Clock as KivyClock
from kivy.properties import NumericProperty, StringProperty
import math
import time
import os
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import Label as CoreLabel
from kivy.uix.spinner import Spinner

class ClockFace(Widget):
    hour_angle = NumericProperty(0)
    minute_angle = NumericProperty(0)
    second_angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = 180
        self.center_x = 250
        self.center_y = 250
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()
        self._clock_event = None
        self.set_to_current_time()
        self.start_clock()

    def set_to_current_time(self):
        now = time.localtime()
        self.hour_angle = ((now.tm_hour % 12) + now.tm_min / 60) * 30
        self.minute_angle = now.tm_min * 6
        self.second_angle = now.tm_sec * 6

    def start_clock(self):
        if self._clock_event:
            self._clock_event.cancel()
        self._clock_event = KivyClock.schedule_interval(self.update_time, 1/30)

    def stop_clock(self):
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None

    def update_time(self, dt):
        now = time.localtime()
        self.hour_angle = ((now.tm_hour % 12) + now.tm_min / 60) * 30
        self.minute_angle = now.tm_min * 6
        self.second_angle = now.tm_sec * 6
        self.update_canvas()

    def hand_pos(self, hand):
        if hand == 'hour':
            angle = math.radians(self.hour_angle - 90)
            length = self.radius * 0.5
        elif hand == 'minute':
            angle = math.radians(self.minute_angle - 90)
            length = self.radius * 0.8
        else:  # second
            angle = math.radians(self.second_angle - 90)
            length = self.radius * 0.9
        x = self.center_x + length * math.cos(angle)
        y = self.center_y + length * math.sin(angle)
        return x, y

    def distance(self, x1, y1, x2, y2):
        return math.hypot(x2 - x1, y2 - y1)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Background (gold-like)
            Color(0.9, 0.8, 0.5)
            Ellipse(pos=(self.center_x - self.radius, self.center_y - self.radius), size=(self.radius*2, self.radius*2))
            # Third most outer ring: fine divisions for ms and us
            outer_ring_radius = self.radius - 2
            # 1000 fine ticks for ms (every 0.36 degrees)
            Color(0.5, 0.5, 0.5, 0.5)
            for i in range(1000):
                angle = math.radians(i * 0.36 - 90)
                outer = outer_ring_radius
                inner = outer_ring_radius - (6 if i % 10 == 0 else 2)
                x1 = self.center_x + outer * math.cos(angle)
                y1 = self.center_y + outer * math.sin(angle)
                x2 = self.center_x + inner * math.cos(angle)
                y2 = self.center_y + inner * math.sin(angle)
                Line(points=[x1, y1, x2, y2], width=1)
            # Outer ring for minute markers
            Color(0, 0, 0)
            for i in range(60):
                angle = math.radians(i * 6 - 90)
                outer = self.radius - 5
                inner = self.radius - (20 if i % 5 == 0 else 10)
                x1 = self.center_x + outer * math.cos(angle)
                y1 = self.center_y + outer * math.sin(angle)
                x2 = self.center_x + inner * math.cos(angle)
                y2 = self.center_y + inner * math.sin(angle)
                Line(points=[x1, y1, x2, y2], width=2 if i % 5 == 0 else 1)
                # Minute numbers
                if i % 5 == 0:
                    min_num = str(i if i > 0 else 60)
                    min_angle = math.radians(i * 6 - 90)
                    tx = self.center_x + (self.radius - 32) * math.cos(min_angle)
                    ty = self.center_y + (self.radius - 32) * math.sin(min_angle)
                    core_label = CoreLabel(text=min_num, font_size=12)
                    core_label.refresh()
                    texture = core_label.texture
                    Rectangle(texture=texture, pos=(tx - texture.width/2, ty - texture.height/2), size=texture.size)
            # Outer ring: 1-12 (large, bold)
            for i in range(1, 13):
                angle = math.radians((i / 12) * 360 - 90)
                tx = self.center_x + (self.radius - 60) * math.cos(angle)
                ty = self.center_y + (self.radius - 60) * math.sin(angle)
                core_label = CoreLabel(text=str(i), font_size=32, bold=True)
                core_label.refresh()
                texture = core_label.texture
                Rectangle(texture=texture, pos=(tx - texture.width/2, ty - texture.height/2), size=texture.size)
            # Inner ring: 13-24 (smaller)
            for i in range(13, 25):
                angle = math.radians(((i-12) / 12) * 360 - 90)
                tx = self.center_x + (self.radius - 95) * math.cos(angle)
                ty = self.center_y + (self.radius - 95) * math.sin(angle)
                core_label = CoreLabel(text=str(i), font_size=16)
                core_label.refresh()
                texture = core_label.texture
                Rectangle(texture=texture, pos=(tx - texture.width/2, ty - texture.height/2), size=texture.size)
            # Draw hands
            # Hour hand
            Color(0.5, 0.2, 0.1)
            hx, hy = self.hand_pos('hour')
            Line(points=[self.center_x, self.center_y, hx, hy], width=6)
            # Minute hand
            Color(0.8, 0, 0)
            mx, my = self.hand_pos('minute')
            Line(points=[self.center_x, self.center_y, mx, my], width=4)
            # Second hand
            Color(0.2, 0.2, 0.2)
            sx, sy = self.hand_pos('second')
            Line(points=[self.center_x, self.center_y, sx, sy], width=2)
            # Center circle
            Color(0.2, 0.2, 0.2)
            Ellipse(pos=(self.center_x-8, self.center_y-8), size=(16, 16))

    def get_alarm_time(self):
        return None

class AlarmApp(App):
    def build(self):
        self.clock_face = ClockFace(size_hint=(1, 0.85))
        self.tone_path = ''
        self.snooze_duration = 5
        self.sound = None
        self.alarm_set = False
        self.alarm_hour = '07'
        self.alarm_minute = '00'
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        main_layout.add_widget(self.clock_face)
        # Footer controls
        footer = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        self.tone_btn = Button(text='Tone', size_hint=(0.18, 1), font_size=16)
        self.tone_btn.bind(on_release=self.open_file_chooser)
        footer.add_widget(self.tone_btn)
        # Digital alarm time controls
        alarm_box = BoxLayout(orientation='horizontal', size_hint=(0.32, 1), spacing=5)
        alarm_label = Label(text='Alarm:', size_hint=(0.3, 1), font_size=14, halign='right', valign='middle')
        alarm_label.bind(size=alarm_label.setter('text_size'))
        self.hour_spinner = Spinner(
            text=self.alarm_hour,
            values=[f"{i:02d}" for i in range(0, 24)],
            size_hint=(0.35, 1),
            font_size=16
        )
        self.minute_spinner = Spinner(
            text=self.alarm_minute,
            values=[f"{i:02d}" for i in range(0, 60)],
            size_hint=(0.35, 1),
            font_size=16
        )
        alarm_box.add_widget(alarm_label)
        alarm_box.add_widget(self.hour_spinner)
        alarm_box.add_widget(Label(text=":", size_hint=(0.1, 1), font_size=16))
        alarm_box.add_widget(self.minute_spinner)
        footer.add_widget(alarm_box)
        # Snooze label and vertical spinner
        snooze_box = BoxLayout(orientation='horizontal', size_hint=(0.18, 1), spacing=5)
        snooze_label = Label(text='Snooze (min):', size_hint=(0.6, 1), font_size=14, halign='right', valign='middle')
        snooze_label.bind(size=snooze_label.setter('text_size'))
        self.snooze_spinner = Spinner(
            text='5',
            values=[str(i) for i in range(1, 61)],
            size_hint=(0.4, 1),
            font_size=16
        )
        snooze_box.add_widget(snooze_label)
        snooze_box.add_widget(self.snooze_spinner)
        footer.add_widget(snooze_box)
        self.set_btn = Button(text='Set Alarm', size_hint=(0.18, 1), font_size=16)
        self.set_btn.bind(on_release=self.set_alarm)
        footer.add_widget(self.set_btn)
        main_layout.add_widget(footer)
        self.status_label = Label(text='Alarm not set', size_hint=(1, 0.07), font_size=14)
        main_layout.add_widget(self.status_label)
        return main_layout

    def open_file_chooser(self, instance):
        content = FileChooserIconView()
        popup = Popup(title='Select Alarm Tone', content=content, size_hint=(0.9, 0.9))
        def file_selected(instance, selection):
            if selection:
                self.tone_path = selection[0]
                self.tone_btn.text = f"Tone: {os.path.basename(self.tone_path)}"
                popup.dismiss()
        content.bind(on_submit=file_selected)
        popup.open()

    def set_alarm(self, instance):
        self.snooze_duration = int(self.snooze_spinner.text)
        self.alarm_hour = self.hour_spinner.text
        self.alarm_minute = self.minute_spinner.text
        self.alarm_time = f"{self.alarm_hour}:{self.alarm_minute}"
        self.status_label.text = f"Alarm set for {self.alarm_time}"
        self.alarm_set = True
        KivyClock.unschedule(self.check_alarm)
        KivyClock.schedule_interval(self.check_alarm, 1)

    def check_alarm(self, dt):
        if not self.alarm_set:
            return
        now = time.strftime('%H:%M')
        if now == self.alarm_time:
            self.status_label.text = 'Alarm ringing!'
            self.play_tone()
            self.show_snooze_popup()
            self.alarm_set = False
            KivyClock.unschedule(self.check_alarm)

    def play_tone(self):
        if self.tone_path and os.path.exists(self.tone_path):
            self.sound = SoundLoader.load(self.tone_path)
            if self.sound:
                self.sound.play()
        else:
            self.status_label.text = 'Tone file not found!'

    def show_snooze_popup(self):
        box = BoxLayout(orientation='vertical', spacing=10, padding=10)
        label = Label(text='Snooze or Stop?')
        box.add_widget(label)
        btn_box = BoxLayout(orientation='horizontal', spacing=10)
        snooze_btn = Button(text='Snooze')
        stop_btn = Button(text='Stop')
        btn_box.add_widget(snooze_btn)
        btn_box.add_widget(stop_btn)
        box.add_widget(btn_box)
        popup = Popup(title='Alarm', content=box, size_hint=(0.7, 0.4))
        def snooze(instance):
            popup.dismiss()
            if self.sound:
                self.sound.stop()
            self.snooze_alarm()
        def stop(instance):
            popup.dismiss()
            if self.sound:
                self.sound.stop()
        snooze_btn.bind(on_release=snooze)
        stop_btn.bind(on_release=stop)
        popup.open()

    def snooze_alarm(self):
        h, m = map(int, self.alarm_time.split(':'))
        total = h * 60 + m + self.snooze_duration
        new_h = (total // 60) % 24
        new_m = total % 60
        self.alarm_time = f"{new_h:02d}:{new_m:02d}"
        self.status_label.text = f"Snoozed to {self.alarm_time}"
        self.alarm_set = True
        KivyClock.unschedule(self.check_alarm)
        KivyClock.schedule_interval(self.check_alarm, 1)

if __name__ == '__main__':
    print("\n==============================\n   Created by Vinay\n==============================\n")
    AlarmApp().run()