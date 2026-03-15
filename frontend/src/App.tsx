import { BrowserRouter, Routes, Route } from 'react-router-dom'
import QuoteForm from './components/QuoteForm'

function App() {
    return (
        <BrowserRouter>
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
                <header className="bg-white shadow-sm">
                    <div className="max-w-7xl mx-auto px-4 py-4">
                        <h1 className="text-2xl font-bold text-primary-700">
                            SwiftValuation AI
                        </h1>
                    </div>
                </header>

                <main className="max-w-4xl mx-auto px-4 py-8">
                    <Routes>
                        <Route path="/" element={<QuoteForm />} />
                        <Route path="/quote/:quoteId" element={<div>Quote Details</div>} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    )
}

export default App