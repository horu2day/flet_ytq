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
                page.add(ft.Text("인증 실패"))
        except Exception as e:
            logging.error(f"Error in auth_callback: {str(e)}")
            page.add(ft.Text(f"오류가 발생했습니다: {str(e)}"))

    auth_app = AuthApp(auth_callback)
    auth_app.build(page)


if __name__ == "__main__":
    try:
        ft.app(target=main, view=ft.WEB_BROWSER, port=8080)
    # ft.app(target=main)  # 데스크톱 모드로 실행
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        raise

##########################################################################################
# import flet as ft
# from auth.authapp import AuthApp
# from main import main as youtube_app

# def main(page: ft.Page):
#     def auth_callback(auth_token):
#         if auth_token:
#             page.clean()  # 페이지 초기화
#             youtube_app(page)  # 유튜브 앱 실행
#         else:
#             page.add(ft.Text("인증 실패"))  # 인증 실패시 에러 메시지 출력

#     auth_app = AuthApp(auth_callback)
#     auth_app.build(page)

# def handler(event, context):
#      # Vercel 환경에서 실행되는 경우
#     page = ft.Page()
#     main(page) # page 를 직접 넘겨주고, ft.app()를 호출하지 않음.

#     return {
#         'statusCode': 200,
#         'body': "Flet app initialized"
#     }
# if __name__ == "__main__":
#     # 개발 환경에서 실행되는 경우
#      ft.app(target=main, view=ft.WEB_BROWSER)
