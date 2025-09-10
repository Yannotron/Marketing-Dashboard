import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string;

// Check if we have valid Supabase credentials
const hasValidCredentials = supabaseUrl && supabaseAnonKey && 
  supabaseUrl !== "your_supabase_url_here" && 
  supabaseAnonKey !== "your_supabase_anon_key_here";

if (!hasValidCredentials) {
  // eslint-disable-next-line no-console
  console.warn("Missing or invalid VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY in environment. App will run in demo mode.");
}

// Create a mock Supabase client for development when credentials are missing
const createMockClient = () => ({
  from: () => ({
    select: () => ({
      order: () => ({
        limit: () => ({
          then: (callback: any) => callback({ data: [], error: null })
        })
      })
    }),
    insert: () => ({ then: (callback: any) => callback({ data: [], error: null }) }),
    update: () => ({ then: (callback: any) => callback({ data: [], error: null }) }),
    delete: () => ({ then: (callback: any) => callback({ data: [], error: null }) })
  })
});

export const supabase = hasValidCredentials 
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: { persistSession: false, autoRefreshToken: false },
    })
  : createMockClient() as any;


