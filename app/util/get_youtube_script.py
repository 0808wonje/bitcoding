from youtube_transcript_api import YouTubeTranscriptApi


def download_script():
    video_id = 'pAjEDOvz6n4' 
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
    with open(f'script_{video_id}.txt', 'w', encoding='utf-8') as script:
        for line in transcript:
            script.write(line['text'])
            script.write('\n')
    print("자막 데이터가 저장되었습니다.")
