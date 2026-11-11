from io import BytesIO

from PIL import Image, ImageOps
import torchvision.transforms as T

from app.utils.errors import InvalidImageError

MAX_PIXELS = 40_000_000


def build_transform(img: int, mean, std) -> T.Compose:
    # identical to tf_eval in the training notebooks
    return T.Compose(
        [
            T.Resize(int(img * 1.14)),
            T.CenterCrop(img),
            T.ToTensor(),
            T.Normalize(mean, std),
        ]
    )


def load_image(data: bytes) -> Image.Image:
    try:
        im = Image.open(BytesIO(data))
    except Exception as exc:  # PIL raises several unrelated types
        raise InvalidImageError(str(exc)) from exc
    # check before load(): a small file can decode into hundreds of MB
    if im.width * im.height > MAX_PIXELS:
        raise InvalidImageError(f"image is {im.width}x{im.height} pixels")
    try:
        im.load()
    except Exception as exc:
        raise InvalidImageError(str(exc)) from exc
    im = ImageOps.exif_transpose(im)  # phone photos are often rotated
    return im.convert("RGB")
