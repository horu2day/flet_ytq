import flet as ft
from fastapi import Request
from auth.authapp import AuthApp
from main import main as youtube_app
import logging
from utils import setup_logging
# 구글 OAuth 라이브러리
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

setup_logging()

oauth_flow: Flow = None
auth_app_instance = None


def google_oauth_callback(req: Request):
    """
    http://127.0.0.1:8080/oauth2callback?code=... 으로 돌아오면,
    여기서 토큰 교환과 Supabase 로그인을 처리.
    """
    global oauth_flow, auth_app_instance

    code = req.query_params.get("code")
    if not code:
        return "No 'code' parameter. 구글 인증 실패."

    try:
        # 기존에 저장해둔 Flow 인스턴스가 있다고 가정
        oauth_flow.fetch_token(code=code)
        credentials = oauth_flow.credentials

        # ID 토큰 검증
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_requests.Request(),
            credentials.client_id
        )

        # 필요하다면, id_info에서 이메일 등 사용자 정보 확인 가능
        # 예: user_email = id_info["email"]

        # Supabase 로그인 로직
        # 여기는 비동기라고 가정되어 있으나, 예시에서는 동기로 처리
        # 실제로는 async/sync를 맞추어야 함
        token, user = auth_app_instance.auth_manager.sign_in_with_google_sync(
            credentials.id_token)
        # ↑ 위 함수가 실제로 있는지 확인하시고,
        #   필요하다면 auth_manager에서 await를 쓸 수도 있으므로
        #   구조 맞춰 조정하십시오.

        if token and user:
            # 성공
            auth_app_instance.token = token
            auth_app_instance.user = user

            # Flet 화면 업데이트를 위해, 나중에 페이지를 refresh하거나 콜백을 태워야 할 수도 있음
            auth_app_instance.auth_callback(token)

            # 콜백 종료 후 Flet 메인 화면으로 리디렉트
            return ft.RedirectResponse(url="/")
        else:
            auth_app_instance.auth_callback(None)
            return "로그인 실패. (Supabase sign_in_with_google 실패)"
    except Exception as e:
        logging.error(f"구글 OAuth 콜백 에러: {e}")
        auth_app_instance.auth_callback(None)
        return f"인증 실패: {e}"


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

    # AuthApp 인스턴스 생성
    global auth_app_instance
    auth_app_instance = AuthApp(auth_callback)
    auth_app_instance.build(page)


if __name__ == "__main__":
    try:
        # ft.app()에 routes 매개변수를 추가하여
        # "/oauth2callback" 라우트를 등록한다.
        #
        # 포트는 8080을 사용하므로, 구글 콘솔에는
        # "http://127.0.0.1:8080/oauth2callback"을 승인된 리디렉션 URI로 등록해야 함.
        ft.app(
            target=main,
            view=ft.WEB_BROWSER,
            port=8080
        )
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
