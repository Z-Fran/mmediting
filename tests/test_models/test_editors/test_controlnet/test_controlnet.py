# Copyright (c) OpenMMLab. All rights reserved.

import os.path as osp
import platform
from unittest import TestCase
from unittest.mock import MagicMock

import pytest
import torch
import torch.nn as nn
from mmengine.utils import digit_version
from mmengine.utils.dl_utils import TORCH_VERSION

from mmedit.registry import MODELS
from mmedit.structures import EditDataSample
from mmedit.utils import register_all_modules

test_dir = osp.join(osp.dirname(__file__), '../../../..', 'tests')
config_path = osp.join(test_dir, 'configs', 'diffuser_wrapper_cfg')
model_path = osp.join(test_dir, 'configs', 'tmp_weight')
ckpt_path = osp.join(test_dir, 'configs', 'ckpt')

register_all_modules()

stable_diffusion_v15_url = 'runwayml/stable-diffusion-v1-5'
config = dict(
    type='ControlStableDiffusion',
    vae=dict(type='AutoencoderKL', sample_size=64),
    unet=dict(
        sample_size=64,
        type='UNet2DConditionModel',
        down_block_types=('DownBlock2D', ),
        up_block_types=('UpBlock2D', ),
        block_out_channels=(32, ),
        cross_attention_dim=16,
    ),
    text_encoder=dict(
        type='ClipWrapper',
        clip_type='huggingface',
        pretrained_model_name_or_path=stable_diffusion_v15_url,
        subfolder='text_encoder'),
    tokenizer=stable_diffusion_v15_url,
    controlnet=dict(
        type='ControlNetModel',
        # from_pretrained=controlnet_canny_rul
        from_config=config_path  # train from scratch
    ),
    scheduler=dict(
        type='DDPMScheduler',
        from_pretrained=stable_diffusion_v15_url,
        subfolder='scheduler'),
    test_scheduler=dict(
        type='DDIMScheduler',
        from_pretrained=stable_diffusion_v15_url,
        subfolder='scheduler'),
    data_preprocessor=dict(type='EditDataPreprocessor'),
    enable_xformers=False,
    init_cfg=dict(type='init_from_unet'))


@pytest.mark.skipif(
    'win' in platform.system().lower(),
    reason='skip on windows due to limited RAM.')
class TestControlStableDiffusion(TestCase):

    def setUp(self):
        # mock SiLU
        if digit_version(TORCH_VERSION) <= digit_version('1.6.0'):
            from mmedit.models.editors.ddpm.denoising_unet import SiLU
            torch.nn.SiLU = SiLU
        control_sd = MODELS.build(config)
        assert not any([p.requires_grad for p in control_sd.vae.parameters()])
        assert not any(
            [p.requires_grad for p in control_sd.text_encoder.parameters()])
        assert not any([p.requires_grad for p in control_sd.unet.parameters()])
        self.control_sd = control_sd

    def test_init_weights(self):
        control_sd = self.control_sd
        # test init_from_unet
        control_sd.init_weights()

        # test init_convert_from_unet
        unet = dict(
            type='UNet2DConditionModel',
            down_block_types=('DownBlock2D', ),
            up_block_types=('UpBlock2D', ),
            block_out_channels=(32, ),
            cross_attention_dim=16)
        control_sd.init_cfg = dict(type='convert_from_unet', base_model=unet)
        control_sd.init_weights()

    def test_infer(self):
        control_sd = self.control_sd
        control = torch.ones([1, 3, 64, 64])

        def mock_encode_prompt(*args, **kwargs):
            return torch.randn(2, 5, 16)  # 2 for cfg

        encode_prompt = control_sd._encode_prompt
        control_sd._encode_prompt = mock_encode_prompt

        result = control_sd.infer(
            'an insect robot preparing a delicious meal',
            control=control,
            height=64,
            width=64,
            num_inference_steps=1,
            return_type='numpy')
        assert result['samples'].shape == (1, 3, 64, 64)

        control_sd._encode_prompt = encode_prompt

    def test_val_step(self):
        control_sd = self.control_sd
        data = dict(
            inputs=[
                dict(
                    target=torch.ones([3, 64, 64]),
                    source=torch.ones([3, 64, 64]))
            ],
            data_samples=[
                EditDataSample(
                    prompt='an insect robot preparing a delicious meal')
            ])

        def mock_encode_prompt(*args, **kwargs):
            return torch.randn(2, 5, 16)  # 2 for cfg

        encode_prompt = control_sd._encode_prompt
        control_sd._encode_prompt = mock_encode_prompt

        # control_sd.text_encoder = mock_text_encoder()
        output = control_sd.val_step(data)
        assert len(output) == 1
        control_sd._encode_prompt = encode_prompt

    def test_test_step(self):
        control_sd = self.control_sd
        data = dict(
            inputs=[
                dict(
                    target=torch.ones([3, 64, 64]),
                    source=torch.ones([3, 64, 64]))
            ],
            data_samples=[
                EditDataSample(
                    prompt='an insect robot preparing a delicious meal')
            ])

        def mock_encode_prompt(*args, **kwargs):
            return torch.randn(2, 5, 16)  # 2 for cfg

        encode_prompt = control_sd._encode_prompt
        control_sd._encode_prompt = mock_encode_prompt

        # control_sd.text_encoder = mock_text_encoder()
        output = control_sd.test_step(data)
        assert len(output) == 1
        control_sd._encode_prompt = encode_prompt

    def test_train_step(self):
        control_sd = self.control_sd
        data = dict(
            inputs=[
                dict(
                    target=torch.ones([3, 64, 64]),
                    source=torch.ones([3, 64, 64]))
            ],
            data_samples=[
                EditDataSample(
                    prompt='an insect robot preparing a delicious meal')
            ])

        optimizer = MagicMock()
        update_params = MagicMock()
        optimizer.update_params = update_params
        optim_wrapper = {'controlnet': optimizer}

        class mock_text_encoder(nn.Module):

            def __init__(self):
                super().__init__()

            def forward(self, *args, **kwargs):
                return [torch.randn(1, 5, 16)]

        control_sd.text_encoder = mock_text_encoder()

        control_sd.train_step(data, optim_wrapper)
