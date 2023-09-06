from app.models.chat import Chat
from app.models.message import Message


async def create_initail_state():
    # create a dummy entry
    try:
        from app.models.user import User
        from app.services.hasher_service import HasherService

        user1 = await User.objects.create(
            username="user1",
            password=HasherService.get_password_hash('user1'),
            first_name="User",
            last_name="One",
        )
        user2 = await User.objects.create(
            username="user2",
            password=HasherService.get_password_hash('user2'),
            first_name="User",
            last_name="Two",
        )

        user3 = await User.objects.create(
            username="user3",
            password=HasherService.get_password_hash('user3'),
            first_name="User",
            last_name="Three",
        )

        chat = await Chat.objects.create(
            sender=user1,
            receiver=user2
        )

        await Message.objects.create(
            user=user1,
            chat=chat,
            content='Hello there'
        )

        await Message.objects.create(
            user=user2,
            chat=chat,
            content='Hello'
        )

        await Chat.objects.create(
            sender=user3,
            receiver=user1
        )
    except:
        pass
