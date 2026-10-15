import os
import traceback

# 1. Set graphics backend
os.environ['KIVY_GL_BACKEND'] = 'sdl2'

# 2. Configure window size BEFORE creating/importing Window
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)


# ... import your other modules ...
# 2. Now import Kivy modules
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

from database import FirstAidDatabase
# initialize my  database instance
db= FirstAidDatabase()


# --- 1. HOME SCREEN ---
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        self.main_layout.add_widget(Label(
            text="[b]First Aid Guide[/b]",
            markup=True,
            font_size='22sp',
            size_hint_y=None,
            height=40
        ))

        self.status_label = Label(
            text="[color=ffff00]🟡 Checking network...[/color]",
            markup=True,
            font_size='14sp',
            size_hint_y=None,
            height=30
        )
        self.main_layout.add_widget(self.status_label)

        self.search_input = TextInput(
            hint_text="Search emergency (e.g., CPR, burn)...",
            size_hint_y=None,
            height=40,
            multiline=False
        )
        self.search_input.bind(text=self.filter_topics)
        self.main_layout.add_widget(self.search_input)

        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        self.main_layout.add_widget(self.scroll)

        self.add_widget(self.main_layout)
        self._render_content()
        self.trigger_sync()

    def trigger_sync(self):
        """Checks connection, syncs updates, and updates the visual UI banner."""
        if db.check_internet():
            print("Online: Checking for updates...")
            self.status_label.text = "[color=00ff00]🟢 Online - Synced[/color]"

            mock_remote_server_data = [
                {
                    "id": 1,
                    "category_id": 1,
                    "title": "Minor Thermal Burns",
                    "symptoms": "Red skin, pain, mild swelling",
                    "steps": "1. Cool the burn under cool running water for 10-20 minutes.\n2. Remove tight items.\n3. Cover loosely with clean cloth. [Updated via Cloud Sync]",
                    "version": 2
                }
            ]
            db.sync_guides_from_server(mock_remote_server_data)
            self.load_categories()
        else:
            print("Offline: Running strictly on local SQLite data.")
            self.status_label.text = "[color=ff5555]🔴 Offline Mode (Local SQLite)[/color]"

    def load_categories(self):
        self._render_content(self.search_input.text)

    def _render_content(self, query_text=""):
        try:
            self.content.clear_widgets()
            query = (query_text or "").strip().lower()

            emergency_topics = db.get_emergency_topics()
            categories = db.get_categories()

            if query:
                emergency_topics = [
                    item for item in emergency_topics
                    if query in item.get('title', '').lower()
                    or query in (item.get('summary') or '').lower()
                ]
                categories = [
                    cat for cat in categories
                    if query in cat.get('name', '').lower()
                ]

            if emergency_topics:
                self.content.add_widget(Label(
                    text="[color=#ff4444]EMERGENCY QUICK ACCESS[/color]",
                    markup=True,
                    font_size='14sp',
                    bold=True,
                    size_hint_y=None,
                    height=30
                ))

                for item in emergency_topics:
                    btn = Button(
                        text=f"🚨 {item['title']}",
                        size_hint_y=None,
                        height=50,
                        background_color=(0.85, 0.2, 0.2, 1)
                    )
                    btn.bind(on_release=lambda instance, t_id=item['id']: self.open_detail(t_id))
                    self.content.add_widget(btn)

            if categories:
                self.content.add_widget(Label(
                    text="CATEGORIES",
                    font_size='14sp',
                    bold=True,
                    color=(0.8, 0.8, 0.8, 1),
                    size_hint_y=None,
                    height=35
                ))

                for cat in categories:
                    btn = Button(
                        text=cat['name'],
                        size_hint_y=None,
                        height=50,
                        background_color=(0.2, 0.5, 0.8, 1)
                    )
                    btn.bind(on_release=lambda instance, c_id=cat['id'], c_name=cat['name']: self.open_category(c_id, c_name))
                    self.content.add_widget(btn)

            if not emergency_topics and not categories:
                self.content.add_widget(Label(
                    text="No matches found",
                    size_hint_y=None,
                    height=40,
                    color=(0.8, 0.8, 0.8, 1)
                ))
        except Exception as e:
            print(f"\n[ERROR in HomeScreen]: {e}")
            traceback.print_exc()

    def filter_topics(self, instance, value):
        self._render_content(value)

    def on_pre_enter(self):
        self._render_content(self.search_input.text)

    def open_category(self, category_id, category_name):
        app = App.get_running_app()
        app.topic_list_screen.category_id = category_id
        app.topic_list_screen.category_name = category_name
        app.sm.current = 'topic_list'

    def open_detail(self, topic_id):
        app = App.get_running_app()
        app.detail_screen.topic_id = topic_id
        app.sm.current = 'detail'


