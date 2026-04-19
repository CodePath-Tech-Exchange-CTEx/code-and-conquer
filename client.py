import asyncio
import websockets
import json

GROUP_ID = "cs_genai"


async def async_input(prompt=""):
    return await asyncio.to_thread(input, prompt)


async def main():
    sender_id = await async_input("sender_id: ")
    uri = f"ws://127.0.0.1:8000/ws/{GROUP_ID}"

    async with websockets.connect(uri) as ws:
        print("connected")

        async def send_loop():
            while True:
                msg = await async_input()
                await ws.send(json.dumps({
                    "sender_id": sender_id,
                    "content": msg
                }))

        async def receive_loop():
            while True:
                data = await ws.recv()
                print(f"\nNEW: {data}")

        await asyncio.gather(send_loop(), receive_loop())


if __name__ == "__main__":
    asyncio.run(main())