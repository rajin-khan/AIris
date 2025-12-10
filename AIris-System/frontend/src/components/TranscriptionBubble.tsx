import { useEffect, useState, useRef } from "react";
import { Loader2, User, Bot } from "lucide-react";

interface TranscriptionBubbleProps {
  voiceOnlyMode: boolean;
  transcription: { type: 'user' | 'system' | 'refresh', text: string } | null;
}

interface BubbleState {
  text: string;
  isVisible: boolean;
  isAnimating: boolean;
  minDisplayTime: number;
  hideTimer: ReturnType<typeof setTimeout> | null;
  isRefresh?: boolean;
}

export default function TranscriptionBubble({
  voiceOnlyMode,
  transcription,
}: TranscriptionBubbleProps) {
  const [systemBubble, setSystemBubble] = useState<BubbleState>({
    text: "",
    isVisible: false,
    isAnimating: false,
    minDisplayTime: 0,
    hideTimer: null,
  });
  const [userBubble, setUserBubble] = useState<BubbleState>({
    text: "",
    isVisible: false,
    isAnimating: false,
    minDisplayTime: 0,
    hideTimer: null,
  });
  const [refreshBubble, setRefreshBubble] = useState<BubbleState>({
    text: "",
    isVisible: false,
    isAnimating: false,
    minDisplayTime: 0,
    hideTimer: null,
  });

  const updateBubble = (
    type: 'user' | 'system' | 'refresh',
    text: string,
    setBubble: React.Dispatch<React.SetStateAction<BubbleState>>
  ) => {
    const now = Date.now();
    const minDisplayTime = now + 2000; // 2 seconds minimum
    const isRefresh = type === 'refresh';

    // Clear any existing hide timer
    setBubble((prev) => {
      if (prev.hideTimer) {
        clearTimeout(prev.hideTimer);
      }
      return {
        text,
        isVisible: true,
        isAnimating: true,
        minDisplayTime,
        hideTimer: null,
        isRefresh,
      };
    });

    // Stop animating after entry animation
    setTimeout(() => {
      setBubble((prev) => ({ ...prev, isAnimating: false }));
    }, 400);

    // Set up auto-hide timer
    const baseTimeout = type === 'refresh' ? 3000 : 5000;
    const hideTimer = setTimeout(() => {
      const checkMinTime = () => {
        setBubble((prev) => {
          const timeSinceMinDisplay = Date.now() - prev.minDisplayTime;
          if (timeSinceMinDisplay >= 0) {
            // Minimum time has passed, safe to hide
            // Clear text after fade out animation
            setTimeout(() => {
              setBubble((prevState) => ({
                ...prevState,
                text: "",
                isAnimating: false,
              }));
            }, 300);
            return {
              ...prev,
              isVisible: false,
              hideTimer: null,
            };
          } else {
            // Still need to wait, check again in 100ms
            setTimeout(checkMinTime, 100);
            return prev;
          }
        });
      };
      checkMinTime();
    }, baseTimeout);

    setBubble((prev) => ({ ...prev, hideTimer }));
  };

  useEffect(() => {
    if (!voiceOnlyMode) {
      setSystemBubble((prev) => {
        if (prev.hideTimer) clearTimeout(prev.hideTimer);
        return { text: "", isVisible: false, isAnimating: false, minDisplayTime: 0, hideTimer: null };
      });
      setUserBubble((prev) => {
        if (prev.hideTimer) clearTimeout(prev.hideTimer);
        return { text: "", isVisible: false, isAnimating: false, minDisplayTime: 0, hideTimer: null };
      });
      setRefreshBubble((prev) => {
        if (prev.hideTimer) clearTimeout(prev.hideTimer);
        return { text: "", isVisible: false, isAnimating: false, minDisplayTime: 0, hideTimer: null };
      });
      return;
    }

    if (transcription) {
      if (transcription.type === 'user') {
        updateBubble('user', transcription.text, setUserBubble);
      } else if (transcription.type === 'system') {
        updateBubble('system', transcription.text, setSystemBubble);
      } else if (transcription.type === 'refresh') {
        // Refresh gets its own separate green bubble
        updateBubble('refresh', transcription.text, setRefreshBubble);
      }
    }
  }, [transcription, voiceOnlyMode]);

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      setSystemBubble((prev) => {
        if (prev.hideTimer) clearTimeout(prev.hideTimer);
        return prev;
      });
      setUserBubble((prev) => {
        if (prev.hideTimer) clearTimeout(prev.hideTimer);
        return prev;
      });
      setRefreshBubble((prev) => {
        if (prev.hideTimer) clearTimeout(prev.hideTimer);
        return prev;
      });
    };
  }, []);

  if (!voiceOnlyMode) {
    return null;
  }

  // Render a single bubble
  const renderBubble = (
    state: BubbleState,
    type: 'user' | 'system',
    side: 'left' | 'right'
  ) => {
    const config =
      type === 'user'
        ? {
            container: "bg-brand-gold/20 border-brand-gold text-brand-gold",
            icon: User,
            label: "You",
            iconClass: "text-brand-gold",
            labelClass: "text-brand-gold/80",
            animation: "animate-fluidInRight",
            glow: "animate-glowGold",
            divider: "bg-brand-gold/30",
          }
        : {
            container: "bg-dark-surface border-brand-gold text-dark-text-primary",
            icon: Bot,
            label: "AIris",
            iconClass: "text-brand-gold",
            labelClass: "text-brand-gold/70",
            animation: "animate-fluidInLeft",
            glow: "animate-glowSystem",
            divider: "bg-brand-gold/20",
          };

    const Icon = config.icon;

    return (
      <div className="w-[50%] min-w-0 flex-shrink-0">
        <div
          className={`h-10 px-4 py-2.5 rounded-xl border-2 ${config.container} flex items-center gap-2.5 overflow-hidden transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] ${
            state.isVisible
              ? "opacity-100 scale-100 translate-y-0"
              : "opacity-0 scale-95 translate-y-1 pointer-events-none"
          } ${state.isAnimating ? config.animation : ""} ${state.isVisible ? config.glow : ""}`}
          style={{ willChange: 'transform, opacity' }}
        >
          {/* Icon with label */}
          <div className="flex items-center gap-1.5 flex-shrink-0">
            <Icon className={`w-4 h-4 ${config.iconClass} transition-transform duration-300 ${state.isVisible ? 'scale-100' : 'scale-0'}`} />
            <span className={`text-[10px] font-semibold uppercase tracking-wider ${config.labelClass} whitespace-nowrap transition-opacity duration-300 ${state.isVisible ? 'opacity-100' : 'opacity-0'}`}>
              {config.label}
            </span>
          </div>

          {/* Divider */}
          <div className={`h-5 w-px ${config.divider} flex-shrink-0 transition-opacity duration-300 ${state.isVisible ? 'opacity-100' : 'opacity-0'}`} />

          {/* Text content */}
          <span className={`text-xs font-medium flex-1 min-w-0 truncate transition-all duration-300 ${state.isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-2'}`}>
            {state.text}
          </span>

          {/* Active indicator for user */}
          {type === 'user' && state.isVisible && (
            <div className="w-1.5 h-1.5 bg-brand-gold rounded-full animate-pulse flex-shrink-0" />
          )}
        </div>
      </div>
    );
  };

  // Render refresh bubble (separate green bubble)
  const renderRefreshBubble = (state: BubbleState) => {
    if (!state.isVisible && !state.text) {
      return null;
    }

    return (
      <div className="flex-1 max-w-2xl mx-6 flex justify-center">
        <div
          className={`h-10 px-4 py-2.5 rounded-xl border-2 bg-green-500/20 border-green-500 text-green-400 flex items-center gap-2.5 overflow-hidden transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] ${
            state.isVisible
              ? "opacity-100 scale-100 translate-y-0"
              : "opacity-0 scale-95 translate-y-1 pointer-events-none"
          } ${state.isAnimating ? "animate-fluidInLeft" : ""} ${state.isVisible ? "animate-glowGreen" : ""}`}
          style={{ willChange: 'transform, opacity' }}
        >
          {/* Spinner icon with label */}
          <div className="flex items-center gap-1.5 flex-shrink-0">
            <Loader2 className={`w-4 h-4 text-green-400 animate-spin transition-transform duration-300 ${state.isVisible ? 'scale-100' : 'scale-0'}`} />
            <span className={`text-[10px] font-semibold uppercase tracking-wider text-green-400/80 whitespace-nowrap transition-opacity duration-300 ${state.isVisible ? 'opacity-100' : 'opacity-0'}`}>
              Refreshing
            </span>
          </div>

          {/* Divider */}
          <div className={`h-5 w-px bg-green-500/30 flex-shrink-0 transition-opacity duration-300 ${state.isVisible ? 'opacity-100' : 'opacity-0'}`} />

          {/* Text content */}
          <span className={`text-xs font-medium flex-1 min-w-0 truncate transition-all duration-300 ${state.isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-2'}`}>
            {state.text}
          </span>
        </div>
      </div>
    );
  };

  // Show refresh bubble if active (takes over the space)
  if (refreshBubble.isVisible || refreshBubble.text) {
    return renderRefreshBubble(refreshBubble);
  }

  return (
    <div className="flex-1 max-w-2xl mx-6 flex gap-2 min-w-0">
      {/* Left: AIris TTS */}
      {renderBubble(systemBubble, 'system', 'left')}
      
      {/* Right: User transcriptions */}
      {renderBubble(userBubble, 'user', 'right')}
    </div>
  );
}

