from gtts import gTTS
from googletrans import Translator

def text_to_speech_hindi(text, output_path=None):
    """
    Translate the given English text to Hindi and generate a speech audio file.
    If output_path is provided, saves the MP3 audio to that path. Otherwise, returns audio bytes.
    """
    translator = Translator()
    try:
        # Translate text to Hindi
        translation = translator.translate(text, dest='hi')
        hindi_text = translation.text
    except Exception as e:
        print(f"Translation to Hindi failed: {e}")
        hindi_text = text  # Fallback to original text if translation fails
    try:
        # Generate speech using gTTS
        tts = gTTS(hindi_text, lang='hi')
        if output_path:
            tts.save(output_path)
            return output_path
        else:
            # Return audio data in memory
            from io import BytesIO
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
    except Exception as e:
        print(f"TTS generation failed: {e}")
        return None
