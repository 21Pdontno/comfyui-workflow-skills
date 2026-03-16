# ComfyUI Node Patterns Reference

## Core Node Patterns

### 1. Text-to-Image (Basic)

```
CheckpointLoader → model, clip, vae
    ├→ [CLIP] CLIPTextEncode (positive) → positive conditioning
    ├→ [CLIP] CLIPTextEncode (negative) → negative conditioning
    ├→ [EmptyLatentImage] → latent
    └→ KSampler(model, positive, negative, latent) → sampled latent
        → VAEDecode(model, sampled latent) → image
        → SaveImage
```

**JSON structure:**
```json
{
  "1": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {"ckpt_name": "model.safetensors"},
    "_meta": {"title": "[Model] Checkpoint Loader - Load main model"}
  },
  "2": {
    "class_type": "CLIPTextEncode",
    "inputs": {"text": "positive prompt", "clip": ["1", 1]},
    "_meta": {"title": "[Prompt] Positive Text Encode - Describe what you want"}
  },
  "3": {
    "class_type": "CLIPTextEncode",
    "inputs": {"text": "negative prompt", "clip": ["1", 1]},
    "_meta": {"title": "[Prompt] Negative Text Encode - Describe what to avoid"}
  },
  "4": {
    "class_type": "EmptyLatentImage",
    "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
    "_meta": {"title": "[Latent] Empty Latent - Define output resolution | 1024x1024 for SDXL, 512x512 for SD1.5"}
  },
  "5": {
    "class_type": "KSampler",
    "inputs": {
      "model": ["1", 0],
      "seed": 123456,
      "steps": 20,
      "cfg": 8.0,
      "sampler_name": "euler",
      "scheduler": "normal",
      "positive": ["2", 0],
      "negative": ["3", 0],
      "latent_image": ["4", 0]
    },
    "_meta": {"title": "[Sampling] KSampler - Main generation sampler | steps: quality vs speed, cfg: prompt adherence"}
  },
  "6": {
    "class_type": "VAEDecode",
    "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
    "_meta": {"title": "[Decode] VAE Decode - Convert latent to visible image"}
  },
  "7": {
    "class_type": "SaveImage",
    "inputs": {"images": ["6", 0], "filename_prefix": "output"},
    "_meta": {"title": "[Output] Save Image - Save generated image to disk"}
  }
}
```

### 2. Image-to-Image

Same as Text-to-Image but replace EmptyLatentImage with:
```
LoadImage → VAEEncode → encoded latent → KSampler
```

```json
{
  "4": {
    "class_type": "LoadImage",
    "inputs": {"image": "input.png"},
    "_meta": {"title": "[Input] Load Image - Load source image"}
  },
  "5": {
    "class_type": "VAEEncode",
    "inputs": {"pixels": ["4", 0], "vae": ["1", 2]},
    "_meta": {"title": "[Encode] VAE Encode - Convert image to latent space"}
  }
}
```

### 3. Qwen Image (Chinese-friendly model)

```json
{
  "1": {
    "class_type": "QwenLoader",
    "inputs": {
      "qwen_name": "qwen_image_2512_fp8_e4m3fn.safetensors",
      "text_encoder_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
      "vae_name": "qwen_image_vae.safetensors"
    },
    "_meta": {"title": "[Model] Qwen Loader - Load Qwen Image model | Supports Chinese prompts natively"}
  },
  "2": {
    "class_type": "EmptyQwenImageLayeredLatentImage",
    "inputs": {"width": 1024, "height": 1024},
    "_meta": {"title": "[Latent] Empty Qwen Latent - Define generation canvas"}
  },
  "3": {
    "class_type": "TextImageEncodeQwenVL",
    "inputs": {
      "text": "描述你想要的画面",
      "text_encoder": ["1", 1],
      "width": 1024,
      "height": 1024
    },
    "_meta": {"title": "[Prompt] Qwen Text/Image Encode - Encode prompt with visual understanding"}
  },
  "4": {
    "class_type": "KSampler",
    "inputs": {
      "model": ["1", 0],
      "seed": 42,
      "steps": 25,
      "cfg": 4.5,
      "sampler_name": "uni_pc_bh2",
      "scheduler": "beta",
      "positive": ["3", 0],
      "negative": ["3", 1],
      "latent_image": ["2", 0]
    },
    "_meta": {"title": "[Sampling] KSampler - Qwen sampling | cfg 4.5 is recommended for Qwen"}
  },
  "5": {
    "class_type": "VAEDecode",
    "inputs": {"samples": ["4", 0], "vae": ["1", 2]},
    "_meta": {"title": "[Decode] VAE Decode"}
  },
  "6": {
    "class_type": "SaveImage",
    "inputs": {"images": ["5", 0], "filename_prefix": "qwen_output"},
    "_meta": {"title": "[Output] Save Qwen Output"}
  }
}
```

### 4. LoRA Application

