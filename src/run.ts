import * as fs from 'fs/promises';
import { deepResearch, writeFinalReport } from './deep-research';
import { generateFeedback } from './feedback';
import { OutputManager } from './output-manager';

const output = new OutputManager();

function log(...args: any[]) {
  output.log(...args);
}

async function run() {
  // Get command line arguments
  const args = process.argv.slice(2);
  
  // Parse arguments
  const query = args[0];
  const breadth = parseInt(args[1] ?? '', 10) || 4;  // default 4
  const depth = parseInt(args[2] ?? '', 10) || 2;    // default 2

  if (!query) {
    console.error('Usage: npm start "<research query>" [breadth] [depth]');
    console.error('Example: npm start "AI advances in 2024" 4 2');
    process.exit(1);
  }

  log(`Creating research plan...`);

  // Generate follow-up questions
  const followUpQuestions = await generateFeedback({
    query: query,
  });

  // Since we can't get interactive answers, we'll modify the combined query
  const combinedQuery = `
Initial Query: ${query}
Research Parameters:
- Breadth: ${breadth}
- Depth: ${depth}
Follow-up Questions to Consider:
${followUpQuestions.map((q: string) => `- ${q}`).join('\n')}
`;

  log('\nResearching your topic...');
  log('\nStarting research with progress tracking...\n');
  
  const { learnings, visitedUrls } = await deepResearch({
    query: combinedQuery,
    breadth,
    depth,
    onProgress: (progress) => {
      output.updateProgress(progress);
    },
  });

  log(`\n\nLearnings:\n\n${learnings.join('\n')}`);
  log(
    `\n\nVisited URLs (${visitedUrls.length}):\n\n${visitedUrls.join('\n')}`,
  );
  log('Writing final report...');

  const report = await writeFinalReport({
    prompt: combinedQuery,
    learnings,
    visitedUrls,
  });

  // Save report to file
  await fs.writeFile('output.md', report, 'utf-8');

  console.log(`\n\nFinal Report:\n\n${report}`);
  console.log('\nReport has been saved to output.md');
}

run().catch(console.error);
