import flet as ft
import google_auth_oauthlib.flow
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt


from auth.authmanager import JWT_SECRET, AuthManager
from utils import get_resource_path

class AuthApp:
    def __init__(self, auth_callback):
        self.auth_manager = AuthManager()
        self.user = None
        self.token = None
        self.auth_callback = auth_callback

    def build(self, page: ft.Page):
        self.page = page
        page.title = "로그인"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window.width = 400
        page.window.height = 600

        # 상태 표시 텍스트
        self.status_text = ft.Text("", size=16)
        
        # 로그인 버튼
        self.login_button = ft.ElevatedButton(
            text="Google로 로그인",
            icon=ft.Icons.LOGIN,
            on_click=self.handle_google_login,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.DEFAULT: ft.Colors.WHITE,
                    ft.ControlState.HOVERED: ft.Colors.WHITE,
                },
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.BLUE,
                    ft.ControlState.HOVERED: ft.Colors.BLUE_700,
                },
            )
        )

        # 구독 상태 컨테이너
        self.subscription_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("구독 상태", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("", size=16),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            visible=False
        )

        # 프리미엄 기능 버튼
        self.premium_button = ft.ElevatedButton(
            text="프리미엄 기능 사용",
            on_click=self.handle_premium_feature,
            visible=False
        )

        # 메인 컨테이너
        main_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Login", size=32, weight=ft.FontWeight.BOLD),
                    self.status_text,
                    self.login_button,
                    self.subscription_container,
                    self.premium_button
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            padding=ft.padding.all(30),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_100,
            )
        )

        page.add(main_container)
        page.update()

    async def handle_google_login(self, e):
        self.status_text.value = "로그인 중..."
        self.status_text.update()
        try:
            port = 8080
            # 다른 프로세스가 해당 포트를 사용하는지 확인
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('', port))
                sock.close()
            except OSError:
                # 8080 포트가 사용 중이면 8081 사용
                port = 8081
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.bind(('', port))
                    sock.close()
                except OSError:
                    raise Exception(f"포트 {port}를 사용할 수 없습니다.")
            # OAuth 2.0 flow 생성
            secrets_file = get_resource_path("client_secrets.json")
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
               secrets_file , 
                ['openid', 'https://www.googleapis.com/auth/userinfo.email'],
                redirect_uri="https://isircfpmirzzkotuyybd.supabase.co/auth/v1/callback"
            )
            auth_url, _ = flow.authorization_url()
            # 로컬 서버로 인증
            credentials = flow.run_local_server(port=port)
            
            # ID 토큰 검증 및 획득
            request = requests.Request()
            id_info = id_token.verify_oauth2_token(
                credentials.id_token, 
                request, 
                credentials.client_id
            )
            # Supabase 로그인
            token, user = await self.auth_manager.sign_in_with_google(credentials.id_token)
            
            if token and user:
                self.token = token
                self.user = user
                self.update_ui_after_login()
                self.auth_callback(token)  # 인증 성공 후 콜백 실행
            else:
                self.status_text.value = "로그인 실패"
                self.status_text.update()
                self.auth_callback(None)  # 인증 실패 후 콜백 실행
        except Exception as e:
            print(f"Google 로그인 에러: {str(e)}")
            self.status_text.value = "로그인 실패"
            self.status_text.update()
            self.auth_callback(None)  # 인증 실패 후 콜백 실행
    def update_ui_after_login(self):
        # 로그인 성공 후 UI 업데이트
        self.status_text.value = f"환영합니다, {self.user.email}!"
        self.login_button.visible = False
        self.subscription_container.visible = True
        
        subscription_data  = eval(jwt.decode(self.token, JWT_SECRET, algorithms=['HS256'])['subscription_type'])
        self.subscription_container.content.controls[1].value = f"현재 구독: {subscription_data['subscription_type'].upper()}"
        
        self.premium_button.visible = True
        self.premium_button.disabled = subscription_data['subscription_type'] != 'premium'
        
        self.page.update()

    async def handle_premium_feature(self, e):
        if not self.token:
            return
            
        try:
            payload = eval(jwt.decode(self.token, JWT_SECRET, algorithms=['HS256'])['subscription_type'])
            if payload['subscription_type'] == 'premium':
                # 프리미엄 기능 실행
                self.status_text.value = "프리미엄 기능 실행 중..."
            else:
                self.status_text.value = "프리미엄 구독이 필요합니다"
            self.status_text.update()
        except Exception:
            self.status_text.value = "오류가 발생했습니다"
            self.status_text.update()