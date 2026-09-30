import React, { useState, useEffect, useRef } from 'react';
import {
  MessageSquareText,
  Send,
  Sparkles,
  Volume2,
  Globe,
  Bot,
  User,
  Hand,
  Play
} from 'lucide-react';
import { SignRenderer } from '../components/SignRenderer';
import { api } from '../services/api';
import { useSpeechSynthesis } from '../hooks/useSpeechSynthesis';
import { ChatMessage, Language, ISLTokenGesture } from '../types';

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      sender: 'assistant',
      text_content: 'Hello! I am SignBridge AI Assistant. I can assist your conversations and convert responses into Indian Sign Language (ISL) animations.',
      language: 'en',
      sign_sequence: [
        { token: 'HELLO', type: 'word', label: 'Hello', duration_ms: 1200, description: 'Friendly greeting' }
      ],
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [language, setLanguage] = useState<Language>('en');
  const [isLoading, setIsLoading] = useState(false);
  const [activeSignSequence, setActiveSignSequence] = useState<ISLTokenGesture[]>([]);

  const { speak } = useSpeechSynthesis();
  const chatBottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (customText?: string) => {
    const textToSend = customText || inputText;
    if (!textToSend.trim() || isLoading) return;

    // 1. Add user message
    const userMsg: ChatMessage = {
      id: Date.now(),
      sender: 'user',
      text_content: textToSend,
      language: language,
      timestamp: new Date().toISOString()
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsLoading(true);

    try {
      const botResponse = await api.sendChatMessage(textToSend, language);
      setMessages((prev) => [...prev, botResponse]);

      if (botResponse.sign_sequence && botResponse.sign_sequence.length > 0) {
        setActiveSignSequence(botResponse.sign_sequence);
      }
    } catch (err) {
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const quickPrompts = [
    { text: 'I need medical assistance', label: '🏥 Medical Help' },
    { text: 'Where is the exit or emergency help?', label: '🚨 Emergency' },
    { text: 'Hello, how can I learn sign language?', label: '👋 Learning' },
    { text: 'Thank you for your help', label: '🙏 Gratitude' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400">
              <MessageSquareText className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-black text-slate-900 dark:text-white">
              Assistive AI Chatbot
            </h1>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Bidirectional communication assistant with automatic text-to-ISL response animation.
          </p>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
          <Globe className="w-4 h-4 text-slate-400" />
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as Language)}
            className="bg-transparent text-xs font-bold text-slate-700 dark:text-slate-200 focus:outline-none cursor-pointer"
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी</option>
            <option value="bn">বাংলা</option>
          </select>
        </div>
      </div>

      {/* Main Two Column */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Chat Window (7 Cols) */}
        <div className="lg:col-span-7 glass-card flex flex-col h-[580px] overflow-hidden">
          {/* Messages list */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {messages.map((msg) => {
              const isUser = msg.sender === 'user';
              return (
                <div
                  key={msg.id}
                  className={`flex items-start gap-2.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-xs shrink-0 ${
                      isUser
                        ? 'bg-brand-600 text-white'
                        : 'bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/30'
                    }`}
                  >
                    {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>

                  <div
                    className={`max-w-[80%] p-3.5 rounded-2xl text-xs sm:text-sm font-medium space-y-2 ${
                      isUser
                        ? 'bg-brand-600 text-white rounded-tr-none'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-none border border-slate-200 dark:border-slate-700'
                    }`}
                  >
                    <p className="leading-relaxed">{msg.text_content}</p>

                    {/* Action buttons on bot message */}
                    {!isUser && (
                      <div className="flex items-center gap-2 pt-1 border-t border-slate-200/50 dark:border-slate-700/50">
                        <button
                          onClick={() => speak(msg.text_content, language)}
                          className="text-[11px] font-semibold text-slate-500 hover:text-brand-500 flex items-center gap-1"
                        >
                          <Volume2 className="w-3 h-3" /> Speak
                        </button>
                        {msg.sign_sequence && msg.sign_sequence.length > 0 && (
                          <button
                            onClick={() => setActiveSignSequence(msg.sign_sequence!)}
                            className="text-[11px] font-semibold text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1"
                          >
                            <Hand className="w-3 h-3" /> View ISL Sign
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
            <div ref={chatBottomRef} />
          </div>

          {/* Quick Prompts Bar */}
          <div className="p-2.5 bg-slate-50 dark:bg-slate-800/40 border-t border-slate-200 dark:border-slate-800 flex gap-2 overflow-x-auto">
            {quickPrompts.map((qp, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(qp.text)}
                className="px-2.5 py-1 bg-white dark:bg-slate-800 hover:bg-brand-500/10 hover:text-brand-600 text-[11px] font-semibold rounded-lg border border-slate-200 dark:border-slate-700 shrink-0 text-slate-600 dark:text-slate-300 transition-colors"
              >
                {qp.label}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="p-3 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 flex items-center gap-2"
          >
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type message to chat with AI assistant..."
              className="flex-1 px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-900 dark:text-slate-100"
            />
            <button
              type="submit"
              disabled={isLoading || !inputText.trim()}
              className="p-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white shadow-sm transition-colors disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>

        {/* Right: Real-Time ISL Sign Renderer Output (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Assistant Sign Response Output
          </div>
          <SignRenderer
            gestures={activeSignSequence}
            playbackSpeed={1.0}
            autoPlay={true}
          />
        </div>
      </div>
    </div>
  );
};
