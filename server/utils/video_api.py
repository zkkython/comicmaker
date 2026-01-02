import requests
import json
import time
import logging
import os
import base64
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()

# from dotenv import load_dotenv

# load_dotenv()


def text_to_video_generate(api_key, prompt, save_path: str = None, model="seedance-v1-pro-t2v-480p", provider="bytedance"):
    url = f"https://api.wavespeed.ai/api/v3/{provider}/{model}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "aspect_ratio": "16:9",
        "duration": 5,
        "prompt": prompt,
        "seed": -1
    }

    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.info(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}"
        }

    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]

            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                url = result["outputs"][0]
                logger.info(f"Task completed. URL: {url}")
                time_ft = datetime.now().strftime("%m%d%H%M%S")
                url_name = url.split("/")[-1]
                output_filename = save_path if save_path else f"{time_ft}_{url_name}"
                resp = requests.get(url, stream=True)
                resp.raise_for_status()
                with open(output_filename, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                return {
                    'success': True,
                    'output_path': output_filename,
                    'message': "Video generated successfully."
                }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }


def image_to_video_generate(api_key, prompt, image, save_path: str = None, model="seedance-v1-pro-i2v-480p", provider="bytedance", duration=5):
    logger.info("Hello from WaveSpeedAI!")
    

    url = f"https://api.wavespeed.ai/api/v3/{provider}/{model}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    with open(image, "rb") as f:
        img_bytes = f.read()
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    seed = int(datetime.now().timestamp())
    payload = {
        "duration": duration,
        "image": f"data:image/jpeg;base64,{b64}",
        "prompt": prompt,
        "seed": seed
    }

    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.info(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}"
        }

    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]

            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                url = result["outputs"][0]
                logger.info(f"Task completed. URL: {url}")
                time_ft = datetime.now().strftime("%m%d%H%M%S")
                url_name = url.split("/")[-1]
                output_filename = save_path if save_path else f"{time_ft}_{url_name}"
                resp = requests.get(url, stream=True)
                resp.raise_for_status()
                with open(output_filename, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                return {
                    'success': True,
                    'output_path': output_filename,
                    'message': "Video generated successfully."
                }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }

def frame_to_frame_video(api_key, prompt, images, save_path: str = None, model="wan-flf2v", provider="wavespeed-ai"):
    logger.info("Hello from WaveSpeedAI!")
    

    url = f"https://api.wavespeed.ai/api/v3/{provider}/{model}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    with open(images[0], "rb") as f:
        img_bytes = f.read()
    first_frame_b64 = base64.b64encode(img_bytes).decode("utf-8")
    with open(images[-1], "rb") as f:
        img_bytes = f.read()
    last_frame_b64 = base64.b64encode(img_bytes).decode("utf-8")
    seed = int(datetime.now().timestamp())
    payload = {
        "duration": 5,
        "enable_safety_checker": True,
        "first_image": f"data:image/jpeg;base64,{first_frame_b64}",
        "guidance_scale": 5,
        "last_image": f"data:image/jpeg;base64,{last_frame_b64}",
        "negative_prompt": "",
        "num_inference_steps": 30,
        "prompt": prompt,
        "seed": seed,
        "size": "832*480"
    }

    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.info(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}"
        }

    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]

            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                url = result["outputs"][0]
                logger.info(f"Task completed. URL: {url}")
                time_ft = datetime.now().strftime("%m%d%H%M%S")
                url_name = url.split("/")[-1]
                output_filename = save_path if save_path else f"{time_ft}_{url_name}"
                resp = requests.get(url, stream=True)
                resp.raise_for_status()
                with open(output_filename, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                return {
                    'success': True,
                    'output_path': output_filename,
                    'message': f"{prompt} success generate video"
                }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Task failed: {result.get('error')}"
            }
        

