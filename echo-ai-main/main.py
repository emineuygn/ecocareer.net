from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.uix.label import Label
import json
import os
import random

# Set default window size and color
Window.size = (400, 700)
Window.clearcolor = (0.1, 0.1, 0.2, 1)
Window.borderless = False  # Ensure window has borders

class UserData:
    @staticmethod
    def save_user(username, email):
        data = {
            'username': username,
            'email': email,
            'total_credits': 50,
            'messages_sent': 0
        }
        with open('user_data.json', 'w') as f:
            json.dump(data, f)
    
    @staticmethod
    def load_user():
        if os.path.exists('user_data.json'):
            with open('user_data.json', 'r') as f:
                return json.load(f)
        return None
    
    @staticmethod
    def update_credits(credits):
        data = UserData.load_user()
        if data:
            data['total_credits'] = credits
            with open('user_data.json', 'w') as f:
                json.dump(data, f)

# Bot responses with credit costs
BOT_RESPONSES = {
    "merhaba": {
        "cost": 1,
        "responses": [
            "Merhaba! Size nasıl yardımcı olabilirim?",
            "Hoş geldiniz! Bugün size nasıl yardımcı olabilirim?",
            "Merhaba! Benimle her konuda sohbet edebilirsiniz."
        ]
    },
    "nasılsın": {
        "cost": 2,
        "responses": [
            "İyiyim, teşekkür ederim! Siz nasılsınız?",
            "Çok iyiyim, siz nasılsınız?",
            "Harika! Umarım sizin de gününüz güzel geçiyordur."
        ]
    },
    "ne yapıyorsun": {
        "cost": 2,
        "responses": [
            "Size yardımcı olmak için buradayım. Nasıl yardımcı olabilirim?",
            "Sizinle sohbet etmek için bekliyordum. Nasıl yardımcı olabilirim?",
            "Her türlü konuda size destek olmaya hazırım."
        ]
    },
    "hava": {
        "cost": 3,
        "responses": [
            "Hava durumu hakkında konuşmak ister misiniz?",
            "Bugün gerçekten güzel bir gün, değil mi?",
            "Hava durumu her zaman ilginç bir konu!"
        ]
    },
    "müzik": {
        "cost": 3,
        "responses": [
            "Müzik harika bir konu! En sevdiğiniz tür nedir?",
            "Müzik ruhun gıdasıdır. Hangi sanatçıları dinlemeyi seversiniz?",
            "Müzik hakkında konuşmayı çok severim!"
        ]
    },
    "film": {
        "cost": 3,
        "responses": [
            "Film önerileri almak ister misiniz?",
            "Hangi tür filmleri seviyorsunuz?",
            "Son zamanlarda izlediğiniz güzel bir film var mı?"
        ]
    },
    "kitap": {
        "cost": 3,
        "responses": [
            "Kitap okumayı sever misiniz? Size önerilerde bulunabilirim.",
            "En son okuduğunuz kitap hangisiydi?",
            "Hangi tür kitapları okumayı tercih edersiniz?"
        ]
    },
    "spor": {
        "cost": 3,
        "responses": [
            "Spor yapmayı sever misiniz?",
            "Hangi spor dallarıyla ilgileniyorsunuz?",
            "Favori takımınız hangisi?"
        ]
    },
    "yemek": {
        "cost": 3,
        "responses": [
            "Yemek yapmayı sever misiniz?",
            "En sevdiğiniz yemek nedir?",
            "Size güzel tarifler önerebilirim!"
        ]
    },
    "teşekkür": {
        "cost": 1,
        "responses": [
            "Rica ederim! Başka nasıl yardımcı olabilirim?",
            "Ne demek, her zaman!",
            "Ben teşekkür ederim! Başka bir konuda yardıma ihtiyacınız var mı?"
        ]
    },
    "görüşürüz": {
        "cost": 1,
        "responses": [
            "Görüşmek üzere! İyi günler!",
            "Hoşça kalın! Tekrar görüşmek üzere!",
            "İyi günler! Yine beklerim!"
        ]
    },
    "default": {
        "cost": 2,
        "responses": [
            "Bu konu hakkında daha fazla bilgi verebilir misiniz?",
            "İlginç bir konu. Devam edin, sizi dinliyorum.",
            "Size bu konuda nasıl yardımcı olabilirim?"
        ]
    }
}

