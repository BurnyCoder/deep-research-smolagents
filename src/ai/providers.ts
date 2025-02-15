import { getEncoding } from 'js-tiktoken';
import { RecursiveCharacterTextSplitter } from './text-splitter';
import fetch from 'node-fetch';

interface PortkeyResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: {
    index: number;
    message: {
      role: string;
      content: string;
      refusal: null | string;
    };
    finish_reason: string;
  }[];
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export async function callPortkeyAPI(messages: ChatMessage[], options: { reasoningEffort?: string; structuredOutputs?: boolean } = {}) {
  const response = await fetch('https://api.portkey.ai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-portkey-api-key': process.env.PORTKEY_API_KEY!,
      'x-portkey-virtual-key': process.env.PORTKEY_VIRTUAL_KEY_OPENAI!,
    },
    body: JSON.stringify({
      model: process.env.OPENAI_MODEL || 'o3-mini',
      messages,
    }),
  });

  if (!response.ok) {
    throw new Error(`Portkey API error: ${response.statusText}`);
  }

  const data: PortkeyResponse = await response.json();
  return data.choices[0]?.message?.content || '';
}

// Models
export const o3MiniModel = async (prompt: string, options: { reasoningEffort?: string; structuredOutputs?: boolean } = {}) => {
  const messages: ChatMessage[] = [
    { role: 'user', content: prompt }
  ];
  return callPortkeyAPI(messages, options);
};

const MinChunkSize = 140;
const encoder = getEncoding('o200k_base');

// trim prompt to maximum context size
export function trimPrompt(
  prompt: string,
  contextSize = Number(process.env.CONTEXT_SIZE) || 128_000,
) {
  if (!prompt) {
    return '';
  }

  const length = encoder.encode(prompt).length;
  if (length <= contextSize) {
    return prompt;
  }

  const overflowTokens = length - contextSize;
  // on average it's 3 characters per token, so multiply by 3 to get a rough estimate of the number of characters
  const chunkSize = prompt.length - overflowTokens * 3;
  if (chunkSize < MinChunkSize) {
    return prompt.slice(0, MinChunkSize);
  }

  const splitter = new RecursiveCharacterTextSplitter({
    chunkSize,
    chunkOverlap: 0,
  });
  const trimmedPrompt = splitter.splitText(prompt)[0] ?? '';

  // last catch, there's a chance that the trimmed prompt is same length as the original prompt, due to how tokens are split & innerworkings of the splitter, handle this case by just doing a hard cut
  if (trimmedPrompt.length === prompt.length) {
    return trimPrompt(prompt.slice(0, chunkSize), contextSize);
  }

  // recursively trim until the prompt is within the context size
  return trimPrompt(trimmedPrompt, contextSize);
}