# API reference — verified 2026-10-21

## Images

POST https://apihub.agnes-ai.com/v1/images/generations

Latest-first models: agnes-image-2.5-flash, agnes-image-2.1-flash, agnes-image-2.0-flash.
All three are currently free at supported resolutions, including reference inputs.
The 2.5 model supports both generation and editing and is compatible with 2.1.
Use model, prompt, size; URL output via extra_body.response_format="url".
Editing inputs: extra_body.image array. Only the 2.0 fallback retains legacy tags=["img2img"].
The CLI retains exact pixel size strings (default 1024x1024); newer models also accept 1K/2K/3K/4K.
Exact unsupported sizes may be normalized. seed is retained for compatibility and reproducibility is not guaranteed.
Response URL: data[0].url.

## Videos

POST https://apihub.agnes-ai.com/v1/videos
Model: agnes-video-2.5-flash; currently limited-time free. No confirmed-free legacy fallback.
Request: prompt, model, seconds as string "4"–"12", size="720P", aspect_ratio.
Text: mode="text". Image: mode="keyframe", first_frame=public image URL.
Do not send legacy num_frames/frame_rate/height/width.
Save video_id from creation response, distinct from id/task_id.
GET https://apihub.agnes-ai.com/agnesapi?video_id=VIDEO_ID&model_name=agnes-video-2.5-flash
Poll status/progress every 2 seconds; completed URL is top-level url.
Do not treat remixed_from_video_id as the download URL.
Flash supports only 720P; advanced reference mode supports at most five images, three audio clips and no reference videos. This CLI exposes text and single-first-frame creation.
Ratios: 21:9,16:9,4:3,1:1,3:4,9:16.

## Sources

- https://www.agnes-ai.com/zh-Hans/docs/pricing
- https://www.agnes-ai.com/zh-Hans/docs/agnes-image-25-flash
- https://www.agnes-ai.com/zh-Hans/docs/agnes-video-25-flash
- https://github.com/AgnesAI-Labs/AgnesAI-Models/blob/main/MODEL_CATALOG.md

Official current pricing and model docs take precedence over the older GitHub catalog.
Pricing and account access may change; free does not mean unlimited or permanent.