Insert between CheckpointLoader and CLIPTextEncode:
```json
{
  "1.5": {
    "class_type": "LoraLoader",
    "inputs": {
      "model": ["1", 0],
      "clip": ["1", 1],
      "lora_name": "my_lora.safetensors",
      "strength_model": 0.8,
      "strength_clip": 0.8
    },
    "_meta": {"title": "[Model] LoRA Loader - Apply style/character LoRA | strength: 0.5-1.0 typical"}
  }
}
```
Then change KSampler to use `["1.5", 0]` for model and `["1.5", 1]` for clip.

### 5. IP-Adapter (Image Reference)

```json
{
  "10": {
    "class_type": "IPAdapterUnifiedLoader",
    "inputs": {
      "model": ["1", 0],
      "clip": ["1", 1],
      "ipadapter": "ip_adapter_plus_comfyui.safetensors"
    },
    "_meta": {"title": "[Reference] IP-Adapter Loader - Load IP-Adapter model"}
  },
  "11": {
    "class_type": "IPAdapter",
    "inputs": {
      "model": ["10", 0],
      "ipadapter": ["10", 1],
      "image": ["4", 0],
      "weight": 0.7,
      "start_at": 0.0,
      "end_at": 1.0,
      "positive": ["2", 0],
      "negative": ["3", 0]
    },
    "_meta": {"title": "[Reference] IP-Adapter Apply - Apply image style reference | weight: 0.5-0.8 for balanced results"}
  }
}
```

### 6. ControlNet

```json
{
  "20": {
    "class_type": "ControlNetLoader",
    "inputs": {"control_net_name": "control_v11p_sd15_canny_fp16.safetensors"},
    "_meta": {"title": "[ControlNet] Loader - Load Canny edge detector"}
  },
  "21": {
    "class_type": "Canny",
    "inputs": {"image": ["4", 0], "low_threshold": 100, "high_threshold": 200},
    "_meta": {"title": "[Preprocess] Canny Edge Detection - Extract edges from input image"}
  },
  "22": {
    "class_type": "ControlNetApply",
    "inputs": {
      "positive": ["2", 0],
      "negative": ["3", 0],
      "control_net": ["20", 0],
      "image": ["21", 0],
      "strength": 0.7
    },
    "_meta": {"title": "[ControlNet] Apply - Apply edge guidance to generation | strength: 0.5-1.0"}
  }
}
```

### 7. Batch Generation (Multiple Seeds)

For generating 3-5 variants, duplicate the KSampler→VAEDecode→SaveImage chain with different seeds:

```json
{
  "5": {
    "class_type": "KSampler",
    "inputs": {"seed": 100001, "...other inputs same..."},
    "_meta": {"title": "[Variant 1] KSampler - First variant"}
  },
  "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "..."}, "_meta": {"title": "[Variant 1] VAE Decode"}},
  "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "variant_1"}, "_meta": {"title": "[Variant 1] Save"}},

  "15": {
    "class_type": "KSampler",
    "inputs": {"seed": 100002, "...same inputs, different seed..."},
    "_meta": {"title": "[Variant 2] KSampler - Second variant"}
  },
  "16": {"class_type": "VAEDecode", "inputs": {"samples": ["15", 0]}, "_meta": {"title": "[Variant 2] VAE Decode"}},
  "17": {"class_type": "SaveImage", "inputs": {"images": ["16", 0], "filename_prefix": "variant_2"}, "_meta": {"title": "[Variant 2] Save"}},

  "25": {
    "class_type": "KSampler",
    "inputs": {"seed": 100003},
    "_meta": {"title": "[Variant 3] KSampler - Third variant"}
  },
  "26": {"class_type": "VAEDecode", "inputs": {"samples": ["25", 0]}, "_meta": {"title": "[Variant 3] VAE Decode"}},
  "27": {"class_type": "SaveImage", "inputs": {"images": ["26", 0], "filename_prefix": "variant_3"}, "_meta": {"title": "[Variant 3] Save"}}
}
```

## Sampler Reference

| Sampler | Speed | Quality | Best For |
|---------|-------|---------|----------|
| euler | Fast | Good | Quick previews |
| euler_ancestral | Fast | Good | Creative/varied results |
| dpmpp_2m | Medium | Very Good | General purpose (recommended) |
| dpmpp_2m_sde | Medium | Excellent | Best quality |
| dpmpp_sde | Medium | Excellent | Detailed images |
| uni_pc_bh2 | Fast | Very Good | Qwen Image |
| ddim | Medium | Good | Stable, predictable |

## Scheduler Reference

| Scheduler | Character |
|-----------|-----------|
| normal | Standard (most models) |
| karras | Better for low step counts |
| exponential | Similar to karras |
| beta | For diffusion models (Qwen, Flux) |
| simple | Basic linear schedule |
| sgm_uniform | SD3/Flux models |
| gits | Some video models |

## VRAM Budget (12GB VRAM Reference)

| Configuration | Est. VRAM |
|---------------|-----------|
| SD1.5 + standard pipeline | ~4GB |
| SDXL FP16 | ~8GB |
| SDXL FP8 | ~5GB |
| Qwen Image FP8 | ~8-10GB |
| FLUX Dev FP8 | ~10GB |
| SDXL + ControlNet + IP-Adapter | ~10GB |
| SD1.5 + multiple ControlNets | ~6GB |
