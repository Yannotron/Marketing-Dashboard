# Reddit Dashboard Web App

A React-based web application for viewing Reddit insights and analytics.

## Development Setup

### Prerequisites
- Node.js 20+
- npm or pnpm

### Local Development

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables (optional for development):**
   Create a `.env` file in the web directory:
   ```env
   VITE_SUPABASE_URL=your_supabase_url_here
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
   ```
   
   **Note:** For production, these values are automatically provided by GitHub Secrets.

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5173` (or the port shown in terminal)

### Production Deployment

The web app is automatically deployed to GitHub Pages when changes are pushed to the main branch. The deployment uses GitHub Secrets for Supabase configuration:

- `SUPABASE_URL` → `VITE_SUPABASE_URL`
- `SUPABASE_ANON_KEY` → `VITE_SUPABASE_ANON_KEY`

#### Setting up GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_ANON_KEY`: Your Supabase anonymous key

#### Testing with Secrets Locally

You can test the build with real Supabase credentials locally:

```bash
# Set environment variables
export SUPABASE_URL="your_supabase_url"
export SUPABASE_ANON_KEY="your_supabase_anon_key"

# Build with secrets
./scripts/build-with-secrets.sh
```

#### GitHub Actions Workflows

- **CI** (`.github/workflows/ci.yml`): Runs on PRs, validates secrets and builds web app
- **Deploy** (`.github/workflows/deploy-web.yml`): Deploys to GitHub Pages on main branch
- **Test** (`.github/workflows/test-web-with-secrets.yml`): Manual workflow to test with secrets

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run test` - Run tests
- `npm run lint` - Run ESLint

### Features

- **Overview**: Dashboard with pipeline status, insights count, and top insights
- **Topics**: Categorized view with filtering and sorting
- **Explorer**: Search interface with detail drawer
- **Drafts**: Markdown export functionality

### Tech Stack

- React 18 + TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- shadcn/ui for components
- React Query for data fetching
- Supabase for backend
- Recharts for data visualization
