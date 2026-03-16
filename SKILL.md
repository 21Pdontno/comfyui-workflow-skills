---
name: comfyui-workflow-master
description: >-
  Full-lifecycle ComfyUI workflow automation. Understands natural language, generates workflows with annotations,
  validates, auto-fixes errors, downloads models, and provides recommendations.
  Triggers: ComfyUI workflow, generate workflow, AI image pipeline, text-to-image, image editing,
  e-commerce product photography, Qwen image generation, Wan image generation.
---

# ComfyUI Workflow Master

## Overview

Full automation for ComfyUI workflow creation from natural language. Covers the complete lifecycle:

1. **Understand** natural language requirements and decompose into modules
2. **Query** available nodes, models, and capabilities from the live ComfyUI instance
3. **Design** workflow architecture with proper node connections and data flow
4. **Generate** complete ComfyUI workflow JSON with detailed Chinese annotations on every node
5. **Validate** workflow via ComfyUI API before execution
6. **Execute** workflow and monitor progress
7. **Auto-fix** errors with intelligent analysis (up to 5 iterations)
8. **Advise** on model selection, parameter tuning, and optimization

## Environment

- **ComfyUI URL**: http://127.0.0.1:8188
- **GPU**: NVIDIA GPU with 12GB+ VRAM recommended
- **API Client Script**: SKILL_DIR/scripts/comfyui_api.py

### Pre-flight Check

Before any operation, verify connectivity and get current environment info:

```
python SKILL_DIR/scripts/comfyui_api.py
```

To query available nodes interactively:

```python
import sys; sys.path.insert(0, 'SKILL_DIR/scripts'); import comfyui_api
c = comfyui_api.connect()
nodes = c.get_node_info()
models = c.get_available_models_summary()
```

## Architecture: Multi-Agent Debug Pattern (inspired by ComfyUI-Copilot)

When debugging a failed workflow, adopt a **coordinator + specialist** approach:

1. **Debug Coordinator** (the agent itself): Validates, analyzes errors, delegates
2. **Connection Specialist**: Fixes missing/broken node connections
3. **Parameter Specialist**: Fixes invalid parameter values, missing models
4. **Structure Specialist**: Removes incompatible nodes, restructures workflow

### Debug Loop Protocol

```
1. Validate workflow (comfyui_api.validate_workflow)
2. If valid -> Execute and check for runtime errors
3. If validation errors:
   a. Parse error messages to classify type
   b. Connection errors -> Fix links, check type compatibility
   c. Parameter errors -> Find valid values from node_info, replace
   d. Missing model -> Check available models, suggest download or alternative
   e. VRAM OOM -> Reduce resolution, use fp8, reduce batch
4. Re-validate after each fix
5. Repeat until valid or max 5 iterations
6. Report results to user
```

## Workflow JSON Format Reference

A ComfyUI workflow (API format) is a JSON object where:
- **Keys** = unique string node IDs (e.g., "3", "10", "load_model")
- **Values** = node definitions: class_type + inputs + optional _meta

### Input Types

- **Primitive (int/float/str/bool)**: Direct value, e.g., "seed": 123456
- **Link (connection)**: [source_node_id, output_slot], e.g., ["4", 0]
- **Combo/select**: String value from allowed list, e.g., "sampler_name": "euler"

### Annotation Standard (MANDATORY for all nodes)

Every node MUST have `_meta.title` in this format:

```
[Module Name] Node Function - Description | Tuning Advice
```

Chinese example:

```json
"_meta": {
  "title": "[Scene Gen] KSampler - Main sampler for generation | Higher steps=more detail but slower"
}
```

## Key Node Patterns

### Pattern 1: Standard Text-to-Image (SDXL/SD1.5)

```
CheckpointLoaderSimple -> (MODEL[0], CLIP[1], VAE[2])
  CLIP -> CLIPTextEncode(positive prompt) -> CONDITIONING
  CLIP -> CLIPTextEncode(negative prompt) -> CONDITIONING
  EmptyLatentImage -> LATENT
  KSampler(model=MODEL, positive, negative, latent) -> LATENT
  VAEDecode(samples=LATENT, vae=VAE) -> IMAGE
  SaveImage(images=IMAGE)
```

Link format: ["node_id", output_slot_index]
Example: "model": ["1", 0] means output slot 0 of node 1

### Pattern 2: Qwen Image / Wan Text-to-Image (Simple API)

