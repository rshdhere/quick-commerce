import type { StoreItem } from "@repo/types";
import { z } from "zod";

export const storeItemSchema = z.object({
  storeId: z.string().trim().min(1),
  sku: z.string().trim().min(1),
}) satisfies z.ZodType<StoreItem>;
