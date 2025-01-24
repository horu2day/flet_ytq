import flet as ft
import google_auth_oauthlib.flow
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
import logging
import socket
import webbrowser
from aiohttp import web

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
        page.title = "유튜브중독자"
        page.icon = get_resource_path("icon.ico")
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
                    ft.Text("로그인", size=32, weight=ft.FontWeight.BOLD),
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
            port = 8550
            # 다른 프로세스가 해당 포트를 사용하는지 확인
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('', port))
                sock.close()
            except OSError:
                # 8550 포트가 사용 중이면 8551 사용
                port = 8551
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.bind(('', port))
                    sock.close()
                except OSError:
                    raise Exception(f"포트 {port}를 사용할 수 없습니다.")

            redirect_uri = f'http://localhost:{port}/callback'
            # OAuth 2.0 flow 생성
            secrets_file = get_resource_path("client_secrets.json")
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                secrets_file,
                ['openid', 'https://www.googleapis.com/auth/userinfo.profile',
                    'https://www.googleapis.com/auth/userinfo.email'],  # 스코프 수정
                redirect_uri=redirect_uri
            )
            # 인증 URL 생성
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )

            async def callback_handler(request):
                query_params = request.query
                code = query_params.get("code", None)
                if code is None:
                    return web.Response(text="code가 없음.", status=400)
                try:
                    flow.fetch_token(code=code)
                    credentials = flow.credentials

                    # ID 토큰 검증 및 획득
                    request = requests.Request()
                    id_token.verify_oauth2_token(
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
                        return web.Response(text="로그인 성공, 창을 닫아주세요", content_type="text/html")
                    else:
                        self.status_text.value = "로그인 실패"
                        self.status_text.update()
                        self.auth_callback(None)  # 인증 실패 후 콜백 실행
                        return web.Response(text="Supabase 로그인 실패", status=400)
                except Exception as e:
                    logging.error(f"인증 오류: {e}")
                    self.status_text.value = "로그인 실패"
                    self.status_text.update()
                    self.auth_callback(None)
                    return web.Response(text=f"인증 오류 : {str(e)}", status=500)

            app = web.Application()
            app.add_routes([web.get('/callback', callback_handler)])
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, 'localhost', port)
            await site.start()

            webbrowser.open(authorization_url)

        except Exception as e:
            logging.error(f"Google 로그인 에러: {str(e)}")
            self.status_text.value = "로그인 실패"
            self.status_text.update()
            self.auth_callback(None)  # 인증 실패 후 콜백 실행

    def update_ui_after_login(self):
        # 로그인 성공 후 UI 업데이트
        self.status_text.value = f"환영합니다, {self.user.email}!"
        self.login_button.visible = False
        self.subscription_container.visible = True

        decoded_token = jwt.decode(
            self.token, JWT_SECRET, algorithms=['HS256'])
        subscription_type = decoded_token.get('subscription_type')  # 직접 값 가져오기

        # subscription_type 이 딕셔너리 형태라면 값을 얻어오고, 그렇지 않다면 그대로 사용
        if isinstance(subscription_type, dict):
            subscription_type = subscription_type.get("subscription_type")

        self.subscription_container.content.controls[1].value = f"현재 구독: {
            subscription_type.upper()}"

        self.premium_button.visible = True
        self.premium_button.disabled = subscription_type != 'premium'

        self.page.update()

    async def handle_premium_feature(self, e):
        if not self.token:
            return

        try:
            payload = eval(jwt.decode(self.token, JWT_SECRET,
                           algorithms=['HS256'])['subscription_type'])
            if payload['subscription_type'] == 'premium':
                # 프리미엄 기능 실행
                self.status_text.value = "프리미엄 기능 실행 중..."
            else:
                self.status_text.value = "프리미엄 구독이 필요합니다"
            self.status_text.update()
        except Exception:
            self.status_text.value = "오류가 발생했습니다"
            self.status_text.update()
