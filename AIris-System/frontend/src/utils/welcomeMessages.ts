/**
 * Welcome message generator for voice-only mode
 * Provides warm, sophisticated, and time-aware welcome messages
 */

type TimeOfDay = "morning" | "afternoon" | "evening" | "night";

interface WelcomeMessageConfig {
  mode: "Activity Guide" | "Scene Description";
  cameraOn: boolean;
}

/**
 * Get time of day based on current hour
 */
function getTimeOfDay(): TimeOfDay {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 12) return "morning";
  if (hour >= 12 && hour < 17) return "afternoon";
  if (hour >= 17 && hour < 22) return "evening";
  return "night";
}

/**
 * Warm and sophisticated welcome messages organized by time of day
 * Each greeting leads with time-of-day customization
 */
const WELCOME_MESSAGES: Record<TimeOfDay, string[]> = {
  morning: [
    "Good morning. How can I help?",
    "Good morning. What would you like to do?",
    "Good morning. I'm here to help.",
    "Good morning. Ready when you are.",
    "Good morning. How may I assist?",
    "Good morning. What can I do for you?",
  ],
  afternoon: [
    "Good afternoon. How can I help?",
    "Good afternoon. What would you like to do?",
    "Good afternoon. I'm here to help.",
    "Good afternoon. Ready when you are.",
    "Good afternoon. How may I assist?",
    "Good afternoon. What can I do for you?",
  ],
  evening: [
    "Good evening. How can I help?",
    "Good evening. What would you like to do?",
    "Good evening. I'm here to help.",
    "Good evening. Ready when you are.",
    "Good evening. How may I assist?",
    "Good evening. What can I do for you?",
  ],
  night: [
    "Good evening. How can I help?",
    "Good evening. What would you like to do?",
    "Good evening. I'm here to help.",
    "Good evening. Ready when you are.",
    "Good evening. How may I assist?",
    "Good evening. What can I do for you?",
  ],
};

/**
 * Generate a warm, sophisticated, time-aware welcome message
 */
export function generateWelcomeMessage(config: WelcomeMessageConfig): string {
  const timeOfDay = getTimeOfDay();
  const messages = WELCOME_MESSAGES[timeOfDay];
  
  // Pick a random greeting
  const randomIndex = Math.floor(Math.random() * messages.length);
  const greeting = messages[randomIndex];
  
  // Build the full message with context (warm and natural, but concise)
  const parts: string[] = [greeting];
  
  // Add mode context (very brief)
  if (config.mode === "Activity Guide") {
    parts.push("Activity Guide mode.");
  } else {
    parts.push("Scene Description mode.");
  }
  
  // Add camera status (only if off, to prompt action)
  if (!config.cameraOn) {
    parts.push('Say "turn on camera" when ready.');
  }
  
  return parts.join(" ");
}

