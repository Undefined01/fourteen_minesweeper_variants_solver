import torch
import torch.nn as nn


class SimpleOcr(nn.Module):
    def __init__(self, nc=3, leakyRelu=False):
        super(SimpleOcr, self).__init__()

        ks = [3, 3, 3, 3, 3, 3, 2]
        ps = [1, 1, 1, 1, 1, 1, 0]
        ss = [1, 1, 1, 1, 1, 1, 1]
        channel_sizes = [16, 32, 64, 64, 128, 128, 128]

        cnn = nn.Sequential()

        def convRelu(layer_idx, batch_normalization=False):
            input_channels = nc if layer_idx == 0 else channel_sizes[layer_idx - 1]
            output_channels = channel_sizes[layer_idx]
            cnn.add_module(f'conv{layer_idx}',
                           nn.Conv2d(input_channels, output_channels, 3, ss[layer_idx], ps[layer_idx]))
            if batch_normalization:
                cnn.add_module(f'batchnorm{layer_idx}', nn.BatchNorm2d(output_channels))
            cnn.add_module(f'relu{layer_idx}', nn.ReLU(True))

        convRelu(0)
        cnn.add_module('pooling{0}'.format(0), nn.MaxPool2d(2, 2))  # 64x16x64
        convRelu(1)
        cnn.add_module('pooling{0}'.format(1), nn.MaxPool2d(2, 2))  # 128x8x32
        convRelu(2, True)
        convRelu(3)
        cnn.add_module('pooling{0}'.format(2),
                       nn.MaxPool2d((2, 2), (2, 1), (0, 1)))  # 256x4x16
        convRelu(4, True)
        convRelu(5)
        cnn.add_module('pooling{0}'.format(3),
                       nn.MaxPool2d((2, 2), (2, 1), (0, 1)))  # 512x2x16
        convRelu(6, True)  # 512x1x16

        self.cnn = cnn

    def forward(self, input):
        return self.cnn(input)

def test():
    net = DdddOcr(1)
    x = torch.randn(1, 1, 128, 128)
    y = net(x)
    print(y.size())

if __name__ == '__main__':
    test()