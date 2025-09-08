from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def summarize_text(text, sentences_count=5):
    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        raise ValueError("No text provided for summarization.")
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, sentences_count)
        result = " ".join(str(sentence) for sentence in summary)
        if not result:
            raise ValueError("Summarizer produced no output.")
        return result
    except Exception as e:
        print(f"DEBUG: Summarization error: {e}")
        raise
