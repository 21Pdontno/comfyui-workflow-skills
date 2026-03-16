# Contributing to ComfyUI Workflow Master

Thank you for your interest in contributing! This project is fully open-source under the MIT License. Everyone is welcome to participate.

## Ways to Contribute

### 1. Workflow Templates 🎨

Share your ComfyUI workflow patterns by adding JSON files to `templates/`:

```
templates/
├── test_qwen_basic.json
├── flux_dev_txt2img.json        ← your contribution
├── sdxl_ipadapter_portrait.json  ← your contribution
└── ...
```

**Requirements:**
- Must pass validation (`comfyui_api.validate_workflow`)
- Include `_meta.title` annotations on every node
- Use descriptive node IDs (e.g., `"load_checkpoint"` not just `"1"`)
- Add a comment block at the top describing the workflow purpose

### 2. Node Patterns 📋

Add new workflow patterns to `references/node-patterns.md`:

- Provide the node connection diagram (ASCII art)
- Include the full JSON skeleton
- Explain key parameters and their effects
- Note VRAM requirements

### 3. Model Support 🔌

Add loading patterns for new models to `SKILL.md` under "Model System Compatibility":

```markdown
### NewModelName
- **Loader**: NewModelLoader
- **CLIP**: CLIPType(type="newmodel")
- **VAE**: NewModelVAE(vae_name="...")
- **Note**: Requires N GB VRAM minimum
```

### 4. Localization 🌍

Translate the annotation standard to other languages. The current default is Chinese, but you can:

- Add Korean annotations in `references/node-patterns.kr.md`
- Add Japanese annotations in `references/node-patterns.ja.md`
- Submit PRs with translated sections

### 5. Bug Reports 🐛

If you find issues:

1. Check if the issue is environment-specific (ComfyUI version, GPU, OS)
2. Include the full error message
3. Include the workflow JSON that caused the issue
4. Describe your ComfyUI setup (models installed, custom nodes)

### 6. Code Improvements 🔧

The API client (`scripts/comfyui_api.py`) is intentionally zero-dependency. Please keep it that way when making changes.

## Pull Request Process

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make changes** with clear commit messages
4. **Test** your changes (validate workflow templates still work)
5. **Submit PR** with a clear description of what changed and why

## Code Style

- Python: Follow PEP 8
- JSON: 2-space indentation, no trailing commas
- Markdown: 80-character line width where practical
- Comments: English for code, Chinese for node annotations (default)

## Questions?

Feel free to open a GitHub Issue for any questions about contributing. We're happy to help you get started!