# Custom Toast implementation
class Toast(Label):
    def __init__(self, text, duration=3, **kwargs):
        super(Toast, self).__init__(**kwargs)
        self.text = text
        self.duration = duration
        self.size_hint = (None, None)
        self.height = 50
        self.opacity = 0
        self.background_color = (0.2, 0.2, 0.2, 0.9)
        self.color = (1, 1, 1, 1)
        self.padding = [20, 10]
        self.bind(texture_size=self._update_size)
        Window.bind(on_resize=self._update_pos)

    def _update_size(self, instance, size):
        self.width = size[0] + 40
        self._update_pos()

    def _update_pos(self, *args):
        self.pos = (Window.width/2 - self.width/2, 100)

    def show(self):
        app = App.get_running_app()
        app.root.add_widget(self)
        anim = Animation(opacity=1, duration=0.3) + Animation(opacity=1, duration=self.duration) + Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=lambda *args: app.root.remove_widget(self))
        anim.start(self)

def show_toast(text, duration=3):
    toast = Toast(text, duration)
    toast.show()

class WelcomeScreen(Screen):
    def on_enter(self):
        pass

class Message(BoxLayout):
    message_text = StringProperty('')
    is_user = BooleanProperty(False)
    cost = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Message, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)
        self.opacity = 0
        Animation(opacity=1, duration=0.3).start(self)

    def _finish_init(self, dt):
        self.bind(size=self._update_rect, pos=self._update_rect)
        self._update_rect(None, None)

    def _update_rect(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_user:
                Color(rgba=get_color_from_hex('#4C5BE0'))
            else:
                Color(rgba=(0.15, 0.15, 0.3, 1))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])

class LoginScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.focus_username())
    
    def focus_username(self):
        self.ids.username.focus = True
        self.ids.username.bind(on_text_validate=lambda x: self.focus_password())
        self.ids.password.bind(on_text_validate=lambda x: self.login())
    
    def focus_password(self):
        self.ids.password.focus = True
        self.ids.username.background_color = (0.15, 0.15, 0.3, 1)

    def validate_password(self, password):
        return len(password) <= 6

    def login(self, *args):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        
        if not username or not password:
            if not username:
                self.ids.username.background_color = (0.8, 0.2, 0.2, 1)
            if not password:
                self.ids.password.background_color = (0.8, 0.2, 0.2, 1)
            return
        
        if not self.validate_password(password):
            self.ids.password.background_color = (0.8, 0.2, 0.2, 1)
            self.ids.password.text = ""
            self.ids.password.hint_text = "Maximum 6 characters!"
            return
        
        try:
            # Save user data
            UserData.save_user(username, username + "@example.com")
            
            # Update chat screen
            chat_screen = self.manager.get_screen('chat')
            chat_screen.username = username
            chat_screen.credits = 50
            chat_screen.save_credits()
            
            # Switch to chat screen
            self.manager.current = 'chat'
            
        except Exception as e:
            print(f"Login error: {e}")
            # Reset fields on error
            self.ids.username.text = ""
            self.ids.password.text = ""
            self.ids.username.background_color = (0.8, 0.2, 0.2, 1)
            self.ids.password.background_color = (0.8, 0.2, 0.2, 1)
    
    def forgot_password(self):
        self.manager.current = 'forgot_password'

class ForgotPasswordScreen(Screen):
    def __init__(self, **kwargs):
        super(ForgotPasswordScreen, self).__init__(**kwargs)
        self.verification_code = None
    
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.focus_phone())
    
    def focus_phone(self):
        self.ids.phone.focus = True
        self.ids.phone.bind(on_text_validate=lambda x: self.send_code())
    
    def send_code(self):
        phone = self.ids.phone.text.strip()
        if phone and len(phone) == 10:
            self.verification_code = str(random.randint(100000, 999999))
            print(f"Verification code: {self.verification_code}")
            verification_screen = self.manager.get_screen('verification')
            verification_screen.verification_code = self.verification_code
            verification_screen.phone = phone
            self.manager.current = 'verification'
        else:
            self.ids.phone.background_color = (0.8, 0.2, 0.2, 1)
    
    def back_to_login(self):
        self.manager.current = 'login'

class VerificationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.verification_code = None
        self.countdown = 0
        self.phone_number = None
        Clock.schedule_interval(self.update_timer, 1)

    def send_verification_code(self):
        phone = self.ids.phone_number.text.strip()
        if not phone:
            return
        
        # Generate a random 6-digit code
        self.verification_code = str(random.randint(100000, 999999))
        self.phone_number = phone
        
        # Enable verification input and button
        self.ids.verification_code.disabled = False
        self.ids.verify_button.disabled = False
        
        # Start countdown timer (3 minutes)
        self.countdown = 180
        self.update_timer(0)
        
        # Show success message
        show_toast(f"Verification code sent to {phone}")

    def update_timer(self, dt):
        if self.countdown > 0:
            minutes = self.countdown // 60
            seconds = self.countdown % 60
            self.ids.timer_label.text = f'Resend code in {minutes:02d}:{seconds:02d}'
            self.countdown -= 1
        else:
            self.ids.timer_label.text = ''

    def verify_code(self):
        entered_code = self.ids.verification_code.text.strip()
        if entered_code == self.verification_code:
            # Code is correct, proceed to new password screen
            self.manager.current = 'new_password'
        else:
            # Show error message
            show_toast("Invalid verification code. Please try again.")

    def back_to_forgot(self):
        self.manager.current = 'forgot_password'

class NewPasswordScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.focus_password())
    
    def focus_password(self):
        self.ids.new_password.focus = True
        self.ids.new_password.bind(on_text_validate=lambda x: self.focus_confirm())
    
    def focus_confirm(self):
        self.ids.confirm_password.focus = True
        self.ids.confirm_password.bind(on_text_validate=lambda x: self.save_password())
    
    def validate_password(self, password):
        return len(password) <= 6
    
    def save_password(self, *args):
        new_pass = self.ids.new_password.text.strip()
        confirm_pass = self.ids.confirm_password.text.strip()
        
        if not self.validate_password(new_pass):
            self.ids.new_password.background_color = (0.8, 0.2, 0.2, 1)
            self.ids.new_password.text = ""
            self.ids.new_password.hint_text = "Maximum 6 characters!"
            return
        
        if new_pass and confirm_pass and new_pass == confirm_pass:
            self.manager.current = 'login'
        else:
            if not new_pass:
                self.ids.new_password.background_color = (0.8, 0.2, 0.2, 1)
            if not confirm_pass:
                self.ids.confirm_password.background_color = (0.8, 0.2, 0.2, 1)
            if new_pass != confirm_pass:
                self.ids.confirm_password.background_color = (0.8, 0.2, 0.2, 1)
                self.ids.confirm_password.text = ""
                self.ids.confirm_password.hint_text = "Passwords don't match!"

class ProfileScreen(Screen):
    user_data = DictProperty({
        'username': '',
        'email': '',
        'total_credits': 0,
        'messages_sent': 0
    })
    
    def on_enter(self):
        self.load_user_data()
    
    def load_user_data(self):
        if os.path.exists('user_data.json'):
            with open('user_data.json', 'r') as f:
                self.user_data.update(json.load(f))
    
    def save_user_data(self):
        with open('user_data.json', 'w') as f:
            json.dump(dict(self.user_data), f)
    
    def logout(self):
        self.manager.current = 'login'

