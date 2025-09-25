from ..video.generator import create_multi_frame_video
import os

script = '''Title: Introduction to Linear Regression
Welcome to this short lesson on linear regression.
In this video, we'll cover:
1) What is linear regression?
2) The simple linear model y = mx + b.
Thank you for watching!'''

print('Testing create_multi_frame_video...')
print('Script content:')
print(repr(script))

# Test line splitting
lines = [line.strip() for line in script.split('\n') if line.strip()]
print(f'\nLines after splitting: {len(lines)}')
for i, line in enumerate(lines, 1):
    print(f'Line {i}: {repr(line)}')

os.makedirs('bucket/videos', exist_ok=True)
try:
    video_path = create_multi_frame_video(script, 'bucket/videos/debug_test.mp4', frame_duration=3.0)
    print(f'\nSUCCESS: Video created at {video_path}')
    if os.path.exists(video_path):
        print(f'File exists and size: {os.path.getsize(video_path)} bytes')
    else:
        print('ERROR: File does not exist')
except Exception as e:
    print(f'\nERROR: {e}')
    import traceback
    traceback.print_exc()