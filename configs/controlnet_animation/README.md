# Controlnet Animation (2023)

> [Controlnet](https://github.com/lllyasviel/ControlNet) Application

> **Task**: controlnet_animation

<!-- [ALGORITHM] -->

## Abstract

<!-- [ABSTRACT] -->

It is difficult to avoid video frame flickering when using stable diffusion to generate video frame by frame.
Here we reproduce a method that effectively avoids video flickering, that is, using controlnet and multi-frame rendering.
[ControlNet](https://github.com/lllyasviel/ControlNet) is a neural network structure to control diffusion models by adding extra conditions.
[Multi-frame rendering](https://xanthius.itch.io/multi-frame-rendering-for-stablediffusion) is a community method to reduce flickering.
We use controlnet with hed condition and stable diffusion img2img for multi-frame rendering.

## Demos

prompt key words: a handsome man, silver hair, smiling, play basketball

<div align="center">
  <video src="https://user-images.githubusercontent.com/12782558/227149757-fd054d32-554f-45d5-9f09-319184866d85.mp4" width=1024/>
</div>

prompt key words: a handsome man

<div align="center">
  <video src="https://user-images.githubusercontent.com/12782558/227152129-d70d5f76-a6fc-4d23-97d1-a94abd08f95a.mp4" width=1024/>
</div>

&#8195;

**Change prompt to get different result**

prompt key words: a girl, black hair, white pants, smiling, play basketball

<div align="center">
  <video src="https://user-images.githubusercontent.com/12782558/227216038-38599164-2384-4a79-b65e-f98785d466bf.mp4" width=512/>
</div>

## Pretrained models

We use pretrained model from hugging face.

|                    Model                    | Dataset |                                     Download                                      |
| :-----------------------------------------: | :-----: | :-------------------------------------------------------------------------------: |
| [anythingv3 config](./anythingv3_config.py) |    -    | [stable diffusion model](https://huggingface.co/Linaqruf/anything-v3.0/tree/main) |

## Quick Start

There are two ways to try controlnet animation.

### 1. Use MMEdit inference API.

Running the following codes, you can get an generated animation video.

```python
from mmedit.edit import MMEdit

# Create a MMEdit instance and infer
editor = MMEdit(model_name='controlnet_animation')

prompt = 'a girl, black hair, T-shirt, smoking, best quality, extremely detailed'
negative_prompt = 'longbody, lowres, bad anatomy, bad hands, missing fingers, ' + \
                  'extra digit, fewer digits, cropped, worst quality, low quality'

# you can download the example video with this link
# https://user-images.githubusercontent.com/12782558/227418400-80ad9123-7f8e-4c1a-8e19-0892ebad2a4f.mp4
video = '/path/to/your/input/video.mp4'
save_path = '/path/to/your/output/video.mp4'

# Do the inference to get result
editor.infer(video=video, prompt=prompt, negative_prompt=negative_prompt, save_path=save_path)
```

### 2. Use controlnet animation gradio demo.

```python
python demo/gradio_controlnet_animation.py
```

## Citation

```bibtex
@misc{zhang2023adding,
  title={Adding Conditional Control to Text-to-Image Diffusion Models},
  author={Lvmin Zhang and Maneesh Agrawala},
  year={2023},
  eprint={2302.05543},
  archivePrefix={arXiv},
  primaryClass={cs.CV}
}
```