def audio_gen(api_key, prompt, video_url, model="mmaudio-v2", save_path=None, provider="wavespeed-ai", duration=5, guidance_scale=4.5, mask_away_clip=False, negative_prompt="", num_inference_steps=25):
    logger.info("Hello from WaveSpeedAI!")

    # Check if video_url is a local file path
    if os.path.exists(video_url):
        # Read the local video file and convert it to base64
        with open(video_url, "rb") as f:
            video_bytes = f.read()
        video_b64 = base64.b64encode(video_bytes).decode("utf-8")
        # Determine the MIME type based on file extension
        ext = os.path.splitext(video_url)[1].lower()
        mime_type = "mp4" if ext in [".mp4", ".mov", ".avi", ".mkv"] else "mp4"  # Default to mp4 if unknown
        video_data_uri = f"data:video/{mime_type};base64,{video_b64}"
    else:
        # Assume it's a URL
        video_data_uri = video_url

    url = f"https://api.wavespeed.ai/api/v3/{provider}/{model}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "duration": duration,
        "guidance_scale": guidance_scale,
        "mask_away_clip": mask_away_clip,
        "negative_prompt": negative_prompt,
        "num_inference_steps": num_inference_steps,
        "prompt": prompt,
        "video": video_data_uri
    }

    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.info(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}"
        }

    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]

            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                url = result["outputs"][0]
                logger.info(f"Task completed. URL: {url}")
                time_ft = datetime.now().strftime("%m%d%H%M%S")
                url_name = url.split("/")[-1]
                output_filename = save_path if save_path else f"{time_ft}_{url_name}"
                resp = requests.get(url, stream=True)
                resp.raise_for_status()
                with open(output_filename, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                return {
                    'success': True,
                    'output_path': output_filename,
                    'message': f"{prompt} success generate video"
                }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }

        time.sleep(0.5)


def runway_video_editing(api_key, prompt, video_url, aspect_ratio="16:9", save_path: str = None):
    url = "https://api.wavespeed.ai/api/v3/runwayml/gen4-aleph"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    with open(video_url, "rb") as f:
            video_bytes = f.read()
    video_b64 = base64.b64encode(video_bytes).decode("utf-8")
    # Determine the MIME type based on file extension
    ext = os.path.splitext(video_url)[1].lower()
    mime_type = "mp4" if ext in [".mp4", ".mov", ".avi", ".mkv"] else "mp4"  # Default to mp4 if unknown
    video_data_uri = f"data:video/{mime_type};base64,{video_b64}"

    payload = {
        "aspect_ratio": aspect_ratio,
        "prompt": prompt,
        "video": video_data_uri
    }

    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        logger.info(f"Error: {response.status_code}, {response.text}")
        return

    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]

            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                url = result["outputs"][0]
                time_ft = datetime.now().strftime("%m%d%H%M%S")
                url_name = url.split("/")[-1]
                os.makedirs("results", exist_ok=True)
                output_filename = save_path if save_path else f"results/{time_ft}_{url_name}"
                resp = requests.get(url, stream=True)
                resp.raise_for_status()
                with open(output_filename, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                return {
                    'success': True,
                    'output_path': output_filename,
                    'message': f"{prompt} success generate video"
                }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }


