import os
from dataclasses import dataclass
from typing import List, Optional, Protocol

# ====== 參數物件（易擴充）======
@dataclass
class GenerationParams:
    max_new_tokens: int = 60
    temperature: float = 0.8
    top_p: float = 0.9


# ====== Provider 名稱 ======
def _get_provider_name() -> str:
    # local | openai
    return os.getenv("CAPTION_PROVIDER", "local").lower()


# ====== Prompt 組裝（延用原本邏輯）======
def _build_prompt(video_id: str, segments: List[dict], lang: str = "zh") -> str:
    secs = " / ".join([f"{int(s['start'])}-{int(s['end'])}s" for s in segments[:4]]) or "0-34s"
    if lang == "zh":
        return (f"你是短影音文案助理，請用旅遊短片語氣寫一句 25~40 字的 caption，"
                f"語調自然，避免浮誇，結尾附 2~3 個 hashtag。重點片段：{secs}")
    return (f"You are a short-video caption assistant. Write a natural 15–25 word travel-style "
            f"caption with 2–3 hashtags at the end. Key moments: {secs}.")


# ====== Provider 介面 ======
class CaptionProvider(Protocol):
    def generate(self, prompt: str, params: GenerationParams) -> str: ...


# ====== OpenAI Provider ======
_openai_client = None

class OpenAIProvider:
    def generate(self, prompt: str, params: GenerationParams) -> str:
        global _openai_client
        from openai import OpenAI
        if _openai_client is None:
            base_url = os.getenv("OPENAI_BASE_URL") or None
            _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=base_url)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        resp = _openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes concise social captions."},
                {"role": "user", "content": prompt},
            ],
            temperature=params.temperature,
            top_p=params.top_p,
            max_tokens=params.max_new_tokens,
        )
        return resp.choices[0].message.content.strip()


# ====== Hugging Face（local）Provider ======
_hf_pipe = None

def _get_quant():
    q = (os.getenv("CAPTION_QUANT") or "").lower()
    return q if q in ("int8", "int4") else None


def _load_local_pipeline():
    global _hf_pipe
    if _hf_pipe is not None:
        return _hf_pipe
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    model_id = os.getenv("CAPTION_BASE_MODEL", "sshleifer/tiny-gpt2")
    quant = _get_quant()
    tok = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    kwargs = {}
    if quant == "int8":
        kwargs.update(dict(load_in_8bit=True, device_map="auto"))
    elif quant == "int4":
        kwargs.update(dict(load_in_4bit=True, device_map="auto"))
    model = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)
    _hf_pipe = pipeline("text-generation", model=model, tokenizer=tok)
    return _hf_pipe


class LocalHFProvider:
    def generate(self, prompt: str, params: GenerationParams) -> str:
        pipe = _load_local_pipeline()
        out = pipe(
            prompt,
            do_sample=True,
            temperature=params.temperature,
            top_p=params.top_p,
            max_new_tokens=params.max_new_tokens,
            num_return_sequences=1,
        )[0]["generated_text"]
        return out[len(prompt):].strip() if out.startswith(prompt) else out.strip()


# ====== Provider 工廠 ======
def _get_provider_impl(name: Optional[str] = None) -> CaptionProvider:
    name = (name or _get_provider_name()).lower()
    if name == "openai":
        return OpenAIProvider()
    return LocalHFProvider()  # 預設 local


# ====== 對外統一入口（向前相容 + 可擴充）======
def generate_caption_text(
    video_id: str,
    segments: List[dict],
    lang: str = "zh",
    *,
    params: Optional[GenerationParams] = None,
    provider_name: Optional[str] = None,
) -> str:
    prompt = _build_prompt(video_id, segments, lang)
    impl = _get_provider_impl(provider_name)
    return impl.generate(prompt, params or GenerationParams())
