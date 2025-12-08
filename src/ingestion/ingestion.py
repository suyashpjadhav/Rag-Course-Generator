import os
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from pytube import YouTube
import whisper
from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader
from langchain_core.documents import Document


# YouTube Ingestion
def extract_video_id(url: str) -> str | None:
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path.startswith('/embed/'):
            return query.path.split('/')[2]
    return None

def load_youtube(video_url: str) -> Document | None:
    try:
        video_id = extract_video_id(video_url)

        # 1) Try official transcript
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en'])
            items = transcript.fetch()
            text = " ".join([item["text"] for item in items])
            print(f"Transcript fetched via API ({len(text)} chars)")
            return Document(page_content=text, metadata={"source": video_url})

        except Exception as e:
            print(f"No captions available via API ({e}). Falling back to Whisper.")

            # 2) Download audio
            try:
                yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
                os.makedirs("downloads", exist_ok=True)
                audio_path = os.path.join("downloads", f"{yt.video_id}.mp4")
                if not os.path.exists(audio_path):
                    stream = yt.streams.get_audio_only()
                    stream.download(filename=audio_path)
            except Exception as e:
                print("Audio download failed:", e)
                return None

            # 3) Transcribe with Whisper
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            text = result.get("text", "")
            print(f"Transcript fetched via Whisper ({len(text)} chars)")
            return Document(page_content=text, metadata={"source": video_url})

    except Exception as e:
        print("YouTube ingestion completely failed:", e)
        return None


# PDF Ingestion
def load_pdf(pdf_path: str) -> list[Document]:
    """Load a PDF file and return it as LangChain Documents."""
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        print(f"PDF ingestion successful — {len(docs)} pages loaded")
        return docs
    except Exception as e:
        print("PDF ingestion failed:", e)
        return []
    

# Audio Ingestion
def load_audio(audio_path: str) -> Document | None:
    """Transcribe a local audio file (MP3/MP4) using Whisper."""
    try:
        if not os.path.exists(audio_path):
            print("Audio file not found.")
            return None

        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        text = result.get("text", "")
        print(f"Audio transcription successful — {len(text)} characters")
        return Document(page_content=text, metadata={"source": audio_path})

    except Exception as e:
        print("Audio ingestion failed:", e)
        return None    


# PPT Ingestion
def load_pptx(ppt_path: str) -> list[Document]:
    """Load a PPT file and return it as LangChain Documents."""
    try:
        loader = UnstructuredFileLoader(ppt_path)
        docs = loader.load()
        print(f"PowerPoint ingestion successful — {len(docs)} slides/chunks loaded")
        return docs
    except Exception as e:
        print("PowerPoint ingestion failed:", e)
        return []
    

# Manual Ingestion
def load_manual_transcript(transcript_text: str, source: str = "manual_input") -> Document | None:
    """Load a manually pasted transcript."""
    if not transcript_text.strip():
        print("Empty transcript text provided.")
        return None
    print(f"Manual transcript loaded ({len(transcript_text)} characters)")
    return Document(page_content=transcript_text.strip(), metadata={"source": source})


