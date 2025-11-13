from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar  # ✅ Usar o Snackbar antigo
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.image import AsyncImage
import random


def show_snackbar(text):
    snackbar = Snackbar(
        text=text,
        snackbar_x="10dp",
        snackbar_y="10dp",
        size_hint_x=0.5,  # Largura
        bg_color=(0.2, 0.2, 0.2, 1),  # Cor de fundo
    )
    snackbar.open()


class HistorySquare(MDCard):
    text = StringProperty('')
    md_bg_color = ListProperty([0.2, 0.4, 0.8, 0.7])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = ('60dp', '35dp')
        self.padding = '8dp'
        self.elevation = 2
        self.radius = [8]

        self.add_widget(
            MDLabel(
                text=self.text,
                theme_text_color='Custom',
                text_color=[1, 1, 1, 1],
                font_size='11sp',
                halign='center',
                valign='center',
                bold=True,
                text_size=(None, None),
                shorten=True,
                shorten_from='right'
            )
        )
        self.bind(text=self.update_label_text)

    def update_label_text(self, instance, value):
        if self.children:
            self.children[0].text = value


class WinnerItem(MDBoxLayout):
    name = StringProperty('')
    amount = NumericProperty(0)
    multiplier = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.size = ('220dp', '55dp')
        self.padding = '8dp'
        self.spacing = '8dp'

        self.avatar_widget = self.create_avatar()

        info_container = MDBoxLayout(
            orientation='vertical',
            size_hint_x=0.7,
            spacing='2dp'
        )

        self.name_label = MDLabel(
            text=self.name,
            theme_text_color='Custom',
            text_color=[0.9, 0.9, 0.9, 1],
            font_size='11sp',
            halign='left',
            valign='center',
            size_hint_y=0.4
        )

        self.amount_label = MDLabel(
            text=f'ganhou {self.format_currency_br(self.amount)} em {self.multiplier:.1f}x',
            theme_text_color='Custom',
            text_color=[0.2, 0.8, 0.4, 1],
            font_size='10sp',
            halign='left',
            valign='center',
            bold=True,
            size_hint_y=0.6
        )

        info_container.add_widget(self.name_label)
        info_container.add_widget(self.amount_label)

        self.add_widget(self.avatar_widget)
        self.add_widget(info_container)

        self.bind(name=self.update_name)
        self.bind(amount=self.update_amount)
        self.bind(multiplier=self.update_multiplier)

    def create_avatar(self):
        try:
            avatar_urls = [
                f"https://i.pravatar.cc/40?img={random.randint(1, 70)}",
                f"https://robohash.org/{random.randint(1, 1000)}.png?set=set1&size=40x40",
                f"https://robohash.org/{random.randint(1, 1000)}.png?set=set2&size=40x40"
            ]

            avatar = AsyncImage(
                source=random.choice(avatar_urls),
                size_hint=(None, None),
                size=('40dp', '40dp'),
                allow_stretch=True,
                keep_ratio=True
            )
            return avatar

        except Exception:
            return MDLabel(
                text=self.name[0].upper() if self.name else 'A',
                theme_text_color='Custom',
                text_color=[0.2, 0.8, 0.4, 1],
                font_size='16sp',
                halign='center',
                valign='center',
                size_hint=(None, None),
                size=('40dp', '40dp'),
                bold=True
            )

    def format_currency_br(self, value):
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    def update_name(self, instance, value):
        self.name_label.text = value
        if hasattr(self.avatar_widget, 'text'):
            self.avatar_widget.text = value[0].upper() if value else 'A'

    def update_amount(self, instance, value):
        self.amount_label.text = f'ganhou {self.format_currency_br(value)} em {self.multiplier:.1f}x'

    def update_multiplier(self, instance, value):
        self.amount_label.text = f'ganhou {self.format_currency_br(self.amount)} em {value:.1f}x'
