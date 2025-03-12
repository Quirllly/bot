from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from tgbot.application.postgres.models import WithdrawalRequest, User
from uuid import UUID
class WithdrawGateway:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_request(
        self,
        user_id: UUID,
        amount: float,
        gift_type: str
    ) -> WithdrawalRequest:
        request = WithdrawalRequest(
            user_id=user_id,
            amount=amount,
            gift_type=gift_type
        )
        self.session.add(request)
        await self.session.commit()
        return request

    async def get_user_requests(self, user_id: UUID) -> list[WithdrawalRequest]:
        result = await self.session.execute(
            select(WithdrawalRequest)
            .where(WithdrawalRequest.user_id == user_id)
            .order_by(WithdrawalRequest.created_at.desc())
        )
        return result.scalars().all()

    async def has_pending_requests(self, user_id: UUID) -> bool:
        result = await self.session.scalar(
            select(WithdrawalRequest)
            .where(
                WithdrawalRequest.user_id == user_id,
                WithdrawalRequest.status == 'pending'
            )
            .exists()
            .select()
        )
        return result
    
    async def get_all_pending(self):
        result = await self.session.execute(
            select(WithdrawalRequest)
            .where(WithdrawalRequest.status == 'pending')
            .order_by(WithdrawalRequest.created_at)
        )
        return result.scalars().all()

    async def update_request(self, request_id: UUID, status: str):
        request = await self.session.get(WithdrawalRequest, request_id)
        request.status = status
        await self.session.commit()
        return request
    async def get_request_by_id(self, request_id: UUID) -> WithdrawalRequest | None:
        return await self.session.get(WithdrawalRequest, request_id)
    
    async def get_user_by_request(self, request: WithdrawalRequest) -> User:
        result = await self.session.execute(
            select(User).where(User.id == request.user_id)
        )
        return result.scalar_one()