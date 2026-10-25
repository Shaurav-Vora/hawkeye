import { DAY_MS, DEFAULTS, clamp01 } from "./types.ts";
import type { MemoryRecord, QueryResult, RetrievedMemory } from "./types.ts";
import { cosine, embed, jaccard, tokenize } from "./embeddings.ts";
import type { MemoryStoreService } from "./memoryStore.ts";
import type { TrustLedgerService } from "./trustLedger.ts";
import { FEEDBACK_DELTAS } from "./types.ts";
import type { FeedbackKind } from "./types.ts";
import { snapshot } from "./memoryStore.ts";

const LAYER_WEIGHT: Record<MemoryRecord["layer"], number> = {
  long_term: 1.0,
  working: 0.8,
  short_term: 0.6,
};
﻿