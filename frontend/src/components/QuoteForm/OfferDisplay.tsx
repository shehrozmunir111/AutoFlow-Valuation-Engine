import { formatCurrency } from '../../utils/helpers'
import Button from '../common/Button'

interface OfferDisplayProps {
    quote: {
        quote_id: string
        classification: string
        confidence: number
        offer_amount: number | null
        offer_valid_until: string
        calculation_method: string
        query_time_ms: number
        needs_human_review: boolean
    }
    onReset: () => void
}

const OfferDisplay = ({ quote, onReset }: OfferDisplayProps) => {
    const validUntil = quote.offer_valid_until ? new Date(quote.offer_valid_until) : new Date();
    const confidencePct = quote.confidence ? Math.round(Number(quote.confidence) * 100) : 0;

    return (
        <div className="max-w-2xl mx-auto">
            <div className="card text-center animate-fade-in shadow-2xl border-t-4 border-green-500">
                <h2 className="text-3xl font-bold text-gray-800 mb-6">Your Instant Offer</h2>

                {quote.needs_human_review ? (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-8 mb-6 text-center">
                        <div className="text-4xl mb-4">🔍</div>
                        <p className="text-yellow-800 text-lg font-medium">
                            This vehicle needs a quick human review. 
                        </p>
                        <p className="text-yellow-700 mt-2">
                             We'll contact you within 24 hours with a guaranteed cash offer.
                        </p>
                    </div>
                ) : (
                    <>
                        <div className="mb-8">
                            <p className="text-gray-600 mb-2">We can offer you</p>
                            <div className="text-6xl font-bold text-green-600 mb-2 drop-shadow-sm">
                                {formatCurrency(quote.offer_amount)}
                            </div>
                            <div className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full font-medium">
                                Category: {quote.classification || 'Vehicle'} ({confidencePct}% confidence)
                            </div>
                        </div>

                        <div className="bg-gray-50 rounded-xl p-6 mb-8 text-left border border-gray-100 grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <p className="text-xs uppercase tracking-wider text-gray-400 font-bold mb-1">Quote ID</p>
                                <p className="text-sm text-gray-700 font-mono bg-white px-2 py-1 rounded border overflow-hidden text-ellipsis">{quote.quote_id || 'N/A'}</p>
                            </div>
                            <div>
                                <p className="text-xs uppercase tracking-wider text-gray-400 font-bold mb-1">Valid Until</p>
                                <p className="text-sm text-gray-700">{validUntil.toLocaleString()}</p>
                            </div>
                            <div>
                                <p className="text-xs uppercase tracking-wider text-gray-400 font-bold mb-1">Pricing Strategy</p>
                                <p className="text-sm text-gray-700 capitalize">{quote.calculation_method?.replace('_', ' ') || 'standard'}</p>
                            </div>
                             <div>
                                <p className="text-xs uppercase tracking-wider text-gray-400 font-bold mb-1">Calculation Speed</p>
                                <p className="text-sm text-gray-700">{Math.round(quote.query_time_ms || 0)}ms</p>
                            </div>
                        </div>

                        <div className="flex gap-4 justify-center">
                            <Button variant="primary">Accept Offer</Button>
                            <Button variant="secondary" onClick={onReset}>
                                Start Over
                            </Button>
                        </div>
                    </>
                )}
            </div>
        </div>
    )
}

export default OfferDisplay