def vace_api(
    api_key,
    prompt,
    image_url: str=None,
    video_url: str=None,
    context_scale: int=1,
    flow_shift: int=16,
    guidance_scale: int=5,
    duration: int=5,
    num_inference_steps: int=40,
    task: str="depth",
    size: str="1280*720",
    save_path: str=None
):
    url = "https://api.wavespeed.ai/api/v3/wavespeed-ai/wan-2.1-14b-vace"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    if os.path.exists(video_url):
        # Read the local video file and convert it to base64
        with open(video_url, "rb") as f:
            video_bytes = f.read()
        video_b64 = base64.b64encode(video_bytes).decode("utf-8")
        # Determine the MIME type based on file extension
        ext = os.path.splitext(video_url)[1].lower()
        mime_type = "mp4" if ext in [".mp4", ".mov", ".avi", ".mkv"] else "mp4"  # Default to mp4 if unknown
        video_data_uri = f"data:video/{mime_type};base64,{video_b64}"
    else:
        # Assume it's a URL
        video_data_uri = video_url

    with open(image_url, "rb") as f:
        img_bytes = f.read()
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    image_b64 = f"data:image/jpeg;base64,{b64}"

    seed = int(datetime.now().timestamp())
    payload = {
        "context_scale": context_scale,
        "duration": duration,
        "flow_shift": flow_shift,
        "guidance_scale": guidance_scale,
        "images": [
            image_b64
        ],
        "negative_prompt": "",
        "num_inference_steps": num_inference_steps,
        "prompt": prompt,
        "seed": seed,
        "size": size,
        "task": task,
        "video": video_data_uri if video_url else ""
    }

    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        logger.info(f"Error: {response.status_code}, {response.text}")
        return

    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]

            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                url = result["outputs"][0]
                time_ft = datetime.now().strftime("%m%d%H%M%S")
                url_name = url.split("/")[-1]
                output_filename = save_path if save_path else f"{time_ft}_{url_name}"
                resp = requests.get(url, stream=True)
                resp.raise_for_status()
                with open(output_filename, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                return {
                    'success': True,
                    'output_path': output_filename,
                    'message': f"{prompt} success generate video"
                }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }


def speech_gen(api_key: str, prompt: str, voice_id: str = "Wise_Woman", emotion: str = "surprised", english_normalization: bool = False, pitch: int = 0, speed: float = 1.0, volume: float = 1, save_path=None, provider="minimax", model="speech-2.5-turbo-preview"):

    url = f"https://api.wavespeed.ai/api/v3/{provider}/{model}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "emotion": emotion,
        "english_normalization": english_normalization,
        "pitch": pitch,
        "speed": speed,
        "text": prompt,
        "voice_id": voice_id,
        "volume": volume
    }

    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        logger.info(f"Error: {response.status_code}, {response.text}")
        return

    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]

            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                url = result["outputs"][0]
                logger.info(f"Task completed. URL: {url}")
                time_ft = datetime.now().strftime("%m%d%H%M%S")
                url_name = url.split("/")[-1]
                output_filename = save_path if save_path else f"{time_ft}_{url_name}"
                resp = requests.get(url, stream=True)
                resp.raise_for_status()
                with open(output_filename, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                return {
                    'success': True,
                    'output_path': output_filename,
                    'message': f"{prompt[:30]} success generate video"
                }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }

        time.sleep(0.5)


