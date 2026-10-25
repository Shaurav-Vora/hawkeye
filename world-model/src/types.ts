export type ISODate = string;
export type EntityId = string;
export type ContextId = string;
export type RelationshipId = string;
export type FactId = string;
export type EventId = string;

/** Every write carries provenance. No provenance, no write (rejected at the boundary). */
export type Provenance = {
  kind: "manual" | "rss" | "api" | "file" | "agent" | "pipeline" | "wire" | (string & {});
  by?: string;
  at: ISODate | Date;
  url?: string;
  checksum?: string;
  runId?: string;
};

/** Provenance after normalization: `at` is always an ISO string internally. */
export type StoredProvenance = Omit<Provenance, "at"> & { at: ISODate };

export type Entity = {
  type: string;
  id: EntityId;
  attrs: Record<string, unknown>;
  schemaVersion: number;
  source: StoredProvenance;
  createdAt: ISODate;
  updatedAt: ISODate;
  name?: string;
  aliases: string[];
  state: "emerging" | "active" | "archived";
  aggregates?: {
    mentionCount: number;
    firstSeenAt?: ISODate;
    lastSeenAt?: ISODate;
    linkedStoryIds: string[];
  };
};

export type Context = {
  type: string;
  id: ContextId;
  attrs: Record<string, unknown>;
  parent?: ContextId;
  startedAt?: ISODate;
  endedAt?: ISODate;
  schemaVersion: number;
  source: StoredProvenance;
  createdAt: ISODate;
  updatedAt: ISODate;
};

export type Relationship = {
  id: RelationshipId;
  from: EntityId;
  type: string;
  to: EntityId;
  context?: ContextId;
  attrs?: Record<string, unknown>;
  validFrom?: ISODate;
  validTo?: ISODate;
  schemaVersion: number;
  source: StoredProvenance;
  createdAt: ISODate;
  supersededBy?: RelationshipId;
};

export type Fact = {
  id: FactId;
  about: EntityId;
  predicate: string;
  value: unknown;
  confidence: number;
  context?: ContextId;
  source: StoredProvenance;
  assertedAt: ISODate;
  supersededBy?: FactId;
};

export type Snapshot = {
  id: string;
  at: ISODate;
  context?: ContextId;
  entities: EntityId[];
  attrs?: Record<string, unknown>;
  schemaVersion: number;
  source: StoredProvenance;
};

export type Tombstone = {
  targetId: string;
  reason?: string;
  at: ISODate;
  by?: string;
};

export type Alias = {
  aliasId: EntityId;
  primaryId: EntityId;
  mergedAt: ISODate;
  mergedBy: string;
  reason: string;
};

export type ViewRebuild = {
  view: string;
  at: ISODate;
  durationMs: number;
  eventsReplayed: number;
};

export type EventKind =
  | "upsertEntity"
  | "upsertContext"
  | "relate"
  | "assertFact"
  | "snapshot"
  | "tombstone"
  | "alias"
  | "view-rebuild";

export type WorldEvent = {
  id: EventId;
  seq: number;
  kind: EventKind;
  payload: unknown;
  schemaVersion: number;
  at: ISODate;
};

export type AuditEntry = {
  seq: number;
  at: ISODate;
  kind: string;
  actor: string;
  summary: string;
  eventId?: EventId;
  runId?: string;
};

export type ObservationRecord = {
  id: string;
  externalId: string;
  entityId: EntityId;
  checksum: string;
  at: ISODate;
  storyId?: string;
  entityIds?: EntityId[];
  syncedAt?: ISODate;
  stale: boolean;
};

export type StoryAggregate = {
  id: string;
  title: string;
  memberIds: string[];
  entityNames: string[];
  entityIds: EntityId[];
  sources: string[];
  firstAt: ISODate;
  lastAt: ISODate;
  milestones: { kind: string; at: ISODate }[];
};

export type ScoreSnapshot = {
  storyId: string;
  at: ISODate;
  velocity1h: number;
  velocity24h: number;
  velocity7d: number;
  trendDirection: -1 | 0 | 1;
};

export type IngestObservation = {
  externalId: string;
  type?: string;
  title: string;
  text?: string;
  at: ISODate;
  source: Provenance;
  entities?: { type: string; name: string }[];
};

export type MergeProposal = {
  id: string;
  leftId: EntityId;
  rightId: EntityId;
  leftName: string;
  rightName: string;
  similarity: number;
  reason: string;
  status: "pending" | "approved" | "rejected";
  proposedAt: ISODate;
  resolvedAt?: ISODate;
  resolvedBy?: string;
};

export type ConflictPolicy =
  | "most-recent-wins"
  | "highest-confidence-wins"
  | "source-priority"
  | "manual";

export type ResolverOptions = {
  strategy?: string | string[];
  autoMergeAt?: number;
  reviewBand?: [number, number];
};

export type WorldModelOptions = {
  storage?: "memory" | "local";
  namespace: string;
  directory?: string;
  clock?: () => Date;
  resolver?: ResolverOptions;
  conflictPolicy?: ConflictPolicy;
  sourcePriority?: string[];
};

export type IngestReport = {
  runId: string;
  processed: number;
  skippedUnchanged: number;
  clusters: number;
  eventsAppended: number;
  changed: boolean;
  stepTimingsMs: { step: number; name: string; ms: number }[];
};