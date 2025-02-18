import flet as ft
from auth.authapp import AuthApp
from main import main as youtube_app
import logging
from utils import setup_logging

setup_logging()


def main(page: ft.Page):
    def auth_callback(auth_token):
        try:
            if auth_token:
                page.clean()
                youtube_app(page)
            else:
                page.add(ft.Text("token is None, 인증 실패"))
        except Exception as e:
            logging.error(f"Error in auth_callback: {str(e)}")
            page.add(ft.Text(f"오류가 발생했습니다: {str(e)}"))

    auth_app = AuthApp(auth_callback)
    auth_app.build(page)


if __name__ == "__main__":
    try:
        # ft.app(target=main, view=ft.WEB_BROWSER, port=8080, show_console=False)
        #ft.app(target=main, view=ft.FLET_APP)  # 데스크톱 모드로 실행
        #ft.app(target=main, port=8000, host="0.0.0.0") 
        ft.app(target=main)            
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        raise
