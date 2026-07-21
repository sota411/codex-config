# Managed Wan2.2 Kijai environment

## Home RTX3080

- Host: `user@ubuntu-wsl.tail24e767.ts.net`
- ComfyUI: `/home/user/ComfyUI`, API `http://127.0.0.1:8180`
- GPU: RTX3080 10GB. Use WanVideoWrapper FP8 scaled models with 22-block swap,
  CPU/offload device, and SDPA. Do not enable torch compile, SageAttention, or TeaCache
  without a separately approved benchmark.
- WanVideoWrapper pin: `088128b224242e110d3906c6750e9a3a348a659b`

## Active Kijai configuration

- Runner: `/home/sota411/Documents/project/2024/sota411.github.io/.production/portfolio-lab/wan-four-beat/wan_four_beat.py`
- Active RTX3080 job: `jobs/coastal-stairway-rtx3080-keyframe-path.json`
- Remote templates: `/home/user/kijai-lightx2v-stage1.json` and
  `/home/user/kijai-lightx2v-stage2.json`
- Custom node: `/home/user/ComfyUI/custom_nodes/ComfyUI-WanVideoConditioningLimit`
- Kijai high LoRA: `Wan_2_2_I2V_A14B_HIGH_lightx2v_4step_lora_260412_rank_64_fp16.safetensors`
  - SHA-256: `8e0a86e765ade42a1deca52eb7411348254a019147be8c4eed88c7ad465d3399`
- Kijai low LoRA: `Wan_2_2_I2V_A14B_LOW_lightx2v_4step_lora_260412_rank_64_fp16.safetensors`
  - SHA-256: `09e10abd98460b66439bd77ea671e94c10fdc8251e0b986aa196d1904e3cc583`

The four other configs remain native schema-v3 configurations. Do not migrate them to
Kijai merely because Systems Delta uses the Kijai schema-v4 backend.

## Safe command shape

From `wan-four-beat`, use the config explicitly:

```sh
python wan_four_beat.py --config jobs/coastal-stairway-rtx3080-keyframe-path.json --profile preview dry-run
python wan_four_beat.py --config jobs/coastal-stairway-rtx3080-keyframe-path.json --profile preview run-beat --beat 1
```

Never run the second command while `/queue` reports someone else's job. Never call
ComfyUI `/free`; it is global to the server.

## Kaggle

`/home/sota411/Documents/project/2024/sota411.github.io/.production/portfolio-lab/kaggle/wan22-kijai-kernel/`
contains a pinned preflight only. It needs a private Kaggle input named
`wan22-i2v-models` with text encoder, two FP8 models, these two LoRAs, and VAE at
the exact paths documented in the artifact README. It does not submit video jobs.
