import { useState } from 'react'
import { calculateQuote } from '../utils/api'
import type { QuoteRequest, QuoteResponse } from '../types'

export const useQuote = () => {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [quote, setQuote] = useState<QuoteResponse | null>(null)

    const getQuote = async (data: QuoteRequest) => {
        setLoading(true)
        setError(null)

        try {
            const response = await calculateQuote(data)
            setQuote(response)
            return response
        } catch (err: any) {
            const rawDetail = err.response?.data?.detail;
            let errorMessage = 'Failed to get quote';
            
            if (typeof rawDetail === 'string') {
                errorMessage = rawDetail;
            } else if (Array.isArray(rawDetail)) {
                // Handle standard FastAPI 422 list
                errorMessage = rawDetail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('; ');
            } else if (rawDetail && typeof rawDetail === 'object') {
                errorMessage = JSON.stringify(rawDetail);
            }
            
            setError(errorMessage);
            return null;
        } finally {
            setLoading(false)
        }
    }

    const resetQuote = () => {
        setQuote(null)
        setError(null)
    }

    return {
        quote,
        loading,
        error,
        getQuote,
        resetQuote,
    }
}