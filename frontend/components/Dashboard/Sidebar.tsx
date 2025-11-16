"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

interface Subtopic {
  id: string;
  title: string;
  page_reference?: number;
}

interface Topic {
  id: string;
  title: string;
  subtopics: Subtopic[];
}

interface SidebarProps {
  mainTopic: string;
  topics: Topic[];
  onSubtopicClick?: (subtopicId: string, pageReference?: number) => void;
  selectedSubtopicId?: string | null;
}

export default function Sidebar({ mainTopic, topics, onSubtopicClick, selectedSubtopicId }: SidebarProps) {
  const router = useRouter();
  const [openDropdowns, setOpenDropdowns] = useState<Set<string>>(new Set());

  const toggleDropdown = (topicId: string) => {
    setOpenDropdowns((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(topicId)) {
        newSet.delete(topicId);
      } else {
        newSet.add(topicId);
      }
      return newSet;
    });
  };

  const handleSubtopicSelect = (subtopicId: string, pageReference: number | undefined, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent dropdown toggle when clicking subtopic
    if (onSubtopicClick) {
      onSubtopicClick(subtopicId, pageReference);
    }
  };

  const handleLogoClick = () => {
    router.push("/");
  };

  return (
    <div className="h-screen bg-[#034748] w-64 flex flex-col fixed left-0 top-0 border-r border-gray-200">
      {/* Logo - centered horizontally, near top - fixed position */}
      <div className="flex-shrink-0 flex justify-center py-6">
        <button
          onClick={handleLogoClick}
          className="bg-white rounded-lg p-3 shadow-lg hover:shadow-xl transition-shadow cursor-pointer"
          aria-label="Go to home page"
        >
          <Image
            src="/images/logo/logo.png"
            alt="Sensei Logo"
            width={180}
            height={54}
            priority
          />
        </button>
      </div>

      {/* Scrollable Topics Container */}
      <div className="flex-1 overflow-y-auto px-6 pb-6">
        {/* Main Topic */}
        <div className="mb-4">
          <h2 className="text-xl font-bold text-white dm-sans-button">
            {mainTopic}
          </h2>
        </div>

        {/* Topics with Subtopics Dropdown */}
        <div className="space-y-2">
          {topics.map((topic) => (
            <div key={topic.id} className="w-full">
              {/* Topic Header (Dropdown Toggle) */}
              <button
                onClick={() => toggleDropdown(topic.id)}
                className="w-full text-left px-4 py-2 rounded-lg hover:bg-[#045a5c] transition-colors dm-sans-button text-base font-medium text-white"
              >
                <div className="flex items-center justify-between">
                  <span>{topic.title}</span>
                  <span className={`transform transition-transform ${openDropdowns.has(topic.id) ? 'rotate-180' : ''}`}>
                    ▼
                  </span>
                </div>
              </button>
              
              {/* Subtopics (Nested) */}
              {openDropdowns.has(topic.id) && (
                <div className="mt-2 ml-4 space-y-1">
                  {topic.subtopics.map((subtopic) => (
                    <button
                      key={subtopic.id}
                      onClick={(e) => handleSubtopicSelect(subtopic.id, subtopic.page_reference, e)}
                      className={`w-full text-left px-4 py-2 rounded-lg transition-colors dm-sans-button text-sm font-medium text-white/90 ${
                        selectedSubtopicId === subtopic.id
                          ? "bg-[#045a5c] text-white"
                          : "hover:bg-[#045a5c]/50"
                      }`}
                    >
                      {subtopic.title}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

