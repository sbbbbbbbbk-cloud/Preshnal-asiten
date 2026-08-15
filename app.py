from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import subprocess

app = FastAPI()

class VideoRequest(BaseModel):
    video_urls: List[str]
    audio_path: str = "/tmp/audio.mp3"
    output_path: str = "/tmp/output.mp4"
    clip_duration: float = 2.0

@app.get("/")
def home():
    return {"status": "FastAPI is running!"}

@app.post("/render")
def render_video(data: VideoRequest):
    try:
        input_args = []
        filter_str = ""
        
        for i, url in enumerate(data.video_urls):
            input_args.extend(["-i", url])
            filter_str += f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS[v{i}];"
            
        concat_inputs = "".join([f"[v{i}]" for i in range(len(data.video_urls))])
        filter_str += f"{concat_inputs}concat=n={len(data.video_urls)}:v=1:a=0[v]"
        
        cmd = [
            "ffmpeg", "-y",
            *input_args,
            "-i", data.audio_path,
            "-filter_complex", filter_str,
            "-map", "[v]",
            "-map", f"{len(data.video_urls)}:a",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest",
            data.output_path
        ]
        
        subprocess.run(cmd, check=True)
        return {"status": "success", "output": data.output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}
