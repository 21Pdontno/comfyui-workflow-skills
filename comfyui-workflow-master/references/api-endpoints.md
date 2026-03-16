# ComfyUI REST API Endpoints Reference

## Base URL
http://127.0.0.1:8188

## System
- GET /system_stats - System info (OS, RAM, VRAM, versions)
- GET /object_info - All node types with input/output specs (~1.8MB)

## Models
- GET /models/{folder} - List models. Folders: checkpoints, diffusion_models, loras, vae, text_encoders, controlnet, clip_vision, style_models, upscale_models

## Queue
- POST /api/prompt - Submit workflow. Body: {prompt: {workflow}, check: bool}
- GET /queue - Running and pending items
- POST /interrupt - Stop current execution

## History
- GET /history - All execution history
- GET /history/{prompt_id} - Specific prompt details

## Files
- POST /upload/image - Upload image (multipart: image, subfolder, type)
- GET /view - Download image (params: filename, subfolder, type)

## Workflow Format
Keys = node IDs, class_type = node type, inputs = values or links [node_id, slot]
