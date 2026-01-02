"""
阿里云 OSS 图片上传工具
用于将本地图片文件上传到阿里云 OSS
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import yaml

try:
    import oss2
except ImportError:
    oss2 = None
    logging.warning("oss2 库未安装，请运行: pip install oss2")

logger = logging.getLogger(__name__)


def load_oss_config() -> Dict[str, str]:
    """
    从 config.yaml 加载 OSS 配置
    
    Returns:
        {
            "access_key_id": "...",
            "access_key_secret": "...",
            "endpoint": "...",
            "bucket_name": "..."
        }
        
    Raises:
        FileNotFoundError: 配置文件不存在时抛出
        KeyError: 配置项缺失时抛出
    """
    # 获取配置文件路径
    server_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(server_dir, "config", "config.yaml")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    oss_config = config.get('oss', {})
    if not oss_config:
        raise KeyError("配置文件中缺少 'oss' 配置")
    
    access_key_id = oss_config.get('access_key_id')
    access_key_secret = oss_config.get('access_key_secret')
    endpoint = oss_config.get('endpoint')
    bucket_name = oss_config.get('bucket_name')
    
    if not access_key_id:
        raise KeyError("配置文件中缺少 'oss.access_key_id' 配置")
    if not access_key_secret:
        raise KeyError("配置文件中缺少 'oss.access_key_secret' 配置")
    if not endpoint:
        raise KeyError("配置文件中缺少 'oss.endpoint' 配置")
    if not bucket_name:
        raise KeyError("配置文件中缺少 'oss.bucket_name' 配置")
    
    return {
        "access_key_id": access_key_id,
        "access_key_secret": access_key_secret,
        "endpoint": endpoint,
        "bucket_name": bucket_name
    }


def upload_image_to_oss(
    local_image_path: str,
    oss_object_key: Optional[str] = None,
    access_key_id: Optional[str] = None,
    access_key_secret: Optional[str] = None,
    endpoint: Optional[str] = None,
    bucket_name: Optional[str] = None,
    use_config_file: bool = True
) -> Dict[str, Any]:
    """
    上传本地图片文件到阿里云 OSS
    
    Args:
        local_image_path: 本地图片文件路径
        oss_object_key: OSS 对象键（文件在 OSS 中的路径），如果不提供则自动生成
        access_key_id: 阿里云 AccessKey ID（可选，优先使用参数，其次从配置文件读取）
        access_key_secret: 阿里云 AccessKey Secret（可选，优先使用参数，其次从配置文件读取）
        endpoint: OSS 端点（可选，优先使用参数，其次从配置文件读取）
        bucket_name: OSS Bucket 名称（可选，优先使用参数，其次从配置文件读取）
        use_config_file: 是否从配置文件读取配置（当参数未提供时）
    
    Returns:
        {
            "success": True,
            "url": "https://bucket.oss-cn-hangzhou.aliyuncs.com/path/to/image.jpg",
            "object_key": "path/to/image.jpg",
            "bucket": "bucket-name"
        }
        
    Raises:
        FileNotFoundError: 本地图片文件不存在
        ImportError: oss2 库未安装
        Exception: 上传失败时抛出异常
    """
    if oss2 is None:
        raise ImportError("oss2 库未安装，请运行: pip install oss2")
    
    # 检查本地文件是否存在
    if not os.path.exists(local_image_path):
        raise FileNotFoundError(f"本地图片文件不存在: {local_image_path}")
    
    # 加载配置（如果参数未提供且允许使用配置文件）
    if use_config_file and (not access_key_id or not access_key_secret or not endpoint or not bucket_name):
        try:
            config = load_oss_config()
            access_key_id = access_key_id or config.get("access_key_id")
            access_key_secret = access_key_secret or config.get("access_key_secret")
            endpoint = endpoint or config.get("endpoint")
            bucket_name = bucket_name or config.get("bucket_name")
        except (FileNotFoundError, KeyError) as e:
            if not access_key_id or not access_key_secret or not endpoint or not bucket_name:
                raise Exception(f"无法加载 OSS 配置，请提供完整的参数或配置 config.yaml: {str(e)}")
    
    # 验证必需参数
    if not access_key_id or not access_key_secret or not endpoint or not bucket_name:
        raise ValueError("缺少必需的 OSS 配置参数：access_key_id, access_key_secret, endpoint, bucket_name")
    
    # 如果没有提供 OSS 对象键，自动生成
    if not oss_object_key:
        # 使用日期目录结构：aisrc/YYYY/MM/DD/filename
        now = datetime.now()
        date_dir = now.strftime("%Y/%m/%d")  # 例如: 2025/01/27
        timestamp = now.strftime("%H%M%S")  # 例如: 143022
        filename = os.path.basename(local_image_path)
        name, ext = os.path.splitext(filename)
        oss_object_key = f"aisrc/{date_dir}/{timestamp}_{name}{ext}"
    
    try:
        # 创建 OSS 认证对象
        auth = oss2.Auth(access_key_id, access_key_secret)
        
        # 创建 Bucket 对象
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        
        # 上传文件
        logger.info(f"开始上传图片到 OSS: {local_image_path} -> {oss_object_key}")
        result = bucket.put_object_from_file(oss_object_key, local_image_path)
        
        # 检查上传结果
        if result.status == 200:
            # 构建访问 URL
            # 格式: https://bucket-name.endpoint/object-key
            if endpoint.startswith("http://") or endpoint.startswith("https://"):
                base_url = f"{endpoint}/{bucket_name}"
            else:
                # 如果没有协议，默认使用 https
                base_url = f"https://{bucket_name}.{endpoint}"
            
            url = f"{base_url}/{oss_object_key}"
            
            logger.info(f"图片上传成功: {url}")
            
            return {
                "success": True,
                "url": url,
                "object_key": oss_object_key,
                "bucket": bucket_name,
                "status": result.status
            }
        else:
            raise Exception(f"上传失败，状态码: {result.status}")
            
    except oss2.exceptions.AccessDenied:
        raise Exception("OSS 访问被拒绝，请检查 AccessKey 权限")
    except oss2.exceptions.NoSuchBucket:
        raise Exception(f"OSS Bucket 不存在: {bucket_name}")
    except oss2.exceptions.OssError as e:
        raise Exception(f"OSS 错误: {str(e)}")
    except Exception as e:
        raise Exception(f"上传图片到 OSS 失败: {str(e)}")


def upload_image_to_oss_with_config(
    local_image_path: str,
    oss_object_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用配置文件中的 OSS 配置上传图片（便捷函数）
    
    Args:
        local_image_path: 本地图片文件路径
        oss_object_key: OSS 对象键（可选，不提供则自动生成）
    
    Returns:
        同 upload_image_to_oss 的返回值
    """
    return upload_image_to_oss(
        local_image_path=local_image_path,
        oss_object_key=oss_object_key,
        use_config_file=True
    )

