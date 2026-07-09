# comfyui-beeble-switchx

Custom nodes for Beeble SwitchX in ComfyUI.

## What is included

This package currently provides two production nodes:

- `Beeble SwitchX Image`
- `Beeble SwitchX Video`

and a set of small test nodes for checking each Beeble API step separately.

## Installation

Clone the repository into your ComfyUI custom nodes folder:

```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/albert999-pixel/comfyui-beeble-switchx.git
```

Expected path after cloning:

```text
ComfyUI/custom_nodes/comfyui-beeble-switchx
```

No extra Python dependencies are required beyond the ComfyUI environment you are already using right now.

After updating the files, restart ComfyUI manually.

## How to install

1. Clone this repository into `ComfyUI/custom_nodes/`.
2. Configure `BEEBLE_API_KEY`.
3. Restart ComfyUI.
4. Search for `Beeble` in the node list.

## Update

To update the node later:

```bash
cd /path/to/ComfyUI/custom_nodes/comfyui-beeble-switchx
git pull
```

## Quick start

```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/albert999-pixel/comfyui-beeble-switchx.git
```

After that:

1. Restart ComfyUI.
2. Add `Beeble SwitchX Image` or `Beeble SwitchX Video`.
3. Connect your source image or video.
4. Add prompt and other inputs.
5. Queue the workflow.

## API key setup

### Recommended for ComfyUI Desktop

Open ComfyUI Desktop:

```text
Instance -> Startup Args -> Environment Variables -> Add Variable
```

Add:

```env
BEEBLE_API_KEY=your_api_key_here
```

Then restart the ComfyUI instance.

### Alternative

Create a `.env` file in this custom node folder.

You can copy the example file:

```bash
cd /path/to/ComfyUI/custom_nodes/comfyui-beeble-switchx
cp .env.example .env
```

Then put your key into `.env`:

```env
BEEBLE_API_KEY=your_beeble_api_key_here
```

### Fallback

The code also accepts the regular environment variable:

```text
BEEBLE_API_KEY
```

Real API keys should never be stored in code, workflow JSON, or logs.

## Production nodes

### Beeble SwitchX Image

Inputs:

```text
image: IMAGE
reference_image: IMAGE optional
mask: MASK optional
alpha_mode: auto | fill | select | custom
prompt
seed
max_resolution
timeout_seconds
poll_interval_seconds
```

Outputs:

```text
image: IMAGE
alpha: MASK
```

Notes:

- `prompt` or `reference_image` must be provided
- `select` and `custom` require `mask`
- the node performs upload -> generation -> polling -> download automatically

### Beeble SwitchX Video

Inputs:

```text
video: VIDEO
reference_image: IMAGE optional
alpha_keyframe_mask: MASK optional
alpha_video: VIDEO optional
alpha_mode: auto | fill | select | custom
alpha_keyframe_index
prompt
seed
max_resolution
timeout_seconds
poll_interval_seconds
```

Outputs:

```text
video: VIDEO
alpha_video: VIDEO
```

Notes:

- `prompt` or `reference_image` must be provided
- `select` requires `alpha_keyframe_mask`
- `custom` requires `alpha_video`
- `alpha_keyframe_index` must be `>= 0`
- Beeble returns video alpha as a video result, so the second output is `alpha_video`
- if Beeble does not return alpha video, the node reuses the main render as `alpha_video` and logs a warning

## Test nodes

Available test nodes:

- `Beeble Account Info Test`
- `Beeble Upload Image Test`
- `Beeble Upload Video Test`
- `Beeble Export Mask Test`
- `Beeble Start Image Generation Test`
- `Beeble Start Video Generation Test`
- `Beeble Poll Job Test`
- `Beeble Wait Job Test`
- `Beeble Download Image Test`
- `Beeble Download Video Test`

These are useful when checking one API step at a time before debugging the full production flow.

## Typical flow

### Image

```text
LoadImage
-> Beeble SwitchX Image
-> PreviewImage / SaveImage
```

For `select` or `custom`, also connect a `MASK` input.

### Video

```text
LoadVideo
-> Beeble SwitchX Video
-> preview/save video node
```

For `select`, the recommended user flow is:

```text
LoadVideo
-> GetVideoComponents
-> ImageFromBatch
-> Mask editing node
-> Beeble SwitchX Video
-> SaveVideo
```

## Example workflows

Saved example workflows are in:

```text
test_workflows/
```

Current example:

- `12_switchx_image_video_demo.json` - combined demo workflow with both image and video branches

To load a saved workflow in ComfyUI:

1. Open ComfyUI.
2. Use the workflow open/import action in the UI.
3. Select a file from `test_workflows/`.
4. Replace local media inputs with your own files if needed.

## Logging

The nodes log short runtime statuses such as:

- preparing source media
- upload started/finished
- job started
- polling status/progress
- downloading render
- render ready

Production nodes keep logs short and readable. Test nodes may log more debug information.

## Current limitations

- no dynamic UI yet
- test workflows are examples, not full documentation
- media compatibility is mostly validated by Beeble API responses for now

## Troubleshooting

- If the nodes do not appear, restart ComfyUI and search for `Beeble`.
- If you see an API key error, check that `.env` exists and contains `BEEBLE_API_KEY=...`.
- If a temporary network or SSL error happens, the node retries automatically a few times before failing.
- If `select` or `custom` mode is used, make sure the required mask or alpha input is actually connected and not bypassed.

## Quick checks

If you want a fast local sanity check after edits:

```bash
python3 -m compileall beeble_switchx __init__.py
```
