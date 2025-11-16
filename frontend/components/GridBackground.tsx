"use client";

import { useEffect, useRef, useState } from "react";

interface GridSquare {
  x: number;
  y: number;
  opacity: number;
}

interface GridBackgroundProps {
  squareSize?: number;
  spacing?: number;
  cursorRadius?: number;
}

export default function GridBackground({
  squareSize = 20,
  spacing = 4,
  cursorRadius = 300,
}: GridBackgroundProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [squares, setSquares] = useState<GridSquare[]>([]);
  const [cursorPos, setCursorPos] = useState({ x: 0, y: 0 });
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    // Calculate grid dimensions
    const calculateGrid = () => {
      if (!containerRef.current) return;

      const container = containerRef.current;
      const width = window.innerWidth;
      const height = window.innerHeight;

      const cols = Math.ceil(width / (squareSize + spacing));
      const rows = Math.ceil(height / (squareSize + spacing));

      const newSquares: GridSquare[] = [];
      for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
          newSquares.push({
            x: col * (squareSize + spacing) + spacing / 2,
            y: row * (squareSize + spacing) + spacing / 2,
            opacity: 0,
          });
        }
      }
      setSquares(newSquares);
    };

    calculateGrid();
    window.addEventListener("resize", calculateGrid);

    return () => {
      window.removeEventListener("resize", calculateGrid);
    };
  }, [squareSize, spacing]);

  useEffect(() => {
    const updateOpacities = () => {
      setSquares((prevSquares) =>
        prevSquares.map((square) => {
          const dx = square.x - cursorPos.x;
          const dy = square.y - cursorPos.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance > cursorRadius) {
            return { ...square, opacity: 0 };
          }

          // Calculate opacity based on distance
          // At distance = cursorRadius: opacity = 0
          // At distance = cursorRadius/2: opacity = 0.5
          // At distance = 0: opacity = 1
          // Linear interpolation: opacity = 1 - (distance / cursorRadius) * 2
          // But we need: at cursorRadius/2, opacity = 0.5
          // So: 0.5 = 1 - (0.5) * k => k = 1
          // Actually: opacity = 1 - (distance / cursorRadius)
          // At cursorRadius/2: opacity = 1 - 0.5 = 0.5 ✓
          // At cursorRadius: opacity = 1 - 1 = 0 ✓
          // At 0: opacity = 1 - 0 = 1 ✓
          const normalizedDistance = distance / cursorRadius;
          const opacity = Math.max(0, Math.min(1, 1 - normalizedDistance));

          return { ...square, opacity };
        })
      );

      animationFrameRef.current = requestAnimationFrame(updateOpacities);
    };

    updateOpacities();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [cursorPos, cursorRadius]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setCursorPos({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener("mousemove", handleMouseMove);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ 
        backgroundColor: "#000000",
        minHeight: "100vh",
        height: "100%"
      }}
    >
      {squares.map((square, index) => (
        <div
          key={index}
          className="absolute bg-white"
          style={{
            left: `${square.x}px`,
            top: `${square.y}px`,
            width: `${squareSize}px`,
            height: `${squareSize}px`,
            opacity: square.opacity,
            transition: "opacity 0.1s ease-out",
          }}
        />
      ))}
    </div>
  );
}

