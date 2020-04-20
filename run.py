#!/usr/bin/env python
import asyncio
from app import beer_bot


async def main():
    beer_bot.run()


if __name__ == "__main__":
    asyncio.run(main())
