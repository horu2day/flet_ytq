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
    
    

if __name__ == "__main__":
    ft.app(target=main)