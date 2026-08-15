from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import subprocess
import os

app = FastAPI()

class VideoRequest(BaseModel):
    video_urls: List[str]
    audio_path: str = "/tmp/voiceover.mp3"
    output_path: str = "/tmp/final_output.mp4"
    clip_duration: float = 3.0  # Har clip 3 second ki hogi

@app.post("/render")
def render_video(data: VideoRequest):
    try:
        filter_str = ""
        inputs = ""
        
        for i, url in enumerate(data.video_urls):
            inputs += f"-i {url} "
            # Yahan color enhancement (contrast, saturation, brightness) add kar diya hai
            filter_str += f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,eq=contrast=1.15:saturation=1.25:brightness=0.02,trim=duration={data.clip_duration},setpts=PTS-STARTPTS[v{i}];"
        
        concat_inputs = "".join([f"[v{i}]" for i in range(len(data.video_urls))])
        filter_str += f"{concat_inputs}concat=n={len(data.video_urls)}:v=1:a=0[outv]"
        
        # Audio aur color-corrected video ko combine karenge
        cmd = f"ffmpeg -y {inputs} -i {data.audio_path} -filter_complex \"{filter_str}\" -map \"[outv]\" -map {len(data.video_urls)}:a -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest {data.output_path}"
        
        os.system(cmd)
        
        return {"status": "success", "file": data.output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}
