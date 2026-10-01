from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform
from datetime import datetime
import os


def resource_path(relative):
    """Правильные пути к ресурсам и на ПК, и внутри APK"""
    if platform == 'android':
        from android.storage import app_storage_path
        base = os.path.dirname(os.path.abspath(__file__))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative)


class MainMenuScreen(Screen):
    pass


class MusicScreen(Screen):
    current_track = StringProperty("Не выбрано")
    is_playing = BooleanProperty(False)
    volume = NumericProperty(0.7)
    sound = None

    tracks = {
        "🌧 Дождь": "assets/sounds/rain.ogg",
        "🌊 Океан": "assets/sounds/ocean.ogg",
        "🌲 Лес": "assets/sounds/forest.ogg",
        "🎵 Белый шум": "assets/sounds/white_noise.ogg",
        "🎹 Пианино": "assets/sounds/piano.ogg",
    }

    def play_track(self, name):
        if self.sound:
            self.sound.stop()
        path = resource_path(self.tracks.get(name, ""))
        if os.path.exists(path):
            self.sound = SoundLoader.load(path)
            if self.sound:
                self.sound.volume = self.volume
                self.sound.loop = True
                self.sound.play()
                self.current_track = name
                self.is_playing = True
        else:
            self.current_track = f"Файл не найден: {name}"

    def toggle_play(self):
        if not self.sound:
            return
        if self.is_playing:
            self.sound.stop()
            self.is_playing = False
        else:
            self.sound.play()
            self.is_playing = True

    def change_volume(self, value):
        self.volume = value
        if self.sound:
            self.sound.volume = value


class TimerScreen(Screen):
    time_left = NumericProperty(0)
    total_time = NumericProperty(0)
    is_running = BooleanProperty(False)
    _event = None

    def set_timer(self, minutes):
        self.stop_timer()
        self.time_left = minutes * 60
        self.total_time = self.time_left
        self.is_running = True
        self._event = Clock.schedule_interval(self._tick, 1)

    def _tick(self, dt):
        if self.time_left > 0:
            self.time_left -= 1
        else:
            self.stop_timer()
            self._on_finish()

    def _on_finish(self):
        app = App.get_running_app()
        music = app.root.get_screen('music')
        if music.sound:
            music.sound.stop()
            music.is_playing = False

    def stop_timer(self):
        if self._event:
            self._event.cancel()
            self._event = None
        self.is_running = False

    def format_time(self):
        m = int(self.time_left) // 60
        s = int(self.time_left) % 60
        return f"{m:02d}:{s:02d}"


class AlarmScreen(Screen):
    alarm_time = StringProperty("07:00")
    alarm_enabled = BooleanProperty(False)
    _event = None

    def toggle_alarm(self, active):
        self.alarm_enabled = active
        if active:
            self._event = Clock.schedule_interval(self._check_time, 1)
        else:
            if self._event:
                self._event.cancel()
                self._event = None

    def _check_time(self, dt):
        now = datetime.now().strftime("%H:%M")
        if now == self.alarm_time and self.alarm_enabled:
            self._ring()
            self.toggle_alarm(False)

    def _ring(self):
        path = resource_path("assets/sounds/alarm.ogg")
        if os.path.exists(path):
            s = SoundLoader.load(path)
            if s:
                s.volume = 1.0
                s.play()


class GalleryScreen(Screen):
    current_image = StringProperty("assets/images/1.jpg")
    images = [
        "assets/images/1.jpg",
        "assets/images/2.jpg",
        "assets/images/3.jpg",
        "assets/images/4.jpg",
    ]

    def next_image(self):
        try:
            i = self.images.index(self.current_image)
            self.current_image = self.images[(i + 1) % len(self.images)]
        except ValueError:
            self.current_image = self.images[0]

    def prev_image(self):
        try:
            i = self.images.index(self.current_image)
            self.current_image = self.images[(i - 1) % len(self.images)]
        except ValueError:
            self.current_image = self.images[0]


class SleepApp(App):
    def build(self):
        self.title = "Sleep Well 🌙"
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(MusicScreen(name='music'))
        sm.add_widget(TimerScreen(name='timer'))
        sm.add_widget(AlarmScreen(name='alarm'))
        sm.add_widget(GalleryScreen(name='gallery'))
        return sm

    def on_stop(self):
        music = self.root.get_screen('music')
        if music.sound:
            music.sound.stop()


if __name__ == '__main__':
    SleepApp().run()