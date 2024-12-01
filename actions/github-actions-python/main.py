#每个任务在30秒后，github action自动停止，所以需要定期重启
# nohup /home/wth000/miniconda3/bin/python /home/wth000/gitee/blockchain/[grass挖矿]/no_proxy.py
# -*- coding: utf-8 -*-
import asyncio
import random
import ssl
import json
import time
import uuid

import websockets
from loguru import logger


async def connect_to_wss(user_id):
    device_id = str(uuid.uuid4())
    logger.info(device_id)
    while True:
        try:
            await asyncio.sleep(random.randint(1, 10) / 10)
            custom_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            }
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            uri = "wss://proxy.wynd.network:4650/"
            server_hostname = "proxy.wynd.network"
            async with websockets.connect(uri, ssl=ssl_context, 
                                        #   extra_headers=custom_headers,#linux系统上没这个参数
                                          server_hostname=server_hostname
                                          ) as websocket:
                async def send_ping():
                    while True:
                        send_message = json.dumps(
                            {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}})
                        logger.debug(send_message)
                        await websocket.send(send_message)
                        await asyncio.sleep(20)

                await asyncio.sleep(1)
                asyncio.create_task(send_ping())

                while True:
                    response = await websocket.recv()
                    message = json.loads(response)
                    logger.info(message)
                    if message.get("action") == "AUTH":
                        auth_response = {
                            "id": message["id"],
                            "origin_action": "AUTH",
                            "result": {
                                "browser_id": device_id,
                                "user_id": user_id,
                                "user_agent": custom_headers['User-Agent'],
                                "timestamp": int(time.time()),
                                "device_type": "extension",
                                "version": "2.5.0"
                            }
                        }
                        logger.debug(auth_response)
                        await websocket.send(json.dumps(auth_response))

                    elif message.get("action") == "PONG":
                        pong_response = {"id": message["id"], "origin_action": "PONG"}
                        logger.debug(pong_response)
                        await websocket.send(json.dumps(pong_response))
        except Exception as e:
            logger.error(e)


async def main():
    # TODO 修改user_id
    # _user_id = '2fjMIhXjkB5HId9CWLxcQpyhD94'#localStorage.getItem('userId')
    _user_id = "2lgiemEtbb0twLzEUHiJ8nCCiHm"#子账户
    await connect_to_wss(_user_id)


if __name__ == '__main__':
    # 运行主函数【使用异步可以规避github action的时间限制问题】
    asyncio.run(main())
