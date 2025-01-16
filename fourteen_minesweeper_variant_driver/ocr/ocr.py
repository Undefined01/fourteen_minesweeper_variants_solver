from PIL import Image
import onnxruntime as ort
import numpy as np
from pathlib import Path


CLASSES = ['#na#', '0', '1', '2', '3', '4', '5', '6', '7', '8', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'blank', 'circle', 'cross', 'flag', 'hidden', 'sqrt']

def decode_one(output: np.ndarray) -> list[str]:
    decoded = []
    last_item = 0
    for item in output:
        item = item
        if item == last_item:
            continue
        else:
            last_item = item
        if item != 0:
            decoded.append(CLASSES[item])
    return decoded

def predict(image: Image.Image | np.ndarray) -> list[str]:
    if isinstance(image, np.ndarray):
        if image.shape[2] != 3:
            raise ValueError(f'Image must have 3 channels, got {image.shape}')
        if image.shape != (64, 64, 3):
            image = Image.fromarray(image)
            return predict(image)
        if image.dtype != np.float32:
            image = image.astype(np.float32)
        input = image
    else:
        image.resize((64, 64))
        input = np.array(image, dtype=np.float32)
    input = input.transpose(2, 0, 1)
    input = input / 255

    ort_sess = ort.InferenceSession(Path(__file__).with_name('ocr_model.onnx'))
    outputs = ort_sess.run(None, {'onnx::Conv_0': input.reshape(1, 3, 64, 64)})
    outputs = outputs[0]
    outputs = outputs.argmax(2).transpose(1, 0)
    
    return decode_one(outputs[0])

if __name__ == '__main__':
    image = Image.open('test.png')
    print(' '.join(predict(image)))
