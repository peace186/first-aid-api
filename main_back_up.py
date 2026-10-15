from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from database import FirstAidDatabase


# Initialize Database instance
db = FirstAidDatabase()


# --- SCREEN 1: CATEGORIES & SEARCH ---
class HomeScreen(Screen):
    def _init_(self, **kwargs):
        super()._init_(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = Label(
            text="[b]First Aid Emergency Guide[/b]",
            markup=True,
            font_size='22sp',
            size_hint_y=0.1
        )
        main_layout.add_widget(header)

        # Search Bar
        self.search_input = TextInput(
            hint_text="Search symptoms or conditions (e.g., Burn, CPR)...",
            multiline=False,
            size_hint_y=0.08
        )
        self.search_input.bind(text=self.on_search)
        main_layout.add_widget(self.search_input)

        # Scrollable Content Area
        self.scroll = ScrollView(size_hint=(1, 0.82))
        self.list_layout = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        
        main_layout.add_widget(self.scroll)
        self.add_widget(main_layout)

    def on_enter(self):
        """Populate categories when screen loads."""
        self.load_categories()

    def load_categories(self):
        self.list_layout.clear_widgets()
        categories = db.get_categories()
        
        if not categories:
            self.list_layout.add_widget(Label(text="No categories found.", size_hint_y=None, height=40))
            return

        for cat in categories:
            btn = Button(
                text=cat['name'],
                size_hint_y=None,
                height=50,
                background_color=(0.2, 0.6, 0.8, 1)
            )
            btn.bind(on_release=lambda b, c_id=cat['id'], name=cat['name']: self.open_guides_list(c_id, name))
            self.list_layout.add_widget(btn)

    def on_search(self, instance, text):
        if not text.strip():
            self.load_categories()
            return

        self.list_layout.clear_widgets()
        results = db.search_guides(text.strip())
        
        if not results:
            self.list_layout.add_widget(Label(text="No matching guides found.", size_hint_y=None, height=40))
            return

        for guide in results:
            btn = Button(
                text=f"🔍 {guide['title']}",
                size_hint_y=None,
                height=50,
                background_color=(0.9, 0.4, 0.2, 1)
            )
            btn.bind(on_release=lambda b, g_id=guide['id']: self.open_guide_detail(g_id))
            self.list_layout.add_widget(btn)

    def open_guides_list(self, category_id, category_name):
        guides_screen = self.manager.get_screen('guides_list')
        guides_screen.set_category(category_id, category_name)
        self.manager.current = 'guides_list'

    def open_guide_detail(self, guide_id):
        detail_screen = self.manager.get_screen('guide_detail')
        detail_screen.load_guide(guide_id)
        self.manager.current = 'guide_detail'


# --- SCREEN 2: GUIDES IN SELECTED CATEGORY ---
class GuidesListScreen(Screen):
    def _init_(self, **kwargs):
        super()._init_(**kwargs)
        self.category_id = None
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.title_label = Label(text="", markup=True, font_size='20sp', size_hint_y=0.1)
        main_layout.add_widget(self.title_label)

        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.list_layout = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        main_layout.add_widget(self.scroll)

        back_btn = Button(text="← Back to Categories", size_hint_y=0.1)
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        main_layout.add_widget(back_btn)

        self.add_widget(main_layout)