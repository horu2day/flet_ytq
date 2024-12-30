import flet as ft
from auth.authapp import AuthApp
from main import main as youtube_app

def main(page: ft.Page):
    def auth_callback(auth_token):
        if auth_token:
            page.clean()  # 페이지 초기화
            youtube_app(page)  # 유튜브 앱 실행
        else:
            page.add(ft.Text("인증 실패"))  # 인증 실패시 에러 메시지 출력
    
    auth_app = AuthApp(auth_callback)
    auth_app.build(page)

def handler(event, context):
    # Vercel 환경에서 실행되는 경우
    ft.app(target=main, view=ft.WEB_BROWSER, server_port=0) # 서버 포트 0으로 설정
    
    return {
        'statusCode': 200,
        'body': "Flet app initialized"
    }
if __name__ == "__main__":
    # 개발 환경에서 실행되는 경우
     ft.app(target=main, view=ft.WEB_BROWSER)