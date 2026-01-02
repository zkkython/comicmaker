"""
阿里云 OSS 图片上传示例
"""

import sys
import os

# 添加 server 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.oss_upload import upload_image_to_oss, upload_image_to_oss_with_config


def example_1_use_config_file():
    """示例1: 使用配置文件中的 OSS 配置上传图片"""
    local_image_path = "/path/to/your/image.jpg"  # 替换为实际的图片路径
    
    try:
        result = upload_image_to_oss_with_config(
            local_image_path=local_image_path,
            oss_object_key="images/my_image.jpg"  # 可选，不提供则自动生成
        )
        
        if result["success"]:
            print(f"上传成功！")
            print(f"URL: {result['url']}")
            print(f"Object Key: {result['object_key']}")
            print(f"Bucket: {result['bucket']}")
        else:
            print("上传失败")
    except Exception as e:
        print(f"上传失败: {str(e)}")


def example_2_use_parameters():
    """示例2: 直接传入参数上传图片"""
    local_image_path = "/path/to/your/image.jpg"  # 替换为实际的图片路径
    
    try:
        result = upload_image_to_oss(
            local_image_path=local_image_path,
            oss_object_key="images/custom_path/image.jpg",
            access_key_id="YOUR_ACCESS_KEY_ID",  # 替换为实际的 AccessKey ID
            access_key_secret="YOUR_ACCESS_KEY_SECRET",  # 替换为实际的 AccessKey Secret
            endpoint="oss-cn-hangzhou.aliyuncs.com",  # 替换为实际的端点
            bucket_name="your-bucket-name",  # 替换为实际的 Bucket 名称
            use_config_file=False  # 不使用配置文件
        )
        
        if result["success"]:
            print(f"上传成功！")
            print(f"URL: {result['url']}")
        else:
            print("上传失败")
    except Exception as e:
        print(f"上传失败: {str(e)}")


def example_3_mixed_usage():
    """示例3: 混合使用（部分参数从配置文件读取，部分直接传入）"""
    local_image_path = "/path/to/your/image.jpg"  # 替换为实际的图片路径
    
    try:
        result = upload_image_to_oss(
            local_image_path=local_image_path,
            oss_object_key="images/custom_path/image.jpg",
            # 只传入部分参数，其他从配置文件读取
            access_key_id="YOUR_ACCESS_KEY_ID",  # 替换为实际的 AccessKey ID
            use_config_file=True  # 允许从配置文件读取缺失的参数
        )
        
        if result["success"]:
            print(f"上传成功！")
            print(f"URL: {result['url']}")
        else:
            print("上传失败")
    except Exception as e:
        print(f"上传失败: {str(e)}")


if __name__ == "__main__":
    print("阿里云 OSS 图片上传示例")
    print("=" * 50)
    print("\n请先配置 server/config/config.yaml 中的 OSS 配置项")
    print("或者直接使用示例2，传入所有参数")
    print("\n取消注释下面的代码来运行示例：")
    print("# example_1_use_config_file()")
    print("# example_2_use_parameters()")
    print("# example_3_mixed_usage()")

