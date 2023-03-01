import os
from typing import Union, Optional

import cv2
import numpy as np
from random import randint, choice
from datetime import datetime
from PIL import Image
from moviepy.editor import VideoFileClip

from pil_round import pill_round_frame


def random_str(length: int = 4):
	return ''.join(choice('abcdefghijklmnopqrstuvwxyz1234567890') for i in range(length))


class RoundVideo(object):
	def __init__(self, custom_bg: Optional[bool] = False, bg_name: Optional[str] = None):
		self.custom_bg = custom_bg
		self.bg_name = bg_name if custom_bg is False else Image.open(bg_name)
		self.round_mask = cv2.imread('mask/output-onlinepngtools.jpg')
		self.cache_frame_n = random_str(4)

	def round_frame(self, frame: Union[np.ndarray, str], size, test_name = ''):
		if (type(frame) == str):
			frame = cv2.imread(frame)
		
		color_converted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		pil_image=Image.fromarray(color_converted)
		
		frame_size_w, frame_size_h = round((self.bg_name.size[0] / 100) * 75), round((self.bg_name.size[1] / 100) * 75)

		n_f = pill_round_frame(pil_image, self.bg_name, (frame_size_w, frame_size_h), 'dd')

		numpy_image = np.array(n_f) 
		result = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

		return result


	def round_video(self, original_video, ):
		cap = cv2.VideoCapture(original_video)
		width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
		height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
		size = int(width) if width > height else int(height)
		fps = cap.get(cv2.CAP_PROP_FPS)
		self.round_mask = cv2.resize(self.round_mask, (size, size))

		if self.custom_bg:
			if (self.bg_name.size < (width, height)):
				size = self.bg_name.size[0] if self.bg_name.size[0] > self.bg_name.size[1] else self.bg_name.size[1]

	
		out = cv2.VideoWriter("result_videos/video.mp4", 
							  cv2.VideoWriter_fourcc(*'mp4v'), 
							  fps, 
							  (640, 640))

		print(f"VIDEO FPS: {fps}\nVIDEO WIDTH: {width}\nVIDEO HEIGHT: {height}\nFINALY SIZE: {size}")

		while(True):
			ret, frame = cap.read()

			if ret and frame is not None:
				if self.custom_bg:
					frame = self.round_frame(frame, size)

				frame = cv2.resize(frame, (640, 640))
				out.write(frame)

			elif frame is None:
				out.release()
				audio_name = self.convert_video_to_audio_moviepy(original_video)
		
				if audio_name is not None:
				 	my_clip = VideoFileClip('result_videos/video.mp4')
				 	my_clip.write_videofile(r'result_videos/video_au.mp4', audio=audio_name)

				break


	def add_to_bg(self, bg, img2):
		brows, bcols = bg.shape[:2]
		rows,cols,channels = img2.shape

		# Below I have changed roi so that the image is displayed in the middle, and not in the upper left corner
		roi = bg[int(brows/2)-int(rows/2):int(brows/2)+int(rows/2), int(bcols/2)- 
		int(cols/2):int(bcols/2)+int(cols/2) ]

		img2gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
		ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
		mask_inv = cv2.bitwise_not(mask)

		img1_bg = cv2.bitwise_and(roi, roi,mask = mask_inv)
		img2_fg = cv2.bitwise_and(img2, img2,mask = mask)

		dst = cv2.add(img1_bg, img2_fg)
		bg[int(brows/2)-int(rows/2):int(brows/2)+int(rows/2), int(bcols/2)- 
		int(cols/2):int(bcols/2)+int(cols/2) ] = dst
		return bg 

	def convert_video_to_audio_moviepy(self, video_file, output_ext="mp3"):
		try:
			filename, ext = os.path.splitext(video_file)
			new_file_name = f"{filename}.{output_ext}"
			clip = VideoFileClip(video_file)
			clip.audio.write_audiofile(new_file_name)
	
			return new_file_name

		except:
			return None

