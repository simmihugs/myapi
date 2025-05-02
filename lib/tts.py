from TTS.api import TTS

tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=True)


def text_to_speech(text: str, output_path: str) -> str:
    try:
        tts.tts_to_file(
            text=f"<speak>{text}</speak>",
            speaker="p256",
            file_path=output_path,
            enable_ssml=True,
        )
        return output_path
    except Exception as e:
        print(f"Failed: {e}")
        return None