class BuyCreditsScreen(Screen):
    def __init__(self, **kwargs):
        super(BuyCreditsScreen, self).__init__(**kwargs)
        self.credit_packages = [
            {'amount': 100, 'price': '10₺', 'description': 'Başlangıç Paketi'},
            {'amount': 250, 'price': '20₺', 'description': 'Standart Paket'},
            {'amount': 500, 'price': '35₺', 'description': 'Premium Paket'},
            {'amount': 1000, 'price': '60₺', 'description': 'VIP Paket'}
        ]
        self.selected_amount = 0
        self.selected_price = ''
        self.warning_shown = False
    
    def on_enter(self):
        # Reset form when entering the screen
        self.reset_form()
        if self.warning_shown:
            self.ids.warning_label.opacity = 1
    
    def show_credit_warning(self):
        self.warning_shown = True
        self.ids.warning_label.opacity = 1
    
    def select_package(self, amount, price):
        self.selected_amount = amount
        self.selected_price = price
        
        # Show the payment form
        self.ids.payment_form.opacity = 1
        self.ids.payment_form.disabled = False
        
        # Highlight selected package
        for child in self.ids.packages_grid.children:
            if hasattr(child, 'credits'):
                if int(child.credits) == amount:
                    child.background_color = (0.4, 0.5, 0.9, 1)
                else:
                    child.background_color = (0.15, 0.15, 0.3, 1)
        
        # Focus on card number input
        Clock.schedule_once(lambda dt: self.focus_card_number())
    
    def focus_card_number(self):
        self.ids.card_number.focus = True
    
    def validate_card(self):
        card_number = self.ids.card_number.text.strip().replace(' ', '')
        card_holder = self.ids.card_holder.text.strip()
        expiry_date = self.ids.expiry_date.text.strip()
        cvv = self.ids.cvv.text.strip()
        
        # Reset background colors
        self.ids.card_number.background_color = (0.15, 0.15, 0.3, 1)
        self.ids.card_holder.background_color = (0.15, 0.15, 0.3, 1)
        self.ids.expiry_date.background_color = (0.15, 0.15, 0.3, 1)
        self.ids.cvv.background_color = (0.15, 0.15, 0.3, 1)
        
        # Basic validation
        if not card_number or len(card_number) != 16 or not card_number.isdigit():
            self.ids.card_number.background_color = (0.8, 0.2, 0.2, 1)
            return False
        
        if not card_holder:
            self.ids.card_holder.background_color = (0.8, 0.2, 0.2, 1)
            return False
        
        if not expiry_date or len(expiry_date) != 5 or expiry_date[2] != '/':
            self.ids.expiry_date.background_color = (0.8, 0.2, 0.2, 1)
            return False
        
        if not cvv or len(cvv) != 3 or not cvv.isdigit():
            self.ids.cvv.background_color = (0.8, 0.2, 0.2, 1)
            return False
        
        return True
    
    def buy_credits(self):
        if self.selected_amount == 0:
            return
        
        if not self.validate_card():
            return
        
        chat_screen = self.manager.get_screen('chat')
        chat_screen.credits += self.selected_amount
        chat_screen.save_credits()
        
        profile_screen = self.manager.get_screen('profile')
        profile_screen.user_data['total_credits'] += self.selected_amount
        profile_screen.save_user_data()
        
        # Show success message
        self.ids.success_label.opacity = 1
        Animation(opacity=0, duration=2).start(self.ids.success_label)
        
        # Reset form after delay
        Clock.schedule_once(lambda dt: self.reset_form(), 2)
        Clock.schedule_once(lambda dt: self.return_to_chat(), 2.5)
    
    def reset_form(self):
        self.ids.card_number.text = ''
        self.ids.card_holder.text = ''
        self.ids.expiry_date.text = ''
        self.ids.cvv.text = ''
        self.selected_amount = 0
        self.selected_price = ''
        self.ids.payment_form.opacity = 0
        self.ids.payment_form.disabled = True
        
        # Reset package buttons
        for child in self.ids.packages_grid.children:
            if hasattr(child, 'credits'):
                child.background_color = (0.15, 0.15, 0.3, 1)
    
    def return_to_chat(self):
        self.manager.current = 'chat'
    
    def on_text_validate(self, instance):
        if instance == self.ids.card_number:
            self.ids.card_holder.focus = True
        elif instance == self.ids.card_holder:
            self.ids.expiry_date.focus = True
        elif instance == self.ids.expiry_date:
            self.ids.cvv.focus = True
        elif instance == self.ids.cvv:
            self.buy_credits()
    
    def format_expiry_date(self, instance, value):
        text = value.replace('/', '')[:4]
        if len(text) > 2:
            text = text[:2] + '/' + text[2:]
        instance.text = text
    
    def format_card_number(self, instance, value):
        text = ''.join(filter(str.isdigit, value))[:16]
        formatted = ' '.join([text[i:i+4] for i in range(0, len(text), 4)]).strip()
        instance.text = formatted

