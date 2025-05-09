"""
SMSA – Social Media Super Agent
Author: The Sovereign
Version: Phase 1
Description:
    This script controls the automation of SMSA across Instagram and other platforms.
    The system must be modular, no-nonsense, efficient, and built to scale.
    
    Phase 1 focuses on:
    - Automating posting for Parent + Child accounts (Instagram-first)
    - Caption + hashtag insertion
    - Basic scheduling loop
    - Daily backup archive

INSTRUCTIONS FOR COPILOT:
    - Build minimal, modular code with zero bloat
    - Each class/function must serve a tactical function, no decorators or fluff
    - Only import necessary libraries. Avoid unused packages.
    - Prioritize future extensibility via class-based structure
    - Do not comment like a beginner. Comment only for function logic or control flow
    - All I/O paths will be absolute or relative to the SMSA root directory

Immediate Modules To Build:
    1. ContentQueue: Reads images/videos from /queue/
    2. CaptionManager: Loads randomized captions from /captions.json
    3. PostingBot: Posts to Instagram using Instagram API or Puppeteer fallback
    4. ScheduleRunner: Cron-style scheduler to execute timed actions
    5. BackupBot: Archives posted content into /storage/ with timestamp

Next Phase Modules (not in this file):
    - EngagementBot
    - DM_Bot
    - AnalyticsBot

Folder Structure Assumed:
    /SMSA
      ├── main.py
      ├── captions.json
      ├── /queue/
      ├── /storage/
      ├── .env

Execution Format:
    > python main.py [run_mode]
    Modes: post, backup, schedule

Lock in tactical minimalism. Begin coding from ContentQueue.
"""

import os
import shutil
import json
import random
from datetime import datetime
import time
from threading import Thread
from instagrapi import Client
from dotenv import load_dotenv
from agents.post_bot import PostBot
from agents.engage_bot import EngageBot
from agents.analytics_bot import AnalyticsBot
from agents.dm_bot import DMBot
from agents.backup_bot import BackupBot
from agents.scheduler import Scheduler
from core.config import Config
from core.credentials import CredentialsManager
from core.logging_utils import Logger

class ContentQueue:
    def __init__(self, queue_dir='queue', archive_dir='storage'):
        self.queue_dir = queue_dir
        self.archive_dir = archive_dir
        self.allowed_ext = ('.jpg', '.jpeg', '.png', '.mp4', '.mov')
        if not os.path.exists(self.queue_dir):
            os.makedirs(self.queue_dir)
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)

    def get_next_content(self):
        files = sorted([
            f for f in os.listdir(self.queue_dir)
            if f.lower().endswith(self.allowed_ext)
        ])
        if not files:
            return None
        return os.path.join(self.queue_dir, files[0])

    def mark_as_posted(self, file_path):
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{timestamp}_{filename}"
        dest_path = os.path.join(self.archive_dir, new_name)
        shutil.move(file_path, dest_path)
        return dest_path

class CaptionManager:
    def __init__(self, captions_file='captions.json'):
        self.captions_file = captions_file
        self.captions = self._load_captions()

    def _load_captions(self):
        if not os.path.exists(self.captions_file):
            return []
        with open(self.captions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and 'captions' in data:
            return data['captions']
        return []

    def get_random_caption(self):
        if not self.captions:
            return ""
        return random.choice(self.captions)

def logger(msg, level="INFO"):
    print(f"[{level}] {datetime.now().isoformat()} | {msg}")

class PostingBot:
    def __init__(self, session_file="session.json"):
        load_dotenv()
        self.username = os.getenv("officialmarionormil")
        self.password = os.getenv("Bk10ngh301!@$196179")
        self.session_file = session_file
        self.client = Client()
        self._login()

    def _login(self):
        # Try to load session for lower ban risk
        if os.path.exists(self.session_file):
            try:
                self.client.load_settings(self.session_file)
                logger("Loaded IG session from disk")
            except Exception as e:
                logger(f"Session load failed: {e}", "WARN")
        try:
            self.client.login(self.username, self.password)
            logger("Instagram login successful")
            self.client.dump_settings(self.session_file)
        except Exception as e:
            logger(f"Login failed: {e}", "ERROR")
            exit(1)

    def post(self, media_path, caption):
        try:
            if media_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                self.client.photo_upload(media_path, caption)
            elif media_path.lower().endswith(('.mp4', '.mov')):
                self.client.video_upload(media_path, caption)
            else:
                raise ValueError("Unsupported media format.")
            logger(f"Posted to Instagram: {media_path}", "SUCCESS")
            return True
        except Exception as e:
            logger(f"Post failed: {e}", "ERROR")
            return False

class ScheduleRunner:
    def __init__(self, interval_seconds, task):
        self.interval = interval_seconds
        self.task = task
        self.thread = Thread(target=self._run, daemon=True)
        self.running = False

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            self.task()
            time.sleep(self.interval)

class BackupBot:
    def __init__(self, queue_dir='queue', archive_dir='storage'):
        self.queue_dir = queue_dir
        self.archive_dir = archive_dir
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)

    def backup_all(self):
        files = [
            f for f in os.listdir(self.queue_dir)
            if os.path.isfile(os.path.join(self.queue_dir, f))
        ]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        for f in files:
            src = os.path.join(self.queue_dir, f)
            dst = os.path.join(self.archive_dir, f"{timestamp}_{f}")
            shutil.copy2(src, dst)

# Phase 2 AI Hooks (placeholders)
def ai_caption_gen(prompt):
    """Generate AI-powered captions."""
    pass

def viral_audio_fetcher(platform="tiktok"):
    """Fetch trending/viral audio."""
    pass

def auto_thumbnail_generator(frame):
    """Generate thumbnails automatically."""
    pass

def sentiment_sorter(comments_list):
    """Sort comments by sentiment."""
    pass

POST_INTERVAL_MINUTES = int(os.getenv('POST_INTERVAL_MINUTES', 60))

if __name__ == "__main__":
    config = Config()
    creds = CredentialsManager()
    post_bot = PostBot(config, queue=None)
    engage_bot = EngageBot(config)
    analytics_bot = AnalyticsBot(config)
    dm_bot = DMBot(config)
    backup_bot = BackupBot(config)
    scheduler = Scheduler(config)
    Logger.info("SMSA 4.1 Execution Agent initialized.")
    Logger.info(f"SMSA Autonomous Posting Agent started. Interval: {POST_INTERVAL_MINUTES} min")
    while True:
        try:
            # Example: prompt can be category, theme, or content hint
            prompt = "Write a viral Instagram caption for a motivational post about discipline."
            # Replace with dynamic prompt/content selection as needed
            media_path = None
            if hasattr(post_bot, 'queue') and post_bot.queue:
                media_path = post_bot.queue.get_next_content()
            if not media_path:
                Logger.info("No content available to post. Sleeping until next interval.")
            else:
                success = post_bot.post_content(media_path, prompt)
                if success and hasattr(post_bot.queue, 'mark_as_posted'):
                    post_bot.queue.mark_as_posted(media_path)
            Logger.info(f"Sleeping for {POST_INTERVAL_MINUTES} minutes.")
            time.sleep(POST_INTERVAL_MINUTES * 60)
        except KeyboardInterrupt:
            Logger.info("Autonomous posting loop stopped by user.")
            break
        except Exception as e:
            Logger.error(f"Error in autonomous posting loop: {e}")
            time.sleep(POST_INTERVAL_MINUTES * 60)