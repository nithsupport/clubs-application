from datetime import datetime
from PIL import Image


def create_unique_filename(f):
    current_time = datetime.now().strftime('%Y%m%d%H%M%S%f')
    return f'{current_time}_{f.name}'

def compress_img(image_name, new_size_ratio=0.8, quality=90, width=None, height=None):
    # load the image to memory
    img = Image.open(image_name)
    current_size = len(img.fp.read())
    if (350 * 1024) <= current_size:
        if new_size_ratio < 1.0:
            # if resizing ratio is below 1.0, then multiply width & height with this ratio to reduce image size
            img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), Image.ANTIALIAS)
        elif width and height:
            # if width and height are set, resize with them instead
            img = img.resize((width, height), Image.ANTIALIAS)
    
    try:
        # save the image with the corresponding quality and optimize set to True
        img.save(image_name, quality=quality, optimize=True)
    except OSError:
        # convert the image to RGB mode first
        img = img.convert("RGB")
        # save the image with the corresponding quality and optimize set to True
        img.save(image_name, quality=quality, optimize=True)
    
    return img
    
    


