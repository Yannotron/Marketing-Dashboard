import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Overview } from '@/pages/Overview'
import * as supabase from '@/lib/supabase'

// Mock Supabase
vi.mock('@/lib/supabase', () => ({
  supabase: {
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        order: vi.fn(() => ({
          limit: vi.fn(() => Promise.resolve({
            data: [
              {
                id: '1',
                title: 'Test Post 1',
                score: 100,
                num_comments: 50,
                created_at: '2024-01-01T00:00:00Z',
                subreddit: 'test',
                author: 'user1',
                url: 'https://example.com/1',
                text: 'Test content 1'
              },
              {
                id: '2',
                title: 'Test Post 2',
                score: 200,
                num_comments: 75,
                created_at: '2024-01-01T01:00:00Z',
                subreddit: 'test',
                author: 'user2',
                url: 'https://example.com/2',
                text: 'Test content 2'
              }
            ],
            error: null
          }))
        }))
      }))
    }))
  }
}))

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  )
}

describe('Overview Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders overview page title', () => {
    renderWithQueryClient(<Overview />)
    
    expect(screen.getByText('Overview')).toBeInTheDocument()
  })

  it('displays loading state initially', () => {
    renderWithQueryClient(<Overview />)
    
    // Should show loading state
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('displays posts after loading', async () => {
    renderWithQueryClient(<Overview />)
    
    await waitFor(() => {
      expect(screen.getByText('Test Post 1')).toBeInTheDocument()
      expect(screen.getByText('Test Post 2')).toBeInTheDocument()
    })
  })

  it('displays post scores and comments', async () => {
    renderWithQueryClient(<Overview />)
    
    await waitFor(() => {
      expect(screen.getByText('100')).toBeInTheDocument()
      expect(screen.getByText('50')).toBeInTheDocument()
      expect(screen.getByText('200')).toBeInTheDocument()
      expect(screen.getByText('75')).toBeInTheDocument()
    })
  })

  it('displays post metadata', async () => {
    renderWithQueryClient(<Overview />)
    
    await waitFor(() => {
      expect(screen.getByText('r/test')).toBeInTheDocument()
      expect(screen.getByText('u/user1')).toBeInTheDocument()
      expect(screen.getByText('u/user2')).toBeInTheDocument()
    })
  })

  it('handles error state', async () => {
    // Mock error response
    const mockSupabase = vi.mocked(supabase.supabase)
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

    renderWithQueryClient(<Overview />)
    
    await waitFor(() => {
      expect(screen.getByText('Error loading posts')).toBeInTheDocument()
    })
  })

  it('displays empty state when no posts', async () => {
    // Mock empty response
    const mockSupabase = vi.mocked(supabase.supabase)
    mockSupabase.from.mockReturnValue({
      select: vi.fn(() => ({
        order: vi.fn(() => ({
          limit: vi.fn(() => Promise.resolve({
            data: [],
            error: null
          }))
        }))
      }))
    } as any)

    renderWithQueryClient(<Overview />)
    
    await waitFor(() => {
      expect(screen.getByText('No posts found')).toBeInTheDocument()
    })
  })
})