class UserInfoScreen(Screen):
    def __init__(self, **kwargs):
        super(UserInfoScreen, self).__init__(**kwargs)
    
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.focus_first_field())
    
    def focus_first_field(self):
        self.ids.email.focus = True
        # Bind Enter key events
        self.ids.email.bind(on_text_validate=lambda x: self.focus_next('password'))
        self.ids.password.bind(on_text_validate=lambda x: self.validate_and_continue())
    
    def focus_next(self, next_field):
        self.ids[next_field].focus = True
    
    def validate_and_continue(self, *args):
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()
        
        # Reset background colors
        self.ids.email.background_color = (0.15, 0.15, 0.3, 1)
        self.ids.password.background_color = (0.15, 0.15, 0.3, 1)
        
        # Basic validation
        if not email or '@' not in email:
            self.ids.email.background_color = (0.8, 0.2, 0.2, 1)
            return
        
        if not password or len(password) < 6:
            self.ids.password.background_color = (0.8, 0.2, 0.2, 1)
            self.ids.password.text = ""
            self.ids.password.hint_text = "Password must be at least 6 characters"
            return
        
        # Save user data
        user_data = {
            'username': email.split('@')[0],
            'email': email,
            'total_credits': 50,
            'messages_sent': 0
        }
        
        with open('user_data.json', 'w') as f:
            json.dump(user_data, f)
        
        # Update chat screen
        chat_screen = self.manager.get_screen('chat')
        chat_screen.username = user_data['username']
        chat_screen.credits = user_data['total_credits']
        chat_screen.save_credits()
        
        # Navigate to menu screen
        self.manager.current = 'menu'

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.menu_items = [
            {'text': 'Sohbete Başla', 'icon': 'assets/chat.png', 'screen': 'chat'},
            {'text': 'Profil', 'icon': 'assets/user.png', 'screen': 'profile'},
            {'text': 'Kredi Satın Al', 'icon': 'assets/coin.png', 'screen': 'buy_credits'},
            {'text': 'Çıkış', 'icon': 'assets/logout.png', 'screen': 'login'}
        ]
    
    def navigate(self, screen_name):
        self.manager.current = screen_name

    def on_enter(self):
        # Load user data and update credits display
        try:
            with open('user_data.json', 'r') as f:
                user_data = json.load(f)
                self.ids.credits_label.text = str(user_data.get('credits', 0))
        except:
            self.ids.credits_label.text = '0'

