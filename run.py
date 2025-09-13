from __future__ import annotations
import os, sys, asyncio

# гарантируем, что корень проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import main

if __name__ == "__main__":
    asyncio.run(main())
