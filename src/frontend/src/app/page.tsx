'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';

interface VideoFormData {
  script: string;
  vibe: string;
}

const VIBE_OPTIONS = [
  'luxury',
  'money',
  'grind',
  'success',
  'motivation',
  'fitness',
  'business',
  'lifestyle'
];

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

export default function Home() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const { register, handleSubmit, formState: { errors } } = useForm<VideoFormData>();

  const onSubmit = async (data: VideoFormData) => {
    setIsGenerating(true);
    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Failed to generate video');
      }

      // Create a blob URL from the video response
      const videoBlob = await response.blob();
      const videoUrl = URL.createObjectURL(videoBlob);
      setVideoUrl(videoUrl);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            ReelsBuilder.ai Clone
          </h1>
          <p className="text-gray-600">
            Create professional motivational videos in seconds
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Motivational Script
              </label>
              <textarea
                {...register('script', { required: true })}
                className="w-full p-3 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                rows={4}
                placeholder="Enter your motivational script (1-3 sentences)..."
              />
              {errors.script && (
                <p className="mt-1 text-sm text-red-600">Script is required</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Vibe
              </label>
              <select
                {...register('vibe', { required: true })}
                className="w-full p-3 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                {VIBE_OPTIONS.map((vibe) => (
                  <option key={vibe} value={vibe}>
                    {vibe.charAt(0).toUpperCase() + vibe.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              disabled={isGenerating}
              className={`w-full py-3 px-4 rounded-md text-white font-medium ${
                isGenerating
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {isGenerating ? 'Generating...' : 'Generate Video'}
            </button>
          </form>
        </div>

        {videoUrl && (
          <div className="mt-8 bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Your Generated Video
            </h2>
            <div className="aspect-[9/16] w-full max-w-md mx-auto bg-black rounded-lg overflow-hidden">
              <video
                src={videoUrl}
                controls
                className="w-full h-full object-cover"
              />
            </div>
            <div className="mt-4 flex justify-center">
              <a
                href={videoUrl}
                download="motivational_video.mp4"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700"
              >
                Download Video
              </a>
            </div>
          </div>
        )}
      </div>
    </main>
  );
} 