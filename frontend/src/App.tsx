import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-background">
          <h1 className="text-4xl font-bold text-center p-8">
            Workflow Monitoring Platform
          </h1>
          <p className="text-center text-muted-foreground">
            Enterprise Video Intelligence & Safety Monitoring
          </p>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App

