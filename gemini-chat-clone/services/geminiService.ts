
import { GoogleGenAI, GenerateContentResponse } from "@google/genai";

/**
 * Initializes the Gemini API client and provides methods for streaming chat responses.
 */
export class GeminiService {
  private ai: GoogleGenAI;

  constructor() {
    // API_KEY is provided by the environment
    // Fix: Using process.env.API_KEY directly as required by the coding guidelines
    this.ai = new GoogleGenAI({ apiKey: process.env.API_KEY as string });
  }

  /**
   * Generates a streaming response for a chat conversation.
   * @param prompt The user's input message.
   * @param history Optional previous conversation context.
   * @param onChunk Callback for each received text chunk.
   */
  async streamChat(
    prompt: string,
    history: { role: 'user' | 'model'; parts: { text: string }[] }[],
    onChunk: (text: string) => void
  ) {
    try {
      // Use gemini-3-flash-preview for fast, chat-optimized responses
      const responseStream = await this.ai.models.generateContentStream({
        model: 'gemini-3-flash-preview',
        contents: [
          ...history,
          { role: 'user', parts: [{ text: prompt }] }
        ],
        config: {
          temperature: 0.7,
          topP: 0.95,
          topK: 40,
        }
      });

      let fullText = "";
      for await (const chunk of responseStream) {
        // Fix: Use the .text property directly as per Gemini API guidelines
        const chunkText = chunk.text;
        if (chunkText) {
          fullText += chunkText;
          onChunk(chunkText);
        }
      }
      return fullText;
    } catch (error) {
      console.error("Gemini API Error:", error);
      throw error;
    }
  }
}

export const geminiService = new GeminiService();
