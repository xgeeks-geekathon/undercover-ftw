// Major ref: https://js.langchain.com/docs/modules/indexes/vector_stores/integrations/pinecone
import dotenv from "dotenv";
import { Document } from "langchain/document";
import { OpenAIEmbeddings } from "langchain/embeddings/openai";
import { PineconeClient } from "@pinecone-database/pinecone";
import { PineconeStore } from "langchain/vectorstores/pinecone";
import fs from "fs";
import path from "path";

dotenv.config({ path: `.env.local` });

const MAX_TOKENS = 8191;

const fileNames = fs.readdirSync("blogs");

// Helper function to chunk a string into smaller parts
const chunkString = (str, length) => {
  const size = Math.ceil(str.length / length);
  const r = Array(size);
  let offset = 0;

  for (let i = 0; i < size; i++) {
    r[i] = str.substr(offset, length);
    offset += length;
  }

  return r;
};

const langchainDocs = [];

fileNames.forEach((fileName) => {
  const filePath = path.join("blogs", fileName);
  const fileContent = fs.readFileSync(filePath, "utf8");

  const chunks = chunkString(fileContent, MAX_TOKENS);

  chunks.forEach((chunk, index) => {
    langchainDocs.push(
      new Document({
        metadata: { fileName, chunkIndex: index },
        pageContent: chunk,
      })
    );
  });
});

const client = new PineconeClient();

async function run() {
  await client.init({
    apiKey: process.env.PINECONE_API_KEY,
    environment: process.env.PINECONE_ENVIRONMENT,
  });

  const pineconeIndex = client.Index(process.env.PINECONE_INDEX);

  return await PineconeStore.fromDocuments(
    langchainDocs,
    new OpenAIEmbeddings({ openAIApiKey: process.env.OPENAI_API_KEY }),
    {
      pineconeIndex,
    }
  );
}

try {
  await run();
  console.log("[ INFO: ] Source documents indexed successfully.");
  process.exit(0);
} catch (error) {
  console.log(error);
  process.exit(0);
  // TODO: return 0 and let the pod's continue
}
