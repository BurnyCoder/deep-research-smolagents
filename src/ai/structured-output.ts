import { z } from 'zod';

interface StructuredOutputOptions<T> {
  model: (prompt: string) => Promise<string>;
  system?: string;
  prompt: string;
  schema: z.ZodType<T>;
  abortSignal?: AbortSignal;
}

function generateSchemaExample(schema: z.ZodType<any>): string {
  if (schema instanceof z.ZodObject) {
    const shape = schema._def.shape();
    const example: any = {};
    for (const [key, value] of Object.entries(shape)) {
      if (value instanceof z.ZodArray) {
        example[key] = [generateSchemaExample(value.element)];
      } else if (value instanceof z.ZodObject) {
        example[key] = generateSchemaExample(value);
      } else if (value instanceof z.ZodString) {
        example[key] = "example_string";
      } else if (value instanceof z.ZodNumber) {
        example[key] = 123;
      } else if (value instanceof z.ZodBoolean) {
        example[key] = true;
      }
    }
    return example;
  } else if (schema instanceof z.ZodArray) {
    return [generateSchemaExample(schema.element)];
  }
  return "example_value";
}

export async function generateStructuredOutput<T>({
  model,
  system,
  prompt,
  schema,
  abortSignal,
}: StructuredOutputOptions<T>): Promise<{ object: T }> {
  const example = generateSchemaExample(schema);
  const fullPrompt = `${system ? `${system}\n\n` : ''}${prompt}\n\n
You must respond with a valid JSON object that exactly matches this structure:
${JSON.stringify(example, null, 2)}

Make sure to:
1. Include all required fields
2. Use the exact field names shown
3. Match the types exactly (strings, arrays, objects)
4. Format as valid JSON

Your response:`;
  
  const response = await model(fullPrompt);
  
  try {
    // Try to extract JSON from the response if it's not already JSON
    const jsonMatch = response.match(/```json\n?([\s\S]*?)\n?```/) || response.match(/\{[\s\S]*\}/);
    const jsonString = jsonMatch ? jsonMatch[0].replace(/```json\n?|```/g, '') : response;
    
    const jsonResponse = JSON.parse(jsonString);
    const validatedResponse = schema.parse(jsonResponse);
    return { object: validatedResponse };
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new Error(`Failed to validate response structure: ${JSON.stringify(error.errors, null, 2)}`);
    }
    throw new Error(`Failed to parse JSON response: ${error}`);
  }
} 