```json
{
  "1": {
    "class_type": "WanTextToImageApi",
    "inputs": {
      "model": "wan2.5-t2i-preview",
      "prompt": "product photo, warm lighting",
      "negative_prompt": "ugly, blurry, low quality",
      "width": 1024, "height": 1024, "seed": 123456
    },
    "_meta": {"title": "[Generation] Wan T2I API - Qwen-based image generation | Supports Chinese prompts"}
  },
  "2": {
    "class_type": "SaveImage",
    "inputs": {"images": ["1", 0], "filename_prefix": "wan_output"},
    "_meta": {"title": "[Output] Save Image"}
  }
}
```

### Pattern 3: Advanced Qwen with CLIP

```json
{
  "1": {
    "class_type": "CLIPLoader",
    "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image"},
    "_meta": {"title": "[Model] CLIP Loader - Load Qwen vision-language model | type must be qwen_image"}
  },
  "2": {
    "class_type": "TextEncodeQwenImageEdit",
    "inputs": {"clip": ["1", 0], "prompt": "describe what you want"},
    "_meta": {"title": "[Prompt] Qwen Image Encoder - Qwen-specific prompt encoding"}
  }
}
```

### Pattern 4: Image-to-Image

Replace EmptyLatentImage with LoadImage + VAEEncode. Set KSampler denoise 0.5-0.8.

### Pattern 5: LoRA Enhancement

Insert LoraLoader between CheckpointLoader and CLIPTextEncode. strength 0.5-1.0.

### Pattern 6: Batch Generation (3-5 Variants)

Duplicate KSampler + VAEDecode + SaveImage with different seeds (100001, 100002, 100003...).

## Critical: Always Query Before Designing

### Step A: Check Available Models

```python
import sys; sys.path.insert(0, 'SKILL_DIR/scripts'); import comfyui_api
c = comfyui_api.connect()
for folder, items in c.get_available_models_summary().items():
    if items: print(f'{folder}: {items}')
```

### Step B: Check Node Specs

```python
node_info = c.get_node_info()
# node_info['KSampler'] shows all required/optional inputs and output types
```

### Step C: Model System Compatibility

- **SDXL**: CheckpointLoaderSimple (all-in-one)
- **FLUX**: UNETLoader + DualCLIPLoader(clip_l + t5xxl) + VAELoader(ae.safetensors)
- **Wan 2.x**: WanVideoModelLoader + WanVideoVAELoader
- **Qwen Image**: CLIPLoader(type="qwen_image")
- **Hunyuan Image**: CLIPLoader(type="hunyuan_image")

## Workflow Generation Process

1. **Parse Intent**: Decompose into input assets, processing pipeline, output requirements
2. **Check Environment**: Pre-flight check models and nodes. Find alternatives if missing.
3. **Design Modules**: Break into logical groups, select nodes, set parameters
4. **Generate JSON**: All nodes with _meta.title annotations, descriptive IDs, matched data types
5. **Validate**: comfyui_api.validate_workflow() - fix errors and retry
6. **Execute**: comfyui_api.execute_workflow() with user permission

## Auto-Fix Error Reference

- **value not in list**: Query node_info for valid options
- **required input missing**: Add missing link or source node
- **Cannot find node**: Find alternative or suggest install
- **CUDA out of memory**: Lower resolution, use fp8, reduce batch
- **shape mismatch**: Match dimensions across pipeline
- **model not found**: Suggest download from HuggingFace/CivitAI
- **type mismatch**: Fix link to connect correct output slot

## E-Commerce Workflow Pattern

- **Module 1 - Input**: LoadImage + CLIPTextEncode (product description)
- **Module 2 - Scene (3-5 variants)**: IPAdapter/img2img + different seeds
- **Module 3 - Model/Figure (3-5 variants)**: ControlNet + IPAdapter + different seeds
- **Module 4 - Selling Point (3-5 variants)**: Crop-focused + detail prompts
- **Module 5 - Product Info (3-5 variants)**: Clean background + studio lighting

## VRAM Budget (12GB VRAM Reference)

- SD1.5: ~4GB | SDXL FP16: ~8GB | SDXL FP8: ~5GB
- Qwen FP8: ~8GB | FLUX FP8: ~10GB | SDXL+ControlNet+IPAdapter: ~10GB

## Sampler Reference

- **dpmpp_2m**: General purpose (recommended)
- **dpmpp_2m_sde**: Highest quality
- **euler**: Fast, good for previews
- **uni_pc_bh2**: For Qwen/Wan models

## Scheduler Reference

- **normal**: Standard (most models)
- **karras**: Better for low step counts
- **beta**: For Qwen/Flux diffusion models

## File Structure

```
comfyui-workflow-master/
  SKILL.md              - This file
  scripts/
    comfyui_api.py      - Python API client
  references/
    node-patterns.md    - Detailed node patterns
    ecommerce-guide.md  - E-commerce guide
    api-endpoints.md    - API reference
  templates/
    test_qwen_basic.json  - Sample workflow
```
