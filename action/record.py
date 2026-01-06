# -*- coding: utf-8 -*-
"""
讯飞语音听写即时听写API (Ifasr)
API文档: https://www.xfyun.cn/doc/asr/voicedictation/API.html
"""
import base64
import hmac
import json
import os
import time
import random
import string
import requests
import urllib.parse
import datetime
import wave
import re
import warnings

# 忽略SSL验证警告（生产环境建议开启验证）
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# 讯飞API基础配置
LFASR_HOST = "https://office-api-ist-dx.iflyaisol.com"
API_UPLOAD = "/v2/upload"
API_GET_RESULT = "/v2/getResult"


class XfyunAsrClient:
    def __init__(self, appid, access_key_id, access_key_secret, audio_file_path):
        self.appid = appid
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.audio_file_path = self._check_audio_path(audio_file_path)
        self.audio_duration = self._get_audio_duration_ms()  # 获取音频时长（毫秒，整数）
        self.order_id = None
        self.signature_random = self._generate_random_str()
        self.last_base_string = ""  # 签名原始串（编码后）
        self.last_signature = ""    # 最终签名
        self.upload_url = ""        # 最终生成的请求URL

    def _check_audio_path(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"音频文件不存在：{path}")
        # 支持WAV和MP3格式
        ext = os.path.splitext(path)[1].lower()
        if ext not in [".wav", ".mp3"]:
            raise ValueError(f"当前代码仅支持WAV和MP3格式音频，您的文件格式为：{ext}")
        return os.path.abspath(path)

    def _generate_random_str(self, length=16):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def _get_local_time_with_tz(self):
        """生成带时区偏移的本地时间（格式：yyyy-MM-dd'T'HH:mm:ss±HHmm）"""
        local_now = datetime.datetime.now()
        tz_offset = local_now.astimezone().strftime('%z')  # 输出格式：+0800 或 -0500
        return f"{local_now.strftime('%Y-%m-%dT%H:%M:%S')}{tz_offset}"

    def _get_audio_duration_ms(self):
        """
        获取音频时长（毫秒，整数）
        支持WAV和MP3格式
        """
        ext = os.path.splitext(self.audio_file_path)[1].lower()

        if ext == ".wav":
            # WAV格式：使用Python内置wave模块
            try:
                with wave.open(self.audio_file_path, 'rb') as wav_file:
                    n_frames = wav_file.getnframes()
                    sample_rate = wav_file.getframerate()
                    duration_ms = int(round(n_frames / sample_rate * 1000))
                    return duration_ms
            except wave.Error as e:
                raise Exception(f"WAV文件解析失败：{str(e)}，请确认文件为标准WAV格式（非损坏、非压缩）")
        elif ext == ".mp3":
            # MP3格式：使用mutagen库或估算
            try:
                from mutagen.mp3 import MP3
                audio = MP3(self.audio_file_path)
                duration_seconds = audio.info.length
                return int(duration_seconds * 1000)
            except ImportError:
                # 如果没有mutagen，使用粗略估算（假设128kbps）
                file_size = os.path.getsize(self.audio_file_path)
                # MP3文件：大小(bytes) / 128(kbps) / 8 = 秒数
                estimated_seconds = file_size / (128 * 1024 / 8)
                print(f"警告：未安装mutagen库，使用估算时长。建议安装：pip install mutagen")
                return int(estimated_seconds * 1000)
            except Exception as e:
                raise Exception(f"MP3文件解析失败：{str(e)}")
        else:
            raise Exception(f"不支持的音频格式：{ext}")

    def generate_signature(self, params):
        """生成签名（根据文档要求：对key和value都进行url encode后生成baseString）"""
        # 排除signature参数，按参数名自然排序（与Java TreeMap一致）
        sign_params = {k: v for k, v in params.items() if k != "signature"}
        sorted_params = sorted(sign_params.items(), key=lambda x: x[0])

        # 构建baseString：对key和value都进行URL编码
        base_parts = []
        for k, v in sorted_params:
            if v is not None and str(v).strip() != "":
                encoded_key = urllib.parse.quote(k, safe='')  # 参数名编码
                encoded_value = urllib.parse.quote(str(v), safe='')  # 参数值编码
                base_parts.append(f"{encoded_key}={encoded_value}")

        self.last_base_string = "&".join(base_parts)

        # HMAC-SHA1加密 + Base64编码
        hmac_obj = hmac.new(
            self.access_key_secret.encode("utf-8"),
            self.last_base_string.encode("utf-8"),
            digestmod="sha1"
        )
        self.last_signature = base64.b64encode(hmac_obj.digest()).decode("utf-8")
        return self.last_signature

    def upload_audio(self):
        """上传音频文件"""
        # 1. 基础参数准备（duration字段为毫秒整数）
        audio_size = str(os.path.getsize(self.audio_file_path))  # 音频文件大小（字节）
        audio_name = os.path.basename(self.audio_file_path)      # 音频文件名
        date_time = self._get_local_time_with_tz()               # 带时区的本地时间
        print(f"音频文件：{audio_name}")
        print(f"文件大小：{audio_size} 字节")
        print(f"音频时长：{self.audio_duration} 毫秒")

        # 2. 构建URL参数 - duration字段为毫秒整数
        url_params = {
            "appId": self.appid,
            "accessKeyId": self.access_key_id,
            "dateTime": date_time,
            "signatureRandom": self.signature_random,
            "fileSize": audio_size,
            "fileName": audio_name,
            "language": "autodialect",
            "duration": str(self.audio_duration)  # 音频时长（毫秒，整数字符串）
        }

        # 3. 生成签名（duration参数参与签名计算）
        signature = self.generate_signature(url_params)
        if not signature:
            raise Exception("签名生成失败，结果为空")

        # 4. 构建请求头
        headers = {
            "Content-Type": "application/octet-stream",
            "signature": signature
        }

        # 5. 构建最终请求URL
        encoded_params = []
        for k, v in url_params.items():
            encoded_key = urllib.parse.quote(k, safe='')
            encoded_v = urllib.parse.quote(str(v), safe='')
            encoded_params.append(f"{encoded_key}={encoded_v}")
        self.upload_url = f"{LFASR_HOST}{API_UPLOAD}?{'&'.join(encoded_params)}"

        # 6. 读取音频文件并发送POST请求
        with open(self.audio_file_path, "rb") as f:
            audio_data = f.read()

        try:
            response = requests.post(
                url=self.upload_url,
                headers=headers,
                data=audio_data,
                timeout=30,
                verify=False  # 测试环境关闭SSL验证
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"上传请求网络失败：{str(e)}")

        # 7. 解析响应结果
        try:
            result = json.loads(response.text)
            print("上传结果：", result)
        except json.JSONDecodeError:
            raise Exception(f"API返回非JSON数据：{response.text}")

        # 8. 处理API业务错误
        if result.get("code") != "000000":
            raise Exception(
                f"上传失败（API错误）：\n"
                f"错误码：{result.get('code')}\n"
                f"错误描述：{result.get('descInfo', '未知错误')}\n"
                f"请求URL：{self.upload_url}\n"
                f"签名原始串：{self.last_base_string}\n"
                f"签名值：{self.last_signature}"
            )

        # 9. 上传成功，记录订单ID
        self.order_id = result["content"]["orderId"]
        print(f"上传成功！订单ID：{self.order_id}")
        return result

    def get_transcribe_result(self):
        """查询音频转写结果（轮询直到完成/超时）"""
        if not self.order_id:
            print("未检测到订单ID，自动执行上传流程...")
            self.upload_audio()
        if not self.order_id:
            raise Exception("未获取到订单ID，无法查询转写结果")

        # 构建查询参数
        query_params = {
            "appId": self.appid,
            "accessKeyId": self.access_key_id,
            "dateTime": self._get_local_time_with_tz(),
            "ts": str(int(time.time())),  # 秒级时间戳
            "orderId": self.order_id,
            "signatureRandom": self.signature_random
        }

        # 生成查询签名
        query_signature = self.generate_signature(query_params)
        query_headers = {
            "Content-Type": "application/json",
            "signature": query_signature
        }

        # 构建查询URL
        encoded_query_params = []
        for k, v in query_params.items():
            encoded_key = urllib.parse.quote(k, safe='')
            encoded_v = urllib.parse.quote(str(v), safe='')
            encoded_query_params.append(f"{encoded_key}={encoded_v}")
        query_url = f"{LFASR_HOST}{API_GET_RESULT}?{'&'.join(encoded_query_params)}"

        # 轮询查询
        max_retry = 100
        retry_count = 0
        while retry_count < max_retry:
            try:
                response = requests.post(
                    url=query_url,
                    headers=query_headers,
                    data=json.dumps({}),
                    timeout=15,
                    verify=False
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise Exception(f"查询请求网络失败：{str(e)}")

            try:
                result = json.loads(response.text)
                print(result)
            except json.JSONDecodeError:
                raise Exception(f"查询响应非JSON数据：{response.text}")

            if result.get("code") != "000000":
                raise Exception(f"查询失败（API错误）：{result.get('descInfo', '未知错误')}")

            # 转写状态：3=处理中，4=完成
            process_status = result["content"]["orderInfo"]["status"]
            if process_status == 4:
                print("转写完成！")
                return result
            elif process_status != 3:
                raise Exception(f"转写异常：状态码={process_status}，描述={result.get('descInfo')}")

            # 处理中，等待10秒后重试
            retry_count += 1
            print(f"转写处理中（已查询{retry_count}/{max_retry}次），10秒后再次查询...")
            time.sleep(10)

        raise Exception(f"查询超时：已重试{max_retry}次，订单ID：{self.order_id}")


def parse_order_result(api_response):
    """
    解析完整的API响应，提取orderResult中的所有w字段内容并拼接

    参数:
        api_response: 完整的API响应字典
    返回:
        拼接后的文本字符串
    """
    try:
        # 从API响应中获取orderResult字段
        order_result_str = api_response.get('content', {}).get('orderResult', '{}')

        # 处理转义字符问题
        cleaned_str = re.sub(r'\\\\', r'\\', order_result_str)

        # 解析orderResult字符串为JSON对象
        order_result = json.loads(cleaned_str)

        # 提取所有w字段的值
        w_values = []

        # 遍历lattice数组
        if 'lattice' in order_result:
            for lattice_item in order_result['lattice']:
                if 'json_1best' in lattice_item:
                    # 解析json_1best字段
                    json_1best = json.loads(lattice_item['json_1best'])

                    # 处理st对象
                    if 'st' in json_1best and 'rt' in json_1best['st']:
                        for rt_item in json_1best['st']['rt']:
                            if 'ws' in rt_item:
                                for ws_item in rt_item['ws']:
                                    if 'cw' in ws_item:
                                        for cw_item in ws_item['cw']:
                                            if 'w' in cw_item:
                                                w_values.append(cw_item['w'])

        # 拼接所有w值
        return ''.join(w_values)

    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return ""
    except Exception as e:
        print(f"处理过程中出错: {e}")
        return ""


def transcribe_audio(audio_file_path):
    """
    语音识别函数，将音频文件转换为文本
    :param audio_file_path: 音频文件路径
    :return: 识别的文本内容
    """
    # 加载配置文件
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'xfyun.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    appid = config.get('APPID', '')
    access_key_id = config.get('AccessKeyId', '')
    access_key_secret = config.get('AccessKeySecret', '')

    if not all([appid, access_key_id, access_key_secret]):
        raise ValueError("请在 config/xfyun.json 中配置完整的 API 密钥信息 (APPID, AccessKeyId, AccessKeySecret)")

    # 创建API客户端并进行识别
    client = XfyunAsrClient(
        appid=appid,
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        audio_file_path=audio_file_path
    )
    result = client.get_transcribe_result()
    return parse_order_result(result)


if __name__ == "__main__":
    # 测试代码
    APPID = "XXXXXXXX"
    APIKey = "XXXXXXXXXXXXXXXXXXXXXXXX"
    APISecret = "XXXXXXXXXXXXXXXXXXXXXXXX"
    AUDIO_FILE = "audio/lfasr_涉政.wav"

    try:
        client = XfyunAsrClient(
            appid=APPID,
            access_key_id=APIKey,
            access_key_secret=APISecret,
            audio_file_path=AUDIO_FILE
        )
        final_result = client.get_transcribe_result()
        result = parse_order_result(final_result)

        print("\n" + "="*50)
        print("=== 最终音频转写结果 ===")
        print(f"转写文本：\n{result}")
        print("="*50)

    except Exception as e:
        print("\n" + "="*50)
        print("=== 程序执行失败 ===")
        print(f"错误原因：{str(e)}")
        print("="*50)
