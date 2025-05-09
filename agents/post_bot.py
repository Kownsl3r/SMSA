import os
from instagrapi import Client
import openai
from core.logging_utils import Logger

class PostBot:
    def __init__(self, config, queue):
        self.config = config
        self.queue = queue
        self.client = Client()
        self._login()
        self.openai_api_key = os.getenv('OPENAI_API_KEY') or getattr(config, 'openai_api_key', None)
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

    def _login(self):
        username = os.getenv('IG_USERNAME') or getattr(self.config, 'ig_username', None)
        password = os.getenv('IG_PASSWORD') or getattr(self.config, 'ig_password', None)
        if not username or not password:
            Logger.error('Instagram credentials not found.')
            raise Exception('Missing Instagram credentials')
        try:
            self.client.login(username, password)
            Logger.info('Instagram login successful')
        except Exception as e:
            Logger.error(f'Instagram login failed: {e}')
            raise

    def prioritize_content(self, content_list):
        # Example: Sort by engagement_score = likes + (2 * saves) + (3 * shares)
        return sorted(content_list, key=lambda x: x.get('engagement_score', 0), reverse=True)

    def generate_caption(self, prompt):
        if not self.openai_api_key:
            Logger.error('OpenAI API key not set. Using prompt as caption.')
            return prompt
        try:
            response = openai.ChatCompletion.create(
                model='gpt-4',
                messages=[
                    {"role": "system", "content": "You are a viral social media copywriter."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60,
                temperature=0.8
            )
            caption = response.choices[0].message['content'].strip()
            Logger.info('Generated AI caption.')
            return caption
        except Exception as e:
            Logger.error(f'OpenAI caption generation failed: {e}')
            return prompt

    def post_content(self, media_path, prompt):
        caption = self.generate_caption(prompt)
        try:
            if media_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                self.client.photo_upload(media_path, caption)
            elif media_path.lower().endswith(('.mp4', '.mov')):
                self.client.video_upload(media_path, caption)
            else:
                raise ValueError('Unsupported media format.')
            Logger.info(f'Posted to Instagram: {media_path}')
            return True
        except Exception as e:
            Logger.error(f'Post failed: {e}')
            return False 