# --- 2. TOPIC LIST SCREEN ---
class TopicListScreen(Screen):
    category_id = None
    category_name = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.header_label = Label(font_size='20sp', bold=True, size_hint_y=0.1)
        self.layout.add_widget(self.header_label)

        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.topics_box = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None)
        self.topics_box.bind(minimum_height=self.topics_box.setter('height'))
        self.scroll.add_widget(self.topics_box)
        self.layout.add_widget(self.scroll)

        back_btn = Button(text="< Back to Home", size_hint_y=0.1)
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def on_pre_enter(self):
        try:
            self.header_label.text = self.category_name
            self.topics_box.clear_widgets()

            category_key = self.category_id if self.category_id is not None else self.category_name
            topics = db.get_topics_by_category(category_key)

            if not topics:
                no_data_lbl = Label(text="No guides available for this category.", size_hint_y=None, height=40)
                self.topics_box.add_widget(no_data_lbl)
                return

            for topic in topics:
                btn = Button(
                    text=topic['title'],
                    size_hint_y=None,
                    height=50,
                    background_color=(0.2, 0.6, 0.8, 1)
                )
                btn.bind(on_release=lambda instance, t_id=topic['id']: self.open_detail(t_id))
                self.topics_box.add_widget(btn)
        except Exception as e:
            print(f"\n[ERROR in TopicListScreen]: {e}")
            traceback.print_exc()

    def open_detail(self, topic_id):
        app = App.get_running_app()
        app.detail_screen.topic_id = topic_id
        app.sm.current = 'detail'


# --- 3. DETAIL SCREEN ---
class DetailScreen(Screen):
    topic_id = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        self.title_label = Label(font_size='22sp', bold=True, size_hint_y=None, height=40)
        self.layout.add_widget(self.title_label)

        self.scroll = ScrollView()
        self.content_box = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None)
        self.content_box.bind(minimum_height=self.content_box.setter('height'))
        self.scroll.add_widget(self.content_box)
        self.layout.add_widget(self.scroll)

        back_btn = Button(text="< Back", size_hint_y=None, height=45)
        back_btn.bind(on_release=lambda instance: setattr(App.get_running_app().sm, 'current', 'home'))
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def on_pre_enter(self):
        try:
            self.content_box.clear_widgets()
            topic_data = db.get_topic_with_steps(self.topic_id)

            if not topic_data:
                no_data_lbl = Label(text="No details found for this topic.", size_hint_y=None, height=40)
                self.content_box.add_widget(no_data_lbl)
                return

            # Handle if the database returns a list of step rows
            if isinstance(topic_data, list):
                if not topic_data:
                    return
                
                first_row = topic_data[0]
                self.title_label.text = first_row.get('title', 'First Aid Guide')

                warning_note = first_row.get('warning_note') or first_row.get('warning')
                if warning_note:
                    warning_lbl = Label(
                        text=f"[color=ff4444][b]WARNING:[/b] {warning_note}[/color]",
                        markup=True,
                        text_size=(320, None),
                        size_hint_y=None
                    )
                    warning_lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                    self.content_box.add_widget(warning_lbl)

                for row in topic_data:
                    step_num = row.get('step_number')
                    instruction = row.get('instruction') or row.get('step_text')
                    if instruction:
                        step_text = f"Step {step_num}: {instruction}" if step_num else f"• {instruction}"
                        step_lbl = Label(
                            text=step_text,
                            markup=True,
                            font_size='15sp',
                            size_hint_y=None,
                            halign='left',
                            valign='top'
                        )
                        step_lbl.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - 20, None)))
                        step_lbl.bind(texture_size=lambda s, w: setattr(s, 'height', s.texture_size[1] + 20))
                        self.content_box.add_widget(step_lbl)
            else:
                topic = topic_data
                self.title_label.text = topic.get('title', 'First Aid Guide')
                steps_text = topic.get('steps', 'No steps available.')
                steps_lbl = Label(
                    text=f"[b]Step-by-Step Instructions:[/b]\n{steps_text}",
                    markup=True,
                    font_size='16sp',
                    size_hint_y=None,
                    halign='left',
                    valign='top'
                )
                steps_lbl.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - 20, None)))
                steps_lbl.bind(texture_size=lambda s, w: setattr(s, 'height', s.texture_size[1] + 20))
                self.content_box.add_widget(steps_lbl)

        except Exception as e:
            print(f"\n[ERROR in DetailScreen]: {e}")
            traceback.print_exc()


# --- 4. MAIN APPLICATION ---
class FirstAidApp(App):
    def build(self):
        Window.clearcolor = (0.12, 0.12, 0.14, 1)
        self.sm = ScreenManager()

        self.home_screen = HomeScreen(name='home')
        self.topic_list_screen = TopicListScreen(name='topic_list')
        self.detail_screen = DetailScreen(name='detail')

        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.topic_list_screen)
        self.sm.add_widget(self.detail_screen)

        return self.sm

if __name__ == '__main__':
    try:
        print("Starting First Aid App...")
        app = FirstAidApp()
        app.run()
    except Exception as e:
        print(f"\n[ERROR CAUGHT]: {e}\n")
        input("Press Enter to close...") # Keeps the terminal open so you can read the error