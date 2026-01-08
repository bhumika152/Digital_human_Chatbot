import { GoogleGenAI } from "@google/genai";

/**
 * Initializes the Gemini API client and provides methods for streaming chat responses.
 */
export class GeminiService {
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
    // Fix: Create a new GoogleGenAI instance right before the API call to ensure it uses the most up-to-date configuration
    // Fix: Use process.env.API_KEY directly as required by the coding guidelines
    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

    try {
      // Use gemini-3-flash-preview for fast, chat-optimized responses
      // Fix: Query ai.models.generateContentStream with both the model name and prompt/contents
      const responseStream = await ai.models.generateContentStream({
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
        // Fix: Use the .text property directly (not a method) as per Gemini API guidelines
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