class ChatScreen(Screen):
    credits = NumericProperty(50)
    username = StringProperty('')
    
    def on_enter(self):
        # Load user data
        user_data = UserData.load_user()
        if user_data:
            self.username = user_data['username']
            self.credits = user_data.get('total_credits', 50)
        
        Clock.schedule_once(lambda dt: self.focus_message_input())
        self.load_messages()
        self.load_credits()
        
        # If this is first time entering chat, show welcome message
        if not os.path.exists('messages.json'):
            Clock.schedule_once(lambda dt: self.welcome_message(), 0.5)
    
    def focus_message_input(self):
        self.ids.message_input.focus = True
        # Bind Enter key to send message
        self.ids.message_input.bind(on_text_validate=self.send_message)
    
    def check_credits(self):
        if self.credits <= 10:
            self.add_message("Kredi miktarınız azalıyor! Daha fazla kredi satın almak ister misiniz?", False, 0)
        elif self.credits <= 0:
            self.add_message("Kredileriniz tükendi! Sohbete devam etmek için lütfen kredi satın alın.", False, 0)
            Clock.schedule_once(lambda dt: self.show_buy_credits(), 2)
    
    def show_buy_credits(self, *args):
        buy_credits_screen = self.manager.get_screen('buy_credits')
        buy_credits_screen.warning_shown = True
        self.manager.current = 'buy_credits'
    
    def welcome_message(self):
        welcome_text = f"Merhaba {self.username}! Size nasıl yardımcı olabilirim?"
        self.add_message(welcome_text, False, 0)
    
    def load_messages(self):
        if os.path.exists('messages.json'):
            with open('messages.json', 'r', encoding='utf-8') as f:
                messages = json.load(f)
                for msg in messages:
                    self.add_message(msg['text'], msg['is_user'], msg.get('cost', 0))
    
    def send_message(self, *args):
        message = self.ids.message_input.text.strip()
        if message:
            min_cost = min(topic['cost'] for topic in BOT_RESPONSES.values())
            if self.credits < min_cost:
                self.add_message("Üzgünüm, krediniz yetersiz! Lütfen daha fazla kredi satın alın.", False, 0)
                Clock.schedule_once(lambda dt: self.show_buy_credits(), 1)
                return
            
            self.add_message(message, True, 0)
            self.ids.message_input.text = ''
            
            Clock.schedule_once(lambda dt: self.bot_response(message.lower()), 0.5)
            Clock.schedule_once(lambda dt: self.focus_message_input(), 0.1)
    
    def bot_response(self, user_message):
        response_data = None
        cost = 0
        
        for key, data in BOT_RESPONSES.items():
            if key in user_message:
                response_data = data
                cost = data['cost']
                break
        
        if not response_data:
            response_data = BOT_RESPONSES['default']
            cost = response_data['cost']
        
        if self.credits < cost:
            self.add_message("Üzgünüm, bu yanıt için yeterli krediniz yok. Lütfen daha fazla kredi satın alın.", False, 0)
            return
        
        self.credits -= cost
        response = random.choice(response_data['responses'])
        
        self.add_message(response, False, cost)
        
        self.save_credits()
        UserData.update_credits(self.credits)
        self.check_credits()
    
    def add_message(self, text, is_user, cost=0):
        message = {
            'message_text': text,
            'is_user': is_user,
            'cost': cost
        }
        self.ids.chat_history.data.append(message)
        Clock.schedule_once(lambda dt: self.scroll_bottom())
        
        # Save message to file
        if os.path.exists('messages.json'):
            with open('messages.json', 'r', encoding='utf-8') as f:
                messages = json.load(f)
        else:
            messages = []
        
        messages.append({
            'text': text,
            'is_user': is_user,
            'cost': cost
        })
        
        with open('messages.json', 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False)
    
    def scroll_bottom(self):
        rv = self.ids.chat_history
        if rv.children:
            box = rv.children[0]
            if box.height > rv.height:
                rv.scroll_y = 0
    
    def save_credits(self):
        with open('credits.json', 'w') as f:
            json.dump({'credits': self.credits}, f)
        UserData.update_credits(self.credits)
    
    def load_credits(self):
        if os.path.exists('credits.json'):
            with open('credits.json', 'r') as f:
                data = json.load(f)
                self.credits = data.get('credits', 50)

class EchoaApp(App):
    def build(self):
        Builder.load_file('echoai.kv')
        
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(UserInfoScreen(name='user_info'))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(BuyCreditsScreen(name='buy_credits'))
        sm.add_widget(ForgotPasswordScreen(name='forgot_password'))
        sm.add_widget(VerificationScreen(name='verification'))
        return sm

if __name__ == '__main__':
    # Create necessary directories
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    # Create necessary files
    if not os.path.exists('messages.json'):
        with open('messages.json', 'w') as f:
            json.dump([], f)
    
    if not os.path.exists('credits.json'):
        with open('credits.json', 'w') as f:
            json.dump({'credits': 50}, f)
    
    if not os.path.exists('user_data.json'):
        with open('user_data.json', 'w') as f:
            json.dump({
                'username': '',
                'email': '',
                'total_credits': 50,
                'messages_sent': 0
            }, f)
    
    if not os.path.exists('user_info.json'):
        with open('user_info.json', 'w') as f:
            json.dump({}, f)
    
    # Create icons if they don't exist
    if not os.path.exists('assets/logo.png'):
        from create_robot_icon import create_logo, create_avatars
        create_logo()
        create_avatars()
    
    try:
        EchoaApp().run()
    except Exception as e:
        print(f"Application error: {e}")
        input("Press Enter to exit...") 