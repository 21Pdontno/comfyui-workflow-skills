# ComfyUI Workflow Master

> AI-native ComfyUI workflow automation skill for intelligent agents. Open-source, model-agnostic, and extensible.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-0.15%2B-green.svg)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

## What Is This?

**ComfyUI Workflow Master** is an open-source skill module designed for AI agent platforms (such as [OpenClaw](https://openclaw.ai), [Claude Code](https://docs.anthropic.com/en/docs/claude-code), or any agent framework that supports skill-based architectures). It enables an AI agent to **fully automate the ComfyUI workflow lifecycle**:

1. **Understand** natural language requirements → decompose into modular workflow architecture
2. **Query** the live ComfyUI instance for available nodes, models, and capabilities
3. **Design** workflows with proper node connections, data types, and parameter defaults
4. **Generate** complete ComfyUI workflow JSON with human-readable annotations on every node
5. **Validate** workflows against the ComfyUI API before execution
6. **Execute** workflows and monitor progress in real-time
7. **Auto-fix** errors intelligently — connection errors, parameter mismatches, missing models, VRAM overflows
8. **Advise** on model selection, hyperparameter tuning, and optimization strategies

### In Plain English

You tell your AI assistant: *"Build me an e-commerce product photography workflow that takes a product image and generates scene shots, model shots, and selling-point highlights — 5 variants each."*

The agent (powered by this skill) connects to your ComfyUI, checks what models you have, designs a multi-module workflow, validates it, fixes any issues, runs it, and delivers the images — all automatically.

## How It Works

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        User Request                              │
│  "Generate an e-commerce product workflow with 5 variants each"   │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Agent + This Skill                            │
│                                                                  │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────────┐    │
│  │ 1. Analyze  │──▶│ 2. Query     │──▶│ 3. Design Modules  │    │
│  │    Intent   │   │    ComfyUI    │   │    & Select Nodes  │    │
│  └─────────────┘   └──────────────┘   └────────────────────┘    │
│                                                     │            │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────┐ │      │
│  │ 6. Execute  │◀──│ 5. Validate  │◀──│ 4. Generate    │─┘      │
│  │    & Monitor│   │    & Fix     │   │    Workflow JSON│         │
│  └──────┬──────┘   └──────┬───────┘   └────────────────┘        │
│         │                 │                                       │
│         ▼                 ▼                                       │
│  ┌─────────────┐   ┌──────────────┐                             │
│  │ 7. Deliver  │   │ Error? Loop  │──── Fix & Re-validate ───▶ │
│  │  Results +  │   │  (max 5x)    │                             │
│  │  Advice     │   └──────────────┘                             │
│  └─────────────┘                                                 │
└──────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     ComfyUI Instance                             │
│              (localhost:8188 or custom endpoint)                  │
│                                                                  │
│  Models ─▶ Nodes ─▶ KSampler ─▶ VAEDecode ─▶ Output Images     │
└──────────────────────────────────────────────────────────────────┘
```

### The Debug Loop

Inspired by [ComfyUI-Copilot](https://github.com/AIDC-AI/ComfyUI-Copilot)'s multi-agent architecture, the skill implements a **coordinator + specialist** debugging pattern:

| Specialist | Handles | Example Fixes |
|---|---|---|
| **Connection Specialist** | Missing/broken node links, type mismatches | `"expected MODEL got CONDITIONING"` → fix link to correct output slot |
| **Parameter Specialist** | Invalid values, missing models, combo mismatches | `"value not in list"` → query valid options, replace with closest match |
| **Structure Specialist** | Incompatible nodes, circular dependencies | Remove broken node, restructure data flow |
| **Resource Specialist** | VRAM overflow, timeout | Reduce resolution, switch to fp8 model, decrease batch size |

The coordinator validates → classifies error → delegates to specialist → re-validates → loops until success or max 5 iterations.

## What's Inside

### File Structure

```
comfyui-workflow-master/
├── SKILL.md                         # Core instruction file (read by AI agent)
├── scripts/
│   └── comfyui_api.py               # Standalone Python client for ComfyUI REST API
├── references/
│   ├── node-patterns.md             # 20+ workflow patterns with copy-paste JSON examples
│   ├── ecommerce-guide.md           # E-commerce workflow design methodology
│   └── api-endpoints.md             # ComfyUI REST API quick reference
├── templates/
│   └── test_qwen_basic.json         # Pre-validated sample workflow
├── README.md                        # This file
├── README_CN.md                     # Chinese documentation
├── LICENSE                          # MIT License
├── CONTRIBUTING.md                  # Contribution guidelines
└── .gitignore
```

### SKILL.md — The Brain

This is the core file that AI agents read to understand how to use the skill. It contains:

- **Environment configuration** (ComfyUI endpoint, VRAM budget)
- **Workflow JSON format specification** (node IDs, link format, annotation standards)
- **6 pre-built workflow patterns** with full JSON examples:
  1. Standard Text-to-Image (SDXL/SD1.5)
  2. Qwen Image / Wan Text-to-Image
  3. Image-to-Image
  4. LoRA Enhancement
  5. Batch Generation (3-5 variants)
  6. E-Commerce Product Photography
- **Model ecosystem mapping** (SDXL, FLUX, Wan, Qwen, Hunyuan — how to load each)
- **Auto-fix error reference table** with diagnosis and fix strategies
- **Sampler & scheduler quick reference** for quality tuning
- **VRAM budget calculator** by configuration

### comfyui_api.py — The Hands

A zero-dependency Python client (uses only stdlib `urllib`) that provides:

```python
from comfyui_api import connect

c = connect()                          # Connect to ComfyUI
c.health_check()                       # Verify connectivity
c.get_system_stats()                   # GPU, RAM, version info
c.get_node_info()                      # All 1000+ node definitions
c.get_models("checkpoints")            # List available models
c.validate_workflow(workflow_json)     # Dry-run validation
c.execute_workflow(workflow_json)      # Run and wait for completion
c.download_all_outputs(result, dir)    # Save generated images
c.upload_image("my_photo.png")         # Upload to ComfyUI
c.clear_queue()                        # Cancel pending jobs
```

**Zero dependencies** — no `requests`, no `aiohttp`, no third-party packages. Just Python 3 stdlib.

## Supported Workflow Patterns

### Text-to-Image

The most fundamental pattern. Load a model, encode prompts, sample, decode, save.

```
CheckpointLoader → CLIPTextEncode(+) → KSampler → VAEDecode → SaveImage
                → CLIPTextEncode(-) ↗
        EmptyLatentImage ────────────────↗
```

### Image-to-Image

Uses an existing image as a starting point. The `denoise` parameter controls how much the output differs from the input (0.0 = identical, 1.0 = completely new).

### Batch Generation

Generates 3-5 variants by duplicating the sampler chain with different random seeds. Each variant explores a different point in the latent space.

### LoRA Enhancement

Applies a style or character LoRA to modify the base model's behavior. Strength parameter (0.5-1.0) controls influence intensity.

### E-Commerce Product Photography

A multi-module workflow designed for commercial product imagery:

| Module | Purpose | Key Technique |
|--------|---------|---------------|
| **Scene Generation** | Product in lifestyle context | IP-Adapter for consistency + scene prompts |
| **Model/Figure** | Product on human model | ControlNet OpenPose + IP-Adapter |
| **Selling Point** | Feature highlight close-ups | Crop-focused composition + detail prompts |
| **Product Info** | Clean studio shot | Neutral background + studio lighting |

### Qwen/Wan Image Generation

Leverages Alibaba's Qwen vision-language model for Chinese-friendly image generation:

```json
{
  "class_type": "WanTextToImageApi",
  "inputs": {
    "model": "wan2.5-t2i-preview",
    "prompt": "一张精美的产品展示图，温暖的自然光线，柔和的背景虚化",
    "width": 1024,
    "height": 1024
  }
}
```

## Node Annotation Standard

Every generated node includes a structured Chinese annotation in `_meta.title`:

```
[Module Name] Node Function - Specific Description | Tuning Advice
```

Example:
```json
"_meta": {
  "title": "[Scene Generation] KSampler - Core sampler controlling image generation | Higher steps = more detail but slower, lower CFG = more creative freedom"
}
```

This makes the workflow self-documenting — any user opening it in ComfyUI can understand what each node does and how to tune it.

## Requirements

- **ComfyUI** v0.15.0+ running and accessible via HTTP API
- **Python** 3.10+
- **PyTorch** 2.0+ with CUDA
- **NVIDIA GPU** with 8GB+ VRAM (12GB+ recommended)
- An **AI agent platform** that supports skill-based architectures

## Installation

### Option 1: Clone into Skills Directory

```bash
# For OpenClaw
git clone https://github.com/YOUR_USERNAME/comfyui-workflow-master.git ~/.openclaw/skills/comfyui-workflow-master

# For other platforms, copy to your agent's skills/plugins directory
```

### Option 2: Manual Install

1. Download the repository as a ZIP
2. Extract to your agent's skills directory
3. Rename the folder to `comfyui-workflow-master`

### Verify Installation

```bash
python scripts/comfyui_api.py
```

Expected output:
```
ComfyUI vX.X.X connected!
  checkpoints: N models
  diffusion_models: N models
  ...
```

## Quick Start

### Standalone API Client

```python
import sys
sys.path.insert(0, 'scripts')
from comfyui_api import connect, get_client

# Connect to ComfyUI
c = connect('http://localhost:8188')

# Check what you have
stats = c.get_system_stats()
print(f"ComfyUI {stats['system']['comfyui_version']}, "
      f"{stats['devices'][0]['vram_total'] / 1e9:.0f}GB VRAM")

# Run a workflow
with open('templates/test_qwen_basic.json') as f:
    import json
    workflow = json.load(f)

result = c.execute_workflow(workflow, timeout=300)
print(f"Status: {result['status']}")

if result['status'] == 'success':
    saved = c.download_all_outputs(result, './output/')
    print(f"Generated {len(saved)} images")
```

### As an Agent Skill

Once installed, simply describe what you need in natural language:

> "Create a text-to-image workflow using SDXL with a cyberpunk style LoRA. Generate 4 variants with different seeds. Save outputs with the prefix 'cyberpunk_'."

The agent will:
1. Check available models and find SDXL checkpoints
2. Locate the LoRA file
3. Build the workflow JSON with proper node connections
4. Add detailed annotations to every node
5. Validate the workflow
6. Execute and deliver the 4 images

## Customization

### Change ComfyUI Endpoint

Edit `scripts/comfyui_api.py` line 20:

```python
def __init__(self, base_url="http://YOUR_IP:YOUR_PORT", timeout=300):
```

Or pass it dynamically:

```python
c = connect("http://192.168.1.100:8188")
```

### Extend for New Models

Add new patterns to `SKILL.md` under "Key Node Patterns" and `references/node-patterns.md`. The skill is designed to be extensible — agents read these files to learn new patterns.

### Add Custom Workflows

Place workflow JSON files in `templates/` with descriptive names. The agent can discover and use them as starting points.

## Comparison with Alternatives

| Feature | This Skill | ComfyUI-Copilot | Manual ComfyUI |
|---|---|---|---|
| Natural language workflow generation | ✅ | ✅ | ❌ |
| Works outside ComfyUI | ✅ | ❌ (plugin) | N/A |
| Auto-fix errors | ✅ | ✅ | ❌ |
| Model-agnostic | ✅ | Partial | ✅ |
| Open source | ✅ MIT | ✅ MIT | N/A |
| No API key required | ✅ | ❌ | N/A |
| Agent-agnostic | ✅ | ComfyUI only | N/A |
| Batch generation | ✅ | ✅ | Manual |
| Chinese annotations | ✅ | ❌ | Manual |
| Zero dependencies | ✅ | ❌ | N/A |

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas where contributions are especially helpful:**

- 🌍 **Translations** — Add Korean, Japanese, or other language annotations
- 📋 **Workflow templates** — Share your workflow patterns in `templates/`
- 🔌 **New model support** — Add patterns for new models (Stable Diffusion 4, etc.)
- 🧪 **Testing** — Test on different GPU/VRAM configurations
- 📖 **Documentation** — Improve guides, add tutorials

## Tech Stack

- **Python 3** — stdlib only (`urllib`, `json`, `os`)
- **ComfyUI REST API** — `/api/prompt`, `/object_info`, `/system_stats`, `/view`
- **Markdown** — Skill instructions and reference docs

No frameworks. No databases. No build step. Just Python and Markdown.

## Acknowledgments

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) — The incredible node-based AI image generation platform
- [ComfyUI-Copilot](https://github.com/AIDC-AI/ComfyUI-Copilot) — Multi-agent debug architecture inspiration
- [Qwen](https://github.com/QwenLM/Qwen-Image) — Alibaba's vision-language image generation model
- All open-source ComfyUI custom node developers

## License

[MIT License](LICENSE) © 2026

Free to use, modify, and distribute. No restrictions on commercial use.
