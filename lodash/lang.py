import langdetect
import iso639


def language_detect(text: str | list[str]) -> str:
    text = ' '.join(text) if isinstance(text, list) else text
    try:
        lang_code = langdetect.detect(str(text))
        return iso639.Language.from_part1(lang_code).name
    except langdetect.LangDetectException:
        # Use English as a fallback language
        return 'English'
