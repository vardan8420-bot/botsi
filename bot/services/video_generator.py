"""
Сервис генерации простых видео (MP4) из изображений и/или текста.
Использует moviepy. Требует установленный ffmpeg (imageio-ffmpeg ставится из requirements).
"""
from typing import List, Optional
import os


class VideoGenerator:
    def __init__(self):
        pass

    def generate_slideshow(
        self,
        image_paths: List[str],
        captions: Optional[List[str]] = None,
        duration_per_image: float = 3.0,
        output_path: str = "output.mp4",
        fps: int = 30,
        resolution: Optional[tuple] = None,
        audio_path: Optional[str] = None,
    ) -> str:
        """
        Создать простое видео-слайдшоу из изображений.
        Возвращает путь к созданному файлу.
        """
        from moviepy.editor import ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip, AudioFileClip

        clips = []
        for idx, img in enumerate(image_paths):
            clip = ImageClip(img).set_duration(duration_per_image)
            if resolution:
                clip = clip.resize(newsize=resolution)

            if captions and idx < len(captions) and captions[idx]:
                txt = TextClip(captions[idx], fontsize=48, color='white', method='caption', size=clip.size)
                txt = txt.set_duration(duration_per_image).set_position(('center', 'bottom'))
                clip = CompositeVideoClip([clip, txt])

            clips.append(clip)

        final = concatenate_videoclips(clips, method="compose")

        if audio_path and os.path.exists(audio_path):
            audio = AudioFileClip(audio_path)
            final = final.set_audio(audio)

        final.write_videofile(output_path, fps=fps)
        return output_path