def hailuo_i2v_pro(api_key: str, prompt: str, image: str, end_image: str = None, enable_prompt_expansion: bool = True, save_path: str = None):
    """
    Generate video from image using MiniMax hailuo-02 i2v-pro model.
    
    Args:
        api_key: WaveSpeed API key
        prompt: Text prompt for video generation
        image: Start image URL or local file path
        end_image: End image URL or local file path (optional)
        enable_prompt_expansion: Whether to enable prompt expansion
        save_path: Optional path to save the generated video
    
    Returns:
        dict: Result containing success status and output URL/path or error message
    """
    logger.info("Hello from WaveSpeedAI!")
    
    # Handle local image file by converting to base64
    if os.path.exists(image):
        with open(image, "rb") as f:
            img_bytes = f.read()
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        ext = os.path.splitext(image)[1].lower()
        mime = "jpeg" if ext in [".jpg", ".jpeg"] else ext.strip(".")
        image_data = f"data:image/{mime};base64,{b64}"
    else:
        # Assume it's a URL
        image_data = image
    
    # Handle end image if provided
    end_image_data = None
    if end_image:
        if os.path.exists(end_image):
            with open(end_image, "rb") as f:
                img_bytes = f.read()
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            ext = os.path.splitext(end_image)[1].lower()
            mime = "jpeg" if ext in [".jpg", ".jpeg"] else ext.strip(".")
            end_image_data = f"data:image/{mime};base64,{b64}"
        else:
            # Assume it's a URL
            end_image_data = end_image
    
    url = "https://api.wavespeed.ai/api/v3/minimax/hailuo-02/i2v-standard"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "image": image_data,
        "prompt": prompt,
        "enable_prompt_expansion": enable_prompt_expansion
    }
    
    # Add end_image to payload if provided
    if end_image_data:
        payload["end_image"] = end_image_data

    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.info(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}"
        }

    url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Poll for results
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            status = result["status"]

            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                output_url = result["outputs"][0]
                logger.info(f"Task completed. URL: {output_url}")
                
                # Download video if save_path is provided
                if save_path:
                    resp = requests.get(output_url, stream=True)
                    resp.raise_for_status()
                    with open(save_path, "wb") as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)
                    return {
                        'success': True,
                        'output_path': save_path,
                        'message': "Video generated successfully."
                    }
                else:
                    return {
                        'success': True,
                        'output_url': output_url,
                        'message': "Video generated successfully."
                    }
            elif status == "failed":
                logger.info(f"Task failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': f"Task failed: {result.get('error')}"
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.info(f"Error: {response.status_code}, {response.text}")
            return {
                'success': False,
                'error': f"Error: {response.status_code}, {response.text}"
            }

        time.sleep(0.5)


def vidu_reference_to_video_q2(
    api_key: str,
    prompt: str,
    image_urls: List[str],
    aspect_ratio: str = "16:9",
    resolution: str = "720p",
    duration: int = 5,
    movement_amplitude: str = "auto",
    seed: int = 0
) -> Dict[str, Any]:
    """
    使用 vidu/reference-to-video-q2 模型生成视频
    
    Args:
        api_key: WaveSpeed API key
        prompt: 文字描述
        image_urls: 图片 URL 列表（最多7张）
        aspect_ratio: 宽高比（1:1, 3:4, 4:3, 16:9, 9:16）
        resolution: 分辨率（540p, 720p, 1080p）
        duration: 时长（1-10秒）
        movement_amplitude: 运动幅度（默认 "auto"）
        seed: 随机种子（默认 0）
    
    Returns:
        dict: 包含 success, output_url, api_request, api_response, error 的字典
    """
    url = "https://api.wavespeed.ai/api/v3/vidu/reference-to-video-q2"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    # 限制最多7张图片
    if len(image_urls) > 7:
        image_urls = image_urls[:7]
        logger.warning(f"图片数量超过7张，已截取前7张")
    
    payload = {
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "duration": duration,
        "movement_amplitude": movement_amplitude,
        "seed": seed,
        "images": image_urls,
        "prompt": prompt
    }
    
    # 保存请求参数用于日志
    api_request = {
        "url": url,
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer ***"
        },
        "payload": {
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "duration": duration,
            "movement_amplitude": movement_amplitude,
            "seed": seed,
            "images": image_urls[:3] if len(image_urls) > 3 else image_urls,  # 只显示前3张用于日志
            "prompt": prompt
        }
    }
    
    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.error(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}",
            'api_request': api_request,
            'api_response': {}
        }
    
    # 轮询结果
    poll_url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    poll_headers = {"Authorization": f"Bearer {api_key}"}
    full_response = None
    
    while True:
        poll_response = requests.get(poll_url, headers=poll_headers)
        if poll_response.status_code == 200:
            result = poll_response.json()["data"]
            status = result["status"]
            full_response = result
            
            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                output_url = result["outputs"][0]
                logger.info(f"Task completed. URL: {output_url}")
                return {
                    'success': True,
                    'output_url': output_url,
                    'api_request': api_request,
                    'api_response': full_response,
                    'message': "Video generated successfully."
                }
            elif status == "failed":
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Task failed: {error_msg}")
                return {
                    'success': False,
                    'error': f"Task failed: {error_msg}",
                    'api_request': api_request,
                    'api_response': full_response
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.error(f"Error: {poll_response.status_code}, {poll_response.text}")
            return {
                'success': False,
                'error': f"Error: {poll_response.status_code}, {poll_response.text}",
                'api_request': api_request,
                'api_response': full_response if full_response else {}
            }
        
        time.sleep(0.5)


def sora_2_image_to_video(
    api_key: str,
    prompt: str,
    image_url: str,
    duration: int = 4
) -> Dict[str, Any]:
    """
    使用 openai/sora-2/image-to-video-pro 模型生成视频
    
    Args:
        api_key: WaveSpeed API key
        prompt: 文字描述
        image_url: 图片 URL
        duration: 时长（4, 8, 12秒）
    
    Returns:
        dict: 包含 success, output_url, api_request, api_response, error 的字典
    """
    url = "https://api.wavespeed.ai/api/v3/openai/sora-2/image-to-video-pro"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    payload = {
        "duration": duration,
        "image": image_url,
        "prompt": prompt
    }
    
    # 保存请求参数用于日志
    api_request = {
        "url": url,
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer ***"
        },
        "payload": {
            "duration": duration,
            "image": image_url,
            "prompt": prompt
        }
    }
    
    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.error(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}",
            'api_request': api_request,
            'api_response': {}
        }
    
    # 轮询结果
    poll_url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    poll_headers = {"Authorization": f"Bearer {api_key}"}
    full_response = None
    
    while True:
        poll_response = requests.get(poll_url, headers=poll_headers)
        if poll_response.status_code == 200:
            result = poll_response.json()["data"]
            status = result["status"]
            full_response = result
            
            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                output_url = result["outputs"][0]
                logger.info(f"Task completed. URL: {output_url}")
                return {
                    'success': True,
                    'output_url': output_url,
                    'api_request': api_request,
                    'api_response': full_response,
                    'message': "Video generated successfully."
                }
            elif status == "failed":
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Task failed: {error_msg}")
                return {
                    'success': False,
                    'error': f"Task failed: {error_msg}",
                    'api_request': api_request,
                    'api_response': full_response
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.error(f"Error: {poll_response.status_code}, {poll_response.text}")
            return {
                'success': False,
                'error': f"Error: {poll_response.status_code}, {poll_response.text}",
                'api_request': api_request,
                'api_response': full_response if full_response else {}
            }
        
        time.sleep(0.5)


def wan_2_5_image_to_video(
    api_key: str,
    prompt: str,
    image_url: str,
    resolution: str = "720p",
    duration: int = 5,
    enable_prompt_expansion: bool = False,
    seed: int = -1
) -> Dict[str, Any]:
    """
    使用 alibaba/wan-2.5/image-to-video 模型生成视频
    
    Args:
        api_key: WaveSpeed API key
        prompt: 文字描述
        image_url: 图片 URL
        resolution: 分辨率（480p, 720p, 1080p）
        duration: 时长（3-10秒）
        enable_prompt_expansion: 是否启用提示词扩展
        seed: 随机种子（默认 -1）
    
    Returns:
        dict: 包含 success, output_url, api_request, api_response, error 的字典
    """
    url = "https://api.wavespeed.ai/api/v3/alibaba/wan-2.5/image-to-video"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    payload = {
        "resolution": resolution,
        "duration": duration,
        "enable_prompt_expansion": enable_prompt_expansion,
        "seed": seed,
        "image": image_url,
        "prompt": prompt
    }
    
    # 保存请求参数用于日志
    api_request = {
        "url": url,
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer ***"
        },
        "payload": {
            "resolution": resolution,
            "duration": duration,
            "enable_prompt_expansion": enable_prompt_expansion,
            "seed": seed,
            "image": image_url,
            "prompt": prompt
        }
    }
    
    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.error(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}",
            'api_request': api_request,
            'api_response': {}
        }
    
    # 轮询结果
    poll_url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    poll_headers = {"Authorization": f"Bearer {api_key}"}
    full_response = None
    
    while True:
        poll_response = requests.get(poll_url, headers=poll_headers)
        if poll_response.status_code == 200:
            result = poll_response.json()["data"]
            status = result["status"]
            full_response = result
            
            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                output_url = result["outputs"][0]
                logger.info(f"Task completed. URL: {output_url}")
                return {
                    'success': True,
                    'output_url': output_url,
                    'api_request': api_request,
                    'api_response': full_response,
                    'message': "Video generated successfully."
                }
            elif status == "failed":
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Task failed: {error_msg}")
                return {
                    'success': False,
                    'error': f"Task failed: {error_msg}",
                    'api_request': api_request,
                    'api_response': full_response
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.error(f"Error: {poll_response.status_code}, {poll_response.text}")
            return {
                'success': False,
                'error': f"Error: {poll_response.status_code}, {poll_response.text}",
                'api_request': api_request,
                'api_response': full_response if full_response else {}
            }
        
        time.sleep(0.5)


def wan_2_6_image_to_video(
    api_key: str,
    prompt: str,
    image_url: str,
    resolution: str = "720p",
    duration: int = 5,
    shot_type: str = "single",
    enable_prompt_expansion: bool = False,
    seed: int = -1,
    enable_audio: bool = False
) -> Dict[str, Any]:
    """
    使用 alibaba/wan-2.6/image-to-video 模型生成视频
    
    Args:
        api_key: WaveSpeed API key
        prompt: 文字描述
        image_url: 图片 URL
        resolution: 分辨率（480p, 720p, 1080p）
        duration: 时长（3-10秒）
        shot_type: 镜头类型（默认 "single"）
        enable_prompt_expansion: 是否启用提示词扩展
        seed: 随机种子（默认 -1）
        enable_audio: 是否生成音频
    
    Returns:
        dict: 包含 success, output_url, api_request, api_response, error 的字典
    """
    url = "https://api.wavespeed.ai/api/v3/alibaba/wan-2.6/image-to-video"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    payload = {
        "resolution": resolution,
        "duration": duration,
        "shot_type": shot_type,
        "enable_prompt_expansion": enable_prompt_expansion,
        "seed": seed,
        "image": image_url,
        "prompt": prompt
    }
    
    # 如果启用音频，添加 enable_audio 参数
    if enable_audio:
        payload["enable_audio"] = True
    
    # 保存请求参数用于日志
    api_request = {
        "url": url,
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer ***"
        },
        "payload": payload.copy()
    }
    
    begin = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()["data"]
        request_id = result["id"]
        logger.info(f"Task submitted successfully. Request ID: {request_id}")
    else:
        error_text = response.text
        try:
            error_json = response.json()
            error_text = json.dumps(error_json, ensure_ascii=False)
        except:
            pass
        logger.error(f"Error: {response.status_code}, {error_text}")
        return {
            'success': False,
            'error': f"Error: {response.status_code}, {error_text}",
            'api_request': api_request,
            'api_response': {}
        }
    
    # 轮询结果
    poll_url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
    poll_headers = {"Authorization": f"Bearer {api_key}"}
    full_response = None
    
    while True:
        poll_response = requests.get(poll_url, headers=poll_headers)
        if poll_response.status_code == 200:
            result = poll_response.json()["data"]
            status = result["status"]
            full_response = result
            
            if status == "completed":
                end = time.time()
                logger.info(f"Task completed in {end - begin} seconds.")
                output_url = result["outputs"][0]
                logger.info(f"Task completed. URL: {output_url}")
                return {
                    'success': True,
                    'output_url': output_url,
                    'api_request': api_request,
                    'api_response': full_response,
                    'message': "Video generated successfully."
                }
            elif status == "failed":
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Task failed: {error_msg}")
                return {
                    'success': False,
                    'error': f"Task failed: {error_msg}",
                    'api_request': api_request,
                    'api_response': full_response
                }
            else:
                logger.info(f"Task still processing. Status: {status}")
        else:
            logger.error(f"Error: {poll_response.status_code}, {poll_response.text}")
            return {
                'success': False,
                'error': f"Error: {poll_response.status_code}, {poll_response.text}",
                'api_request': api_request,
                'api_response': full_response if full_response else {}
            }
        
        time.sleep(0.5)
