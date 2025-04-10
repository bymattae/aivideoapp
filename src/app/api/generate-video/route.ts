import { NextResponse } from 'next/server';
import { createFFmpeg, fetchFile } from '@ffmpeg/ffmpeg';
import { PexelsAPI } from 'pexels-api';

// Initialize Pexels API
const pexels = new PexelsAPI(process.env.PEXELS_API_KEY);

export async function POST(request: Request) {
  try {
    const { script, voice, max_duration } = await request.json();

    // Initialize FFmpeg
    const ffmpeg = createFFmpeg({ log: true });
    await ffmpeg.load();

    // Step 1: Generate voiceover using Web Speech API
    const utterance = new SpeechSynthesisUtterance(script);
    utterance.voice = voice === 'male' ? 
      speechSynthesis.getVoices().find(v => v.name.includes('Male')) :
      speechSynthesis.getVoices().find(v => v.name.includes('Female'));
    
    const audioBlob = await new Promise<Blob>((resolve) => {
      const audioContext = new AudioContext();
      const mediaRecorder = new MediaRecorder(new MediaStream());
      const chunks: BlobPart[] = [];
      
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorder.onstop = () => resolve(new Blob(chunks, { type: 'audio/wav' }));
      
      mediaRecorder.start();
      speechSynthesis.speak(utterance);
      setTimeout(() => mediaRecorder.stop(), max_duration * 1000);
    });

    // Step 2: Fetch relevant video clips from Pexels
    const keywords = ['luxury car', 'dubai skyline', 'private jet', 'watch macro', 'city at night'];
    const videoClips: Blob[] = [];
    
    for (const keyword of keywords) {
      const response = await pexels.searchVideos(keyword, { per_page: 1 });
      if (response.videos && response.videos.length > 0) {
        const videoResponse = await fetch(response.videos[0].video_files[0].link);
        videoClips.push(await videoResponse.blob());
      }
    }

    // Step 3: Process videos with FFmpeg
    const inputFiles = videoClips.map((clip, i) => `input${i}.mp4`);
    await Promise.all(videoClips.map((clip, i) => 
      ffmpeg.FS('writeFile', inputFiles[i], await fetchFile(clip))
    ));

    // Concatenate videos
    await ffmpeg.run(
      '-i', inputFiles[0],
      '-i', inputFiles[1],
      '-i', inputFiles[2],
      '-i', inputFiles[3],
      '-i', inputFiles[4],
      '-filter_complex', '[0:v][1:v][2:v][3:v][4:v]concat=n=5:v=1:a=0[outv]',
      '-map', '[outv]',
      'output.mp4'
    );

    // Add audio
    await ffmpeg.FS('writeFile', 'audio.wav', await fetchFile(audioBlob));
    await ffmpeg.run(
      '-i', 'output.mp4',
      '-i', 'audio.wav',
      '-c:v', 'copy',
      '-c:a', 'aac',
      '-shortest',
      'final.mp4'
    );

    // Resize to 9:16
    await ffmpeg.run(
      '-i', 'final.mp4',
      '-vf', 'scale=608:1080:force_original_aspect_ratio=decrease,pad=608:1080:(ow-iw)/2:(oh-ih)/2',
      'final_vertical.mp4'
    );

    // Read the final video
    const data = ffmpeg.FS('readFile', 'final_vertical.mp4');
    const videoBlob = new Blob([data.buffer], { type: 'video/mp4' });

    // Clean up
    ffmpeg.FS('unlink', 'output.mp4');
    ffmpeg.FS('unlink', 'final.mp4');
    ffmpeg.FS('unlink', 'final_vertical.mp4');
    ffmpeg.FS('unlink', 'audio.wav');
    inputFiles.forEach(file => ffmpeg.FS('unlink', file));

    // Return the video as a blob URL
    return new NextResponse(videoBlob, {
      headers: {
        'Content-Type': 'video/mp4',
        'Content-Disposition': 'attachment; filename="motivational-video.mp4"'
      }
    });

  } catch (error) {
    console.error('Error generating video:', error);
    return NextResponse.json({ 
      success: false,
      error: 'Failed to generate video'
    }, { status: 500 });
  }
} 