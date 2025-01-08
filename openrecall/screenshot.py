import os
import time
import platform

import mss
import numpy as np
from PIL import Image
import pyscreenshot  # Make sure pyscreenshot is installed

from openrecall.config import screenshots_path, args
from openrecall.database import insert_entry
from openrecall.nlp import get_embedding
from openrecall.ocr import extract_text_from_image
from openrecall.utils import (
    get_active_app_name,
    get_active_window_title,
    is_user_active,
)


def mean_structured_similarity_index(img1, img2, L=255):
    # This calculates the SSIM (Structural Similarity Index)
    K1, K2 = 0.01, 0.03
    C1, C2 = (K1 * L) ** 2, (K2 * L) ** 2

    def rgb2gray(img):
        return 0.2989 * img[..., 0] + 0.5870 * img[..., 1] + 0.1140 * img[..., 2]

    img1_gray = rgb2gray(img1)
    img2_gray = rgb2gray(img2)
    mu1 = np.mean(img1_gray)
    mu2 = np.mean(img2_gray)
    sigma1_sq = np.var(img1_gray)
    sigma2_sq = np.var(img2_gray)
    sigma12 = np.mean((img1_gray - mu1) * (img2_gray - mu2))
    ssim_index = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / (
        (mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2)
    )
    return ssim_index


def is_similar(img1, img2, similarity_threshold=0.9):
    # Compare two screenshots using SSIM
    similarity = mean_structured_similarity_index(img1, img2)
    return similarity >= similarity_threshold


def take_screenshots(monitor=1):
    """
    Takes screenshots of either:
      - every monitor using MSS (default),
      - or entire screen on Wayland (using pyscreenshot).
    """
    screenshots = []

    # Detect if we are on Linux + Wayland
    is_linux = platform.system().lower() == "linux"
    is_wayland = os.getenv("XDG_SESSION_TYPE", "").lower() == "wayland"

    if is_linux and is_wayland:
        # Wayland - use pyscreenshot to grab the entire screen
        # (pyscreenshot doesn't handle multi-monitor as easily, so this is a single image)
        shot = pyscreenshot.grab()
        shot_np = np.array(shot)
        # Pyscreenshot needs another order here in order for the color to look correct
        shot_np = shot_np[:, :, [0, 1, 2]]
        screenshots.append(shot_np)
    else:
        # Non-Wayland fallback (MSS)
        with mss.mss() as sct:
            for idx, mon in enumerate(sct.monitors):
                # If primary_monitor_only is True, only capture monitor #1
                if args.primary_monitor_only and idx != 1:
                    continue
                screenshot = np.array(sct.grab(mon))
                # Convert from BGRA to BGR in correct order for downstream usage
                screenshot = screenshot[:, :, [2, 1, 0]]
                screenshots.append(screenshot)

    return screenshots


def record_screenshots_thread():
    """
    Continuously takes screenshots, checks if they have changed
    (using SSIM), and saves them along with extracted text to DB.
    """
    # Disables parallelism warnings from HF tokenizers if used.
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    last_screenshots = take_screenshots()

    while True:
        if not is_user_active():
            # Sleep if user is inactive
            time.sleep(3)
            continue

        screenshots = take_screenshots()
        # Compare new screenshots to old ones
        for i, screenshot in enumerate(screenshots):
            if i >= len(last_screenshots):
                # Just in case the number of screenshots changed
                last_screenshots.append(screenshot)

            last_screenshot = last_screenshots[i]

            # If the new screenshot is different enough, record it
            if not is_similar(screenshot, last_screenshot):
                last_screenshots[i] = screenshot
                image = Image.fromarray(screenshot)
                timestamp = int(time.time())
                image.save(
                    os.path.join(screenshots_path, f"{timestamp}.webp"),
                    format="webp",
                    lossless=True,
                )
                text = extract_text_from_image(screenshot)
                embedding = get_embedding(text)
                active_app_name = get_active_app_name()
                active_window_title = get_active_window_title()
                insert_entry(
                    text, timestamp, embedding, active_app_name, active_window_title
                )

        time.sleep(3)
