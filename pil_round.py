from PIL import Image, ImageDraw


def prepare_mask(size, antialias = 2):
	mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
	ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
	return mask.resize(size, Image.Resampling.LANCZOS)


def crop(im, s):
	w, h = im.size
	k = w / s[0] - h / s[1]
	if k > 0: im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
	elif k < 0: im = im.crop((0, (h - w) / 2, w, (h + w) / 2))
	return im.resize(s, Image.Resampling.LANCZOS)


def pill_round_frame(image, mask, size, f_name):
	f_name = f'{f_name}.png'

	image = crop(image, size)
	image.putalpha(prepare_mask(size, 4))
	#im.save(f"cache/{f_name}")

	mask.paste(image, (round((mask.size[0]-image.size[0]) / 2), round((mask.size[1]-image.size[1])/2)),  image)

	return mask
