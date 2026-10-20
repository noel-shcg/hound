import { useState, useEffect, useRef } from 'react';
import { photosApi, Photo } from '../api/photos';

interface ScreensaverProps {
  className?: string;
  onWake: () => void;
  isActive: boolean;
}

export const Screensaver: React.FC<ScreensaverProps> = ({ className = '', onWake, isActive }) => {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [currentPhoto, setCurrentPhoto] = useState<Photo | null>(null);
  const [isDimmed, setIsDimmed] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const fetchPhotos = async () => {
      try {
        const data = await photosApi.list();
        setPhotos(data);
        if (data.length > 0) {
          setCurrentPhoto(data[Math.floor(Math.random() * data.length)]);
        }
      } catch (err) {
        console.error('Failed to load photos:', err);
      }
    };

    fetchPhotos();
  }, []);

  useEffect(() => {
    if (!isActive || photos.length === 0) return;

    // Rotate photos
    const rotatePhoto = () => {
      setCurrentPhoto(prev => {
        if (!prev || photos.length === 1) return prev;
        let nextIndex;
        do {
          nextIndex = Math.floor(Math.random() * photos.length);
        } while (photos[nextIndex].id === prev?.id && photos.length > 1);
        return photos[nextIndex];
      });
    };

    intervalRef.current = setInterval(rotatePhoto, 10000); // Rotate every 10 seconds

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isActive, photos]);

  useEffect(() => {
    if (!isActive) return;

    // Check if we should dim (between 22:00 and 07:00)
    const checkDimming = () => {
      const now = new Date();
      const hour = now.getHours();
      const shouldDim = hour >= 22 || hour < 7;
      setIsDimmed(shouldDim);
    };

    checkDimming();
    timeoutRef.current = setInterval(checkDimming, 60000); // Check every minute

    return () => {
      if (timeoutRef.current) clearInterval(timeoutRef.current);
    };
  }, [isActive]);

  const handleInteraction = () => {
    onWake();
  };

  if (!isActive || !currentPhoto) {
    return null;
  }

  return (
    <div
      className={`screensaver ${className} ${isDimmed ? 'dimmed' : ''}`}
      onClick={handleInteraction}
      onTouchStart={handleInteraction}
    >
      <img
        src={photosApi.getUrl(currentPhoto.filename)}
        alt={currentPhoto.original_filename}
        className="screensaver-image"
      />
      {isDimmed && <div className="screensaver-dim-overlay" />}
    </div>
  );
};
