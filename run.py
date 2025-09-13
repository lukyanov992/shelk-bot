#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from src.bot import create_app

async def main():
    dp, bot, run_polling_forever = await create_app()
    print("✅ Colizeum Bot (aiogram) is running…")
    await run_polling_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Stopped by user")
