import { supabase } from '@/lib/supabase'

// Mock Supabase client
const mockSupabase = {
  from: vi.fn(() => ({
    select: vi.fn(() => ({
      order: vi.fn(() => ({
        limit: vi.fn(() => Promise.resolve({
          data: [],
          error: null
        }))
      }))
    }))
  }))
}

vi.mock('@supabase/supabase-js', () => ({
  createClient: vi.fn(() => mockSupabase)
}))

describe('Supabase Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates Supabase client with correct configuration', () => {
    expect(supabase).toBeDefined()
    expect(supabase.from).toBeDefined()
  })

  it('can query posts table', async () => {
    const { data, error } = await supabase
      .from('posts')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10)

    expect(mockSupabase.from).toHaveBeenCalledWith('posts')
    expect(data).toEqual([])
    expect(error).toBeNull()
  })

  it('can query comments table', async () => {
    const { data, error } = await supabase
      .from('comments')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10)

    expect(mockSupabase.from).toHaveBeenCalledWith('comments')
    expect(data).toEqual([])
    expect(error).toBeNull()
  })

  it('handles query errors', async () => {
    // Mock error response
    mockSupabase.from.mockReturnValue({
      select: vi.fn(() => ({
        order: vi.fn(() => ({
          limit: vi.fn(() => Promise.resolve({
            data: null,
            error: { message: 'Database error' }
          }))
        }))
      }))
    } as any)

    const { data, error } = await supabase
      .from('posts')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10)

    expect(data).toBeNull()
    expect(error).toEqual({ message: 'Database error' })
  })
})

