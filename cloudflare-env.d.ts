declare namespace Cloudflare {
  interface Env {
    DB?: D1Database;
    BUCKET?: R2Bucket;
    AUDIO?: R2Bucket;
    SUPABASE_URL?: string;
    SUPABASE_PUBLISHABLE_KEY?: string;
    LITTLEFINGER_OWNER_EMAIL?: string;
  }
}
