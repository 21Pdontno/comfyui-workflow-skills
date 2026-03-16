# E-Commerce Workflow Design Guide

## Typical E-Commerce Image Requirements

1. **Product Scene Image** - Product placed in lifestyle/usage context
2. **Model/Figure Image** - Product shown on model/person
3. **Selling Point Image** - Feature highlight close-ups
4. **Product Info Image** - Clean product shot (often with text overlay)
5. **Banner/Hero Image** - Marketing hero for landing pages

## Designing for E-Commerce

### Module 1: Product Analysis (AI Text Analysis)

Before generation, analyze the product:
- Extract visual features (color, shape, material, style)
- Identify target audience
- Determine suitable scene contexts
- Generate scene/style keywords

**ComfyUI approach**: Use ChatGLM/OpenAI node for text analysis, or manually craft detailed prompts.

### Module 2: Scene Generation

**Approach**: Use IP-Adapter to maintain product consistency + ControlNet for composition.

**Key parameters**:
- IP-Adapter weight: 0.5-0.7 (too high = too similar, too low = lost product identity)
- ControlNet strength: 0.4-0.6 (subtle guidance)
- Prompt: Describe desired scene + product placement
- Steps: 25-35 for quality, 15-20 for speed
- CFG: 6-8 for balance

### Module 3: Model/Figure

**Approach**: 
- Use ControlNet OpenPose to guide figure placement
- Use IP-Adapter FaceID if face consistency needed
- Product should be composited or generated inline

### Module 4: Selling Point Showcase

**Approach**:
- Start with product image
- Use inpainting to place in different contexts
- Use image crop + zoom for detail shots
- Generate multiple angles/perspectives

### Module 5: Batch Output

For each module, generate 3-5 variants:
- Different seeds
- Slightly varied prompts (word order, emphasis)
- Different compositions (close-up, medium, wide)
- Different lighting (warm, cool, studio, natural)

## Prompt Templates

### Product Scene
```
A [product] placed in [scene description], [lighting], [mood], professional product photography, 
high quality, detailed, 8k resolution, commercial photography style
```

### Model Shot
```
A [model description] wearing/holding [product] in [setting], [pose], [lighting], 
professional fashion photography, editorial style, high quality
```

### Selling Point Highlight
```
Close-up of [product feature], [material/texture description], [lighting], 
product detail photography, macro shot, professional studio lighting, 8k
```

### Product Info (Clean)
```
[Product] on [background color/texture] background, centered composition, 
studio lighting, clean professional product shot, no shadows, white/light gray background
```

## Resolution Recommendations

| Use Case | Recommended | Notes |
|----------|-------------|-------|
| Product detail | 1024x1024 | Square for detail |
| Banner/Hero | 1920x1080 or 1344x768 | Landscape for web |
| Social media | 1080x1350 (4:5) | Instagram-friendly |
| Model shot | 768x1152 or 832x1216 | Portrait orientation |
| Scene | 1344x768 | Landscape context |
