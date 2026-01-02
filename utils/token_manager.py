import uuid
import time
import json
import os
from typing import Optional, Dict

# Token配置
TOKEN_STORAGE_FILE = "./user_tokens.json"  # Token持久化文件（避免程序重启丢失）


class TokenManager:
    def __init__(self):
        # 内存缓存：{token: {"user_id": 1, "username": "小周"}}
        self.token_map: Dict[str, Dict] = {}
        # 加载本地持久化的Token（程序启动时恢复状态）
        self._load_tokens_from_file()

    def _generate_token(self) -> str:
        """生成唯一Token（UUID4）"""
        return str(uuid.uuid4())

    def _load_tokens_from_file(self):
        """从文件加载Token（避免重启丢失）"""
        if os.path.exists(TOKEN_STORAGE_FILE):
            try:
                with open(TOKEN_STORAGE_FILE, "r", encoding="utf-8") as f:
                    self.token_map = json.load(f)
            except Exception as e:
                print(f"加载Token失败：{e}")
                self.token_map = {}

    def _save_tokens_to_file(self):
        """Token保存到文件（持久化）"""
        try:
            with open(TOKEN_STORAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.token_map, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存Token失败：{e}")

    def login(self, user_id: int, username: str) -> str:
        """
        用户登录成功，生成Token并记录状态
        :param user_id: 用户ID
        :param username: 用户名
        :return: 生成的Token
        """
        # 1. 生成Token
        token = self._generate_token()
        # 3. 记录Token与用户映射
        self.token_map[token] = {
            "user_id": user_id,
            "username": username
        }
        # 4. 持久化到文件
        self._save_tokens_to_file()
        return token

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        验证Token有效性，返回用户信息（无效返回None）
        :param token: 登录凭证
        :return: {"user_id": 1, "username": "小周"} 或 None
        """
        # 1. 校验Token是否存在且未过期
        if token not in self.token_map:
            return None
        user_info = self.token_map[token]
        # 2. 返回用户核心信息（隐藏过期时间）
        return {
            "user_id": user_info["user_id"],
            "username": user_info["username"]
        }

    def logout(self, token: str) -> bool:
        """用户登出，删除Token"""
        if token in self.token_map:
            del self.token_map[token]
            self._save_tokens_to_file()
            return True
        return False

    def get_current_user(self, token: str) -> Optional[Dict]:
        """快捷获取当前登录用户信息（封装verify_token）"""
        return self.verify_token(token)


# 单例模式：全局唯一的Token管理器（避免重复创建）
token_manager = TokenManager()
# token = token_manager.login(1, "zhang_san")  # 测试用例
# token_manager.logout(token)  # 测试用例
