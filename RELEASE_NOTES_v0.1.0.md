# Release v0.1.0

First public release of `comfyui-beeble-switchx`.

## Included

- `Beeble SwitchX Image`
- `Beeble SwitchX Video`
- reusable Beeble API helpers
- small test nodes for upload, generation, polling, download, and account checks
- example workflow in `test_workflows/`

## Supported modes

### Image

- `auto`
- `fill`
- `select`
- `custom`

### Video

- `auto`
- `fill`
- `select`
- `custom`

## Highlights

- local `.env` support for `BEEBLE_API_KEY`
- short runtime logging
- automatic polling until generation is ready
- retry logic for temporary network and SSL failures
- video outputs loaded from file paths instead of full in-memory `BytesIO`
- safe fallback when Beeble does not return `alpha_video`

## Notes

- dynamic UI is not implemented yet
- example workflows are included as references, not as full tutorials
- media validation mostly relies on Beeble API responses in this version
