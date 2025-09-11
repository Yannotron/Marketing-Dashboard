import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Explorer } from '@/pages/Explorer'
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

describe('Explorer Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders explorer page title', () => {
    renderWithQueryClient(<Explorer />)
    
    expect(screen.getByText('Explorer')).toBeInTheDocument()
  })

  it('displays search input', () => {
    renderWithQueryClient(<Explorer />)
    
    const searchInput = screen.getByPlaceholderText(/search posts/i)
    expect(searchInput).toBeInTheDocument()
  })

  it('displays filter controls', () => {
    renderWithQueryClient(<Explorer />)
    
    expect(screen.getByText('Subreddit')).toBeInTheDocument()
    expect(screen.getByText('Sort by')).toBeInTheDocument()
  })

  it('handles search input changes', async () => {
    renderWithQueryClient(<Explorer />)
    
    const searchInput = screen.getByPlaceholderText(/search posts/i)
    fireEvent.change(searchInput, { target: { value: 'test query' } })
    
    expect(searchInput).toHaveValue('test query')
  })

  it('handles subreddit filter changes', async () => {
    renderWithQueryClient(<Explorer />)
    
    const subredditSelect = screen.getByRole('combobox', { name: /subreddit/i })
    fireEvent.click(subredditSelect)
    
    // Should show subreddit options
    await waitFor(() => {
      expect(screen.getByText('All')).toBeInTheDocument()
    })
  })

  it('handles sort changes', async () => {
    renderWithQueryClient(<Explorer />)
    
    const sortSelect = screen.getByRole('combobox', { name: /sort by/i })
    fireEvent.click(sortSelect)
    
    // Should show sort options
    await waitFor(() => {
      expect(screen.getByText('Score')).toBeInTheDocument()
      expect(screen.getByText('Comments')).toBeInTheDocument()
      expect(screen.getByText('Date')).toBeInTheDocument()
    })
  })

  it('displays posts after loading', async () => {
    renderWithQueryClient(<Explorer />)
    
    await waitFor(() => {
      expect(screen.getByText('Test Post 1')).toBeInTheDocument()
    })
  })

  it('displays post details', async () => {
    renderWithQueryClient(<Explorer />)
    
    await waitFor(() => {
      expect(screen.getByText('100')).toBeInTheDocument()
      expect(screen.getByText('50')).toBeInTheDocument()
      expect(screen.getByText('r/test')).toBeInTheDocument()
      expect(screen.getByText('u/user1')).toBeInTheDocument()
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

    renderWithQueryClient(<Explorer />)
    
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

    renderWithQueryClient(<Explorer />)
    
    await waitFor(() => {
      expect(screen.getByText('No posts found')).toBeInTheDocument()
    })
  })
})

