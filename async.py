import asyncio

async def ws(f):
    print('ws')


async def callback(*args):
    print('call back')


async def create():
    tasks = [
        asyncio.create_task(
            ws(callback)
        )
    ]

    await asyncio.wait(tasks)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(create())