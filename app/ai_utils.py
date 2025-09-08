from transformers import pipeline

# Use a small summarization model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_text(text):
    # DistilBART has a max token limit; chunk if needed
    if len(text) > 1000:
        text = text[:1000]
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']