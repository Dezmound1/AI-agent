"""
Идемпотентное заполнение БД тестовыми пользователями и комментариями.
Запускается из docker-entrypoint после миграций.
"""

from __future__ import annotations

import sys
import uuid

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Comment, CommentCharacter, CommentSentiment, User

USER_ANNA = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa01")
USER_BORIS = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb02")


def seed() -> None:
    if not settings.seed_mock_on_start:
        print("seed_mock_data: SEED_MOCK_ON_START=false, skip", file=sys.stderr)
        return

    engine = create_engine(settings.database_url_sync)

    with Session(engine) as session:
        existing = session.scalar(select(func.count()).select_from(User))
        if existing and existing > 0:
            print("seed_mock_data: данные уже есть, пропуск")
            return

        anna = User(
            id=USER_ANNA,
            email="anna.mock@example.local",
            display_name="Анна",
        )
        boris = User(
            id=USER_BORIS,
            email="boris.mock@example.local",
            display_name="Борис",
        )
        session.add_all([anna, boris])

        session.add_all(
            [
                Comment(
                    user_id=USER_ANNA,
                    body="Добрый день. Прошу уточнить сроки поставки по договору №12.",
                    character=CommentCharacter.FORMAL,
                    sentiment=CommentSentiment.NEUTRAL,
                ),
                Comment(
                    user_id=USER_ANNA,
                    body="Ого, наконец-то завелось!!! Спасибо огромное 🎉",
                    character=CommentCharacter.EMOTIONAL,
                    sentiment=CommentSentiment.POSITIVE,
                ),
                Comment(
                    user_id=USER_ANNA,
                    body="Ну да, конечно, «работает» — раз в пятницу вечером, классика.",
                    character=CommentCharacter.SARCASTIC,
                    sentiment=CommentSentiment.NEGATIVE,
                ),
                Comment(
                    user_id=USER_BORIS,
                    body="stack trace: NullPointerException at line 404, версия 2.3.1",
                    character=CommentCharacter.TECHNICAL,
                    sentiment=CommentSentiment.NEGATIVE,
                ),
                Comment(
                    user_id=USER_BORIS,
                    body="Короче, норм тема, но ценник кусается и поддержка так себе.",
                    character=CommentCharacter.CASUAL,
                    sentiment=CommentSentiment.MIXED,
                ),
            ]
        )
        session.commit()

    print("seed_mock_data: добавлены мок-пользователи и комментарии")


if __name__ == "__main__":
    seed()
