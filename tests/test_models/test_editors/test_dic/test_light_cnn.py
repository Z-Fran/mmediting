# Copyright (c) OpenMMLab. All rights reserved.
import pytest
import torch

# from mmedit.models.image_restorers.dic.light_cnn import MaxFeature
from mmedit.models.editors import MaxFeature
from mmedit.registry import MODELS


def test_max_feature():
    # cpu
    conv2d = MaxFeature(16, 16, filter_type='conv2d')
    x1 = torch.rand(3, 16, 16, 16)
    y1 = conv2d(x1)
    assert y1.shape == (3, 16, 16, 16)
    linear = MaxFeature(16, 16, filter_type='linear')
    x2 = torch.rand(3, 16)
    y2 = linear(x2)
    assert y2.shape == (3, 16)
    # gpu
    if torch.cuda.is_available():
        x1 = x1.cuda()
        x2 = x2.cuda()
        conv2d = conv2d.cuda()
        linear = linear.cuda()
        y1 = conv2d(x1)
        assert y1.shape == (3, 16, 16, 16)
        y2 = linear(x2)
        assert y2.shape == (3, 16)
    # filter_type should be conv2d or linear
    with pytest.raises(ValueError):
        MaxFeature(12, 12, filter_type='conv1d')


def test_light_cnn():
    cfg = dict(type='LightCNN', in_channels=3)
    net = MODELS.build(cfg)
    # cpu
    inputs = torch.rand((2, 3, 128, 128))
    output = net(inputs)
    assert output.shape == (2, 1)
    # gpu
    if torch.cuda.is_available():
        net = net.cuda()
        output = net(inputs.cuda())
        assert output.shape == (2, 1)
