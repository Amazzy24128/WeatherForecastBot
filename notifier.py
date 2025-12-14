"""
通知模块 - Server酱推送
"""
import requests
import logging

logger = logging.getLogger(__name__)

class ServerChanNotifier:
    def __init__(self, sendkey: str):
        self.sendkey = sendkey
        self.api_url = f"https://sctapi.ftqq.com/{sendkey}.send"
    
    def send(self, title: str, content: str) -> bool:
        """
        发送通知
        
        Args:
            title: 通知标题
            content: 通知内容（支持Markdown）
        
        Returns:
            bool:  是否发送成功
        """
        try:
            data = {
                "title": title,
                "desp": content
            }
            
            response = requests.post(self.api_url, data=data, timeout=10)
            result = response.json()
            
            if result.get('code') == 0:
                logger.info("Server酱通知发送成功")
                return True
            else:
                logger. error(f"Server酱通知发送失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"发送Server酱通知异常: {e}")
            return False
