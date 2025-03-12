from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from tgbot.application.postgres.models import Promocode, PromocodeType, UserPromocode

class PromoGateway:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_valid_promo(self, promo_code: str):
        return await self.session.scalar(
            select(Promocode).where(
                Promocode.name == promo_code,
                Promocode.expires_at > datetime.utcnow(),
                Promocode.remaining_usages > 0
            )
        )

    async def is_promo_used(self, user_id: int, promo_id: int):
        return await self.session.scalar(
            select(UserPromocode).where(
                UserPromocode.user_id == user_id,
                UserPromocode.promocode_id == promo_id
            )
        )

    async def can_use_promo(self, user, promocode):
        return not (
            promocode.type == PromocodeType.referral_based and 
            user.amount_of_referrals < promocode.required_referrals
        )

    async def activate_promo(self, user, promocode):
        user.balance += promocode.reward
        promocode.remaining_usages -= 1
        self.session.add(UserPromocode(user_id=user.id, promocode_id=promocode.id))
        await self.session.commit()