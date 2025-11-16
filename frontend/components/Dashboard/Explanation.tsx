"use client";

interface ExplanationProps {
  text: string;
}

export default function Explanation({ text }: ExplanationProps) {
  return (
    <div className="w-full h-full bg-gray-800 rounded-xl p-6 shadow-lg overflow-y-auto">
      <h3 className="text-xl font-bold mb-4 text-white dm-sans-button">Explanation</h3>
      <p className="text-gray-300 leading-relaxed dm-sans-button font-normal">
        {text || "No explanation available."}
      </p>
    </div>
  );
}

