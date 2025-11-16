"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";

interface InteractiveSliderProps {
  image1: string;
  image2: string;
  alt1?: string;
  alt2?: string;
}

export default function InteractiveSlider({
  image1,
  image2,
  alt1 = "Before",
  alt2 = "After",
}: InteractiveSliderProps) {
  // Start at center (50%) showing half of both images
  const [targetPosition, setTargetPosition] = useState(50);
  const [sliderPosition, setSliderPosition] = useState(50);
  const containerRef = useRef<HTMLDivElement>(null);
  const animationFrameRef = useRef<number>();

  // Smooth easing animation
  useEffect(() => {
    const animate = () => {
      setSliderPosition((prev) => {
        const diff = targetPosition - prev;
        // Easing function for smooth transition (ease-out curve)
        const easing = 0.15;
        const newPosition = prev + diff * easing;
        
        // Stop animation when close enough
        if (Math.abs(diff) < 0.1) {
          return targetPosition;
        }
        
        return newPosition;
      });
      
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [targetPosition]);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = (x / rect.width) * 100;
    const clampedPercentage = Math.max(0, Math.min(100, percentage));
    setTargetPosition(clampedPercentage);
  };

  const handleMouseLeave = () => {
    setTargetPosition(50); // Return to center
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full h-[400px] overflow-hidden cursor-col-resize rounded-lg"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {/* Image 2 (background, shows on right side when cursor is left of center) */}
      <div className="absolute inset-0 rounded-lg overflow-hidden">
        {image2.startsWith('data:') ? (
          <img
            src={image2}
            alt={alt2}
            className="w-full h-full object-cover"
          />
        ) : (
          <Image
            src={image2}
            alt={alt2}
            fill
            className="object-cover"
            priority
          />
        )}
      </div>

      {/* Image 1 (foreground, shows on left side, initially 100%) */}
      <div
        className="absolute inset-0 overflow-hidden rounded-l-lg"
        style={{ width: `${sliderPosition}%` }}
      >
        {image1.startsWith('data:') ? (
          <img
            src={image1}
            alt={alt1}
            className="w-full h-full object-cover"
          />
        ) : (
          <Image
            src={image1}
            alt={alt1}
            fill
            className="object-cover"
            priority
          />
        )}
      </div>

      {/* White divider bar */}
      <div
        className="absolute top-0 bottom-0 w-1 bg-white z-10 shadow-lg"
        style={{ left: `${sliderPosition}%`, transform: "translateX(-50%)" }}
      >
        {/* Handle circle */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full border-2 border-gray-300 shadow-lg flex items-center justify-center">
          <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
        </div>
      </div>
    </div>
  );
}

