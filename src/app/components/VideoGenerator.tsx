'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';

interface VideoFormData {
  script: string;
  voice: 'male' | 'female';
  max_duration: number;
}

export default function VideoGenerator() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const { register, handleSubmit, formState: { errors } } = useForm<VideoFormData>();

  const onSubmit = async (data: VideoFormData) => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/generate-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();
      if (result.success) {
        setVideoUrl(result.videoUrl);
      } else {
        console.error('Failed to generate video:', result.error);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Motivational Video Generator</h1>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Motivational Script
          </label>
          <textarea
            {...register('script', { required: true })}
            className="w-full p-2 border rounded-md min-h-[150px]"
            placeholder="Enter your motivational script here..."
          />
          {errors.script && (
            <p className="text-red-500 text-sm mt-1">Script is required</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Voice Type
          </label>
          <select
            {...register('voice', { required: true })}
            className="w-full p-2 border rounded-md"
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Maximum Duration (seconds)
          </label>
          <input
            type="number"
            {...register('max_duration', { required: true, min: 10, max: 60 })}
            className="w-full p-2 border rounded-md"
            defaultValue={60}
          />
          {errors.max_duration && (
            <p className="text-red-500 text-sm mt-1">
              Duration must be between 10 and 60 seconds
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={isGenerating}
          className={`w-full py-2 px-4 rounded-md text-white ${
            isGenerating ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {isGenerating ? 'Generating...' : 'Generate Video'}
        </button>
      </form>

      {videoUrl && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-2">Generated Video</h2>
          <video
            src={videoUrl}
            controls
            className="w-full rounded-lg"
          />
        </div>
      )}
    </div>
  );
} 