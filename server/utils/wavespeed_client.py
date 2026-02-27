"""
WaveSpeed API 统一客户端

提供统一的接口访问 WaveSpeed 平台的所有服务：
- 图像生成 (text-to-image, image-to-image)
- 视频生成 (text-to-video, image-to-video)
- 视频编辑 (runway, vace)
- LLM 对话 (chat completion, multimodal)

使用示例:
    client = WavespeedClient(api_key="your-api-key")

    # 图像生成
    result = client.generate_image(prompt="a cat", model="seedream-v4.5")

    # 视频生成
    result = client.generate_video(prompt="a dog running", model="seedance-v1-pro-t2v-480p")

    # LLM 对话
    response = client.chat_completion(messages=[{"role": "user", "content": "Hello"}])
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class WavespeedAPIError(Exception):
    """WaveSpeed API 调用错误"""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class WavespeedTimeoutError(Exception):
    """WaveSpeed API 调用超时"""
    pass


class WavespeedClient:
    """
    WaveSpeed API 统一客户端

    封装所有 WaveSpeed API 的调用，提供统一的接口和错误处理。
    """

    BASE_URL = "https://api.wavespeed.ai/api/v3"

    def __init__(self, api_key: str, timeout: int = 300):
        """
        初始化 WaveSpeed 客户端

        Args:
            api_key: WaveSpeed API 密钥
            timeout: 请求超时时间（秒），默认 300 秒
        """
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求到 WaveSpeed API

        Args:
            method: HTTP 方法 (GET, POST, etc.)
            endpoint: API 端点路径（不包含 BASE_URL）
            payload: 请求体数据
            headers: 额外的请求头

        Returns:
            API 响应的 JSON 数据

        Raises:
            WavespeedAPIError: API 调用失败
            WavespeedTimeoutError: 请求超时
        """
        url = f"{self.BASE_URL}/{endpoint}"
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)

        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=request_headers, timeout=30)
            else:
                response = self.session.request(
                    method,
                    url,
                    headers=request_headers,
                    data=json.dumps(payload) if payload else None,
                    timeout=30
                )

            if response.status_code != 200:
                error_text = response.text
                try:
                    error_data = response.json()
                    error_text = json.dumps(error_data, ensure_ascii=False)
                except:
                    pass
                raise WavespeedAPIError(
                    f"API error: {response.status_code}, {error_text}",
                    status_code=response.status_code
                )

            return response.json()

        except requests.exceptions.Timeout:
            raise WavespeedTimeoutError(f"Request to {endpoint} timed out")
        except requests.exceptions.RequestException as e:
            raise WavespeedAPIError(f"Request failed: {str(e)}")

    def _poll_result(
        self,
        request_id: str,
        poll_interval: float = 0.5,
        max_wait: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        轮询异步任务结果

        Args:
            request_id: 任务请求 ID
            poll_interval: 轮询间隔（秒）
            max_wait: 最大等待时间（秒），None 表示使用客户端默认 timeout

        Returns:
            任务结果数据

        Raises:
            WavespeedTimeoutError: 超过最大等待时间
            WavespeedAPIError: 任务失败或 API 错误
        """
        max_wait = max_wait or self.timeout
        endpoint = f"predictions/{request_id}/result"
        start_time = time.time()

        while True:
            if time.time() - start_time > max_wait:
                raise WavespeedTimeoutError(f"Polling exceeded max wait time of {max_wait}s")

            result = self._request("GET", endpoint)
            data = result.get("data", {})
            status = data.get("status")

            if status == "completed":
                return data
            elif status == "failed":
                error_msg = data.get("error", "Unknown error")
                raise WavespeedAPIError(f"Task failed: {error_msg}")
            else:
                logger.info(f"Task still processing. Status: {status}")
                time.sleep(poll_interval)

    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        将图片文件编码为 base64 data URI

        Args:
            image_path: 图片文件路径

        Returns:
            base64 data URI 字符串
        """
        import base64

        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        mime_type = mime_types.get(ext, "image/jpeg")

        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"

    def _encode_video_to_base64(self, video_path: str) -> str:
        """
        将视频文件编码为 base64 data URI

        Args:
            video_path: 视频文件路径

        Returns:
            base64 data URI 字符串
        """
        import base64

        ext = os.path.splitext(video_path)[1].lower()
        mime_type = "video/mp4" if ext in [".mp4", ".mov", ".avi", ".mkv"] else "video/mp4"

        with open(video_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"

    def _prepare_image_input(self, image: str) -> str:
        """
        准备图片输入（支持 URL、本地路径、base64）

        Args:
            image: 图片 URL、本地路径或 base64 字符串

        Returns:
            处理后的图片 data URI 或 URL
        """
        if image.startswith("data:image/"):
            return image
        elif image.startswith("http://") or image.startswith("https://"):
            return image
        elif os.path.exists(image):
            return self._encode_image_to_base64(image)
        else:
            raise ValueError(f"Invalid image input: {image}")

    # ==================== 图像生成方法 ====================

    def generate_image(
        self,
        prompt: str,
        model: str = "seedream-v4.5",
        provider: str = "bytedance",
        size: str = "1024*1024",
        seed: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        文生图

        Args:
            prompt: 提示词
            model: 模型名称
            provider: 提供商
            size: 图片尺寸 (如 "1024*1024")
            seed: 随机种子
            aspect_ratio: 宽高比（用于 nano-banana-pro）
            resolution: 分辨率（用于 nano-banana-pro）
            **kwargs: 其他模型特定参数

        Returns:
            包含生成结果的字典
        """
        if seed is None:
            seed = int(datetime.now().timestamp())

        # 构建端点
        if provider == "google" and model == "nano-banana-pro":
            endpoint = f"{provider}/{model}/text-to-image"
            payload = {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio or "16:9",
                "resolution": resolution or "1k",
                "seed": seed
            }
        elif provider == "alibaba" and model.startswith("wan-2.6"):
            endpoint = f"{provider}/{model}/text-to-image"
            payload = {
                "prompt": prompt,
                "size": size,
                "seed": seed
            }
        else:
            endpoint = f"{provider}/{model}"
            payload = {
                "prompt": prompt,
                "size": size,
                "seed": seed
            }

        payload.update(kwargs)

        begin = time.time()
        result = self._request("POST", endpoint, payload)
        request_id = result["data"]["id"]
        logger.info(f"Image task submitted. Request ID: {request_id}")

        data = self._poll_result(request_id)
        end = time.time()
        logger.info(f"Image generated in {end - begin:.2f}s")

        image_url = data["outputs"][0]
        return {
            "success": True,
            "url": image_url,
            "request_id": request_id,
            "elapsed_time": end - begin
        }

    def edit_image(
        self,
        prompt: str,
        images: Union[str, List[str]],
        model: str = "seedream-v4.5",
        provider: str = "bytedance",
        size: str = "1024*1024",
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        图生图 / 图像编辑

        Args:
            prompt: 提示词
            images: 图片路径、URL 或列表
            model: 模型名称
            provider: 提供商
            size: 输出尺寸
            aspect_ratio: 宽高比
            resolution: 分辨率
            seed: 随机种子
            **kwargs: 其他参数

        Returns:
            包含编辑结果的字典
        """
        if seed is None:
            seed = int(datetime.now().timestamp())

        # 处理图片输入
        if isinstance(images, str):
            images = [images]

        image_list = []
        for img in images[:10]:  # 最多 10 张
            if img.startswith("http://") or img.startswith("https://"):
                image_list.append(img)
            elif img.startswith("data:image/"):
                image_list.append(img)
            elif os.path.exists(img):
                image_list.append(self._encode_image_to_base64(img))
            elif img:  # 非空字符串但不是有效路径
                image_list.append(img)

        # 构建端点和 payload
        if provider == "google" and model == "nano-banana-pro":
            endpoint = f"{provider}/{model}/edit"
            payload = {
                "prompt": prompt,
                "images": image_list,
                "aspect_ratio": aspect_ratio or "16:9",
                "resolution": resolution or "1k",
                "seed": seed
            }
        elif provider == "alibaba" and model.startswith("wan-2.6"):
            endpoint = f"{provider}/{model}/image-edit"
            payload = {
                "prompt": prompt,
                "images": image_list,
                "size": size,
                "seed": seed
            }
        else:
            endpoint = f"{provider}/{model}/edit"
            payload = {
                "prompt": prompt,
                "images": image_list,
                "size": size,
                "seed": seed
            }

        payload.update(kwargs)

        begin = time.time()
        result = self._request("POST", endpoint, payload)
        request_id = result["data"]["id"]
        logger.info(f"Image edit task submitted. Request ID: {request_id}")

        data = self._poll_result(request_id)
        end = time.time()
        logger.info(f"Image edited in {end - begin:.2f}s")

        image_url = data["outputs"][0]
        return {
            "success": True,
            "url": image_url,
            "request_id": request_id,
            "elapsed_time": end - begin
        }

    # ==================== 视频生成方法 ====================

    def generate_video(
        self,
        prompt: str,
        model: str = "seedance-v1-pro-t2v-480p",
        provider: str = "bytedance",
        aspect_ratio: str = "16:9",
        duration: int = 5,
        seed: int = -1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        文生视频

        Args:
            prompt: 提示词
            model: 模型名称
            provider: 提供商
            aspect_ratio: 宽高比
            duration: 时长（秒）
            seed: 随机种子
            **kwargs: 其他参数

        Returns:
            包含生成结果的字典
        """
        endpoint = f"{provider}/{model}"
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "seed": seed
        }
        payload.update(kwargs)

        begin = time.time()
        result = self._request("POST", endpoint, payload)
        request_id = result["data"]["id"]
        logger.info(f"Video task submitted. Request ID: {request_id}")

        data = self._poll_result(request_id)
        end = time.time()
        logger.info(f"Video generated in {end - begin:.2f}s")

        video_url = data["outputs"][0]
        return {
            "success": True,
            "url": video_url,
            "request_id": request_id,
            "elapsed_time": end - begin
        }

    def generate_video_from_image(
        self,
        prompt: str,
        image: str,
        model: str = "seedance-v1-pro-i2v-480p",
        provider: str = "bytedance",
        duration: int = 5,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        图生视频

        Args:
            prompt: 提示词
            image: 图片路径或 URL
            model: 模型名称
            provider: 提供商
            duration: 时长（秒）
            seed: 随机种子
            **kwargs: 其他参数

        Returns:
            包含生成结果的字典
        """
        if seed is None:
            seed = int(datetime.now().timestamp())

        image_data = self._prepare_image_input(image)

        endpoint = f"{provider}/{model}"
        payload = {
            "prompt": prompt,
            "image": image_data,
            "duration": duration,
            "seed": seed
        }
        payload.update(kwargs)

        begin = time.time()
        result = self._request("POST", endpoint, payload)
        request_id = result["data"]["id"]
        logger.info(f"Image-to-video task submitted. Request ID: {request_id}")

        data = self._poll_result(request_id)
        end = time.time()
        logger.info(f"Video generated from image in {end - begin:.2f}s")

        video_url = data["outputs"][0]
        return {
            "success": True,
            "url": video_url,
            "request_id": request_id,
            "elapsed_time": end - begin
        }

    def edit_video(
        self,
        prompt: str,
        video: str,
        image: Optional[str] = None,
        task: str = "depth",
        model: str = "wan-2.1-14b-vace",
        provider: str = "wavespeed-ai",
        **kwargs
    ) -> Dict[str, Any]:
        """
        视频编辑 (VACE, Runway 等)

        Args:
            prompt: 提示词
            video: 视频路径或 URL
            image: 参考图片路径或 URL（可选）
            task: 任务类型 (depth, pose, etc.)
            model: 模型名称
            provider: 提供商
            **kwargs: 其他参数

        Returns:
            包含编辑结果的字典
        """
        # 准备视频输入
        if video.startswith("http://") or video.startswith("https://"):
            video_data = video
        elif os.path.exists(video):
            video_data = self._encode_video_to_base64(video)
        else:
            video_data = video

        endpoint = f"{provider}/{model}"
        payload = {
            "prompt": prompt,
            "video": video_data,
            "task": task
        }

        if image:
            payload["images"] = [self._prepare_image_input(image)]

        payload.update(kwargs)

        begin = time.time()
        result = self._request("POST", endpoint, payload)
        request_id = result["data"]["id"]
        logger.info(f"Video edit task submitted. Request ID: {request_id}")

        data = self._poll_result(request_id)
        end = time.time()
        logger.info(f"Video edited in {end - begin:.2f}s")

        video_url = data["outputs"][0]
        return {
            "success": True,
            "url": video_url,
            "request_id": request_id,
            "elapsed_time": end - begin
        }

    # ==================== LLM 方法 ====================

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        provider: str = "openai",
        max_tokens: int = 6024,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        LLM 对话补全

        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            model: 模型名称
            provider: 提供商 (openai, etc.)
            max_tokens: 最大 token 数
            temperature: 温度参数
            **kwargs: 其他参数

        Returns:
            包含响应内容的字典
        """
        endpoint = f"{provider}/{model}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        payload.update(kwargs)

        result = self._request("POST", endpoint, payload)

        if "choices" in result and len(result["choices"]) > 0:
            return {
                "success": True,
                "content": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {}),
                "model": result.get("model", model),
                "raw_response": result
            }
        else:
            raise WavespeedAPIError("Invalid response format from API")

    def multimodal_chat(
        self,
        prompt: str,
        images: Optional[List[str]] = None,
        videos: Optional[List[str]] = None,
        model: str = "gpt-4o",
        provider: str = "openai",
        max_tokens: int = 6024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        多模态对话（文本 + 图片/视频）

        Args:
            prompt: 文本提示
            images: 图片路径列表
            videos: 视频路径列表
            model: 模型名称
            provider: 提供商
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            包含响应内容的字典
        """
        content_parts = [{"type": "text", "text": prompt}]

        # 处理图片
        if images:
            for img_path in images:
                image_data = self._prepare_image_input(img_path)
                content_parts.append({
                    "type": "image_url",
                    "image_url": {"url": image_data}
                })

        # 处理视频（提取帧）
        if videos:
            for video_path in videos:
                frames = self._extract_video_frames(video_path)
                for frame_data in frames:
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": frame_data}
                    })

        messages = [{"role": "user", "content": content_parts}]
        return self.chat_completion(messages, model, provider, max_tokens, **kwargs)

    def _extract_video_frames(
        self,
        video_path: str,
        num_frames: int = 10,
        target_size: tuple = (360, 420)
    ) -> List[str]:
        """
        从视频中提取帧并编码为 base64

        Args:
            video_path: 视频路径
            num_frames: 提取帧数
            target_size: 目标尺寸

        Returns:
            base64 编码的帧列表
        """
        try:
            import cv2
            import numpy as np

            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if total_frames <= 0:
                raise ValueError("Video has no frames")

            indices = np.linspace(0, total_frames - 1, min(num_frames, total_frames), dtype=int)
            frames = []

            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    # 调整大小
                    frame = cv2.resize(frame, target_size)
                    _, buffer = cv2.imencode(".jpg", frame)
                    encoded = base64.b64encode(buffer).decode("utf-8")
                    frames.append(f"data:image/jpeg;base64,{encoded}")

            cap.release()
            return frames

        except Exception as e:
            logger.warning(f"Failed to extract video frames: {e}")
            return []


# 便捷函数：从配置创建客户端
def create_client_from_config(config_path: Optional[str] = None) -> WavespeedClient:
    """
    从配置文件创建 WavespeedClient

    Args:
        config_path: 配置文件路径，默认使用 server/config/config.yaml

    Returns:
        配置好的 WavespeedClient 实例
    """
    import yaml

    if config_path is None:
        server_dir = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(server_dir, "config", "config.yaml")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # 优先使用新的统一 key
    api_key = config.get('wavespeed_api_key')

    # 向后兼容：尝试从旧位置读取
    if not api_key:
        api_key = (
            config.get('image_gen', {}).get('wavespeed_api')
            or config.get('video_gen', {}).get('wavespeed_api')
            or config.get('llm', {}).get('openai_api_key')
        )

    if not api_key:
        raise ValueError("No API key found in config. Please set wavespeed_api_key.")

    return WavespeedClient(api_key=api_key)
