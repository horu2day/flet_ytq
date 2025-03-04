import os
import jwt
from datetime import datetime, timedelta, timezone
from supabase import create_client

# Supabase 설정
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
JWT_SECRET = os.environ.get("JWT_SECRET")

class AuthManager:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    async def sign_in_with_google(self, id_token: str):
        try:
            auth_response = await self.supabase.auth.sign_in_with_id_token({
                "provider": "google",
                "token": id_token
            })

            user = auth_response.user
            user_id = user.id
            #user.user_metadata['is_paid_member'] = True #metadata 업데이트 막음

            # 먼저 메타데이터 존재 여부 확인
            metadata = await self.supabase.from_('user_metadata')\
                .select('subscription_type, expiry_date')\
                .eq('user_id', user_id)\
                .execute()

            if not metadata.data:
                # 신규 사용자라면 trial_period 가져와서 적용
                period_data = await self.supabase.from_(
                    'settings').select('trial_period').execute()
                if period_data.data:  # period_data.data 가 비어있지 않은지 확인
                    trial_period = period_data.data[0].get(
                        'trial_period', 30)  # 첫번째 요소에서 값을 가져옴
                else:
                    trial_period = 30  # 만약 결과가 없다면 기본 값 30 으로 설정
                expiry_date = datetime.now(timezone.utc) + timedelta(days=trial_period)
                await self.supabase.from_('user_metadata').insert({
                    'user_id': user_id,
                    'subscription_type': 'premium',
                    'expiry_date': expiry_date.isoformat()
                }).execute()

            metadata = await self.supabase.from_('user_metadata')\
                .select('subscription_type, expiry_date')\
                .eq('user_id', user_id)\
                .maybe_single()\
                .execute()

            # 현재 시간과 만료일 비교해서 subscription_type 결정
            current_subscription = 'free'
            if metadata.data: # 데이터가 있을때만 처리
              expiry_date = datetime.fromisoformat(
                  metadata.data['expiry_date'].replace('Z', '+00:00'))
              current_time = datetime.now(timezone.utc)

              if expiry_date > current_time:
                  current_subscription = metadata.data['subscription_type']
            custom_token = jwt.encode({
                'user_id': user_id,
                'subscription_type': current_subscription,
                'exp': datetime.now(timezone.utc) + timedelta(days=24)
            }, JWT_SECRET, algorithm="HS256")

            return custom_token, user
        except Exception as e:
            print(f"로그인 에러: {str(e)}")
            return None, None