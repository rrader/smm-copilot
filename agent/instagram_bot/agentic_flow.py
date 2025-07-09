from openai import OpenAI
from .config import OPENAI_API_KEY
from typing import Callable, Awaitable
import asyncio

client = OpenAI(api_key=OPENAI_API_KEY)


async def agentic_flow(message: str, chat_data: dict, reply_to_message: Callable[[str], Awaitable[None]]) -> None:
    pass


if __name__ == "__main__":
    async def reply_to_message(message: str) -> None:
        print(message)

    async def main():
        while True:
            message = input("Enter a message: ")
            await agentic_flow(message, {}, reply_to_message)

    asyncio.run(main())
