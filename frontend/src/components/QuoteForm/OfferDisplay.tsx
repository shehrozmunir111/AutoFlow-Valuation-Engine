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
    const validUntil = quote.offer_valid_until ? new Date(quote.offer_valid_until) : new Date()
    const confidencePct = quote.confidence ? Math.round(Number(quote.confidence) * 100) : 0

    return (
        <div className="max-w-2xl mx-auto">
            <div className="card text-center animate-fade-in shadow-2xl border-t-4 border-green-500">
                <h2 className="text-3xl font-bold text-gray-800 mb-6">Your Instant Offer</h2>

                {quote.needs_human_review ? (
                    <div className="mb-6 rounded-xl border border-yellow-200 bg-yellow-50 p-8 text-center">
                        <div className="mb-4 text-4xl font-semibold text-yellow-900">Review</div>
                        <p className="text-lg font-medium text-yellow-800">
                            This vehicle needs a quick human review.
                        </p>
                        <p className="mt-2 text-yellow-700">
                            We&apos;ll contact you within 24 hours with a guaranteed cash offer.
                        </p>
                        <div className="mt-6">
                            <Button variant="secondary" onClick={onReset}>
                                Start Over
                            </Button>
                        </div>
                    </div>
                ) : (
                    <>
                        <div className="mb-8">
                            <p className="mb-2 text-gray-600">We can offer you</p>
                            <div className="mb-2 text-6xl font-bold text-green-600 drop-shadow-sm">
                                {formatCurrency(quote.offer_amount)}
                            </div>
                            <div className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
                                Category: {quote.classification || 'Vehicle'} ({confidencePct}% confidence)
                            </div>
                        </div>

                        <div className="mb-8 grid grid-cols-1 gap-4 rounded-xl border border-gray-100 bg-gray-50 p-6 text-left sm:grid-cols-2">
                            <div>
                                <p className="mb-1 text-xs font-bold uppercase tracking-wider text-gray-400">Quote ID</p>
                                <p className="overflow-hidden text-ellipsis rounded border bg-white px-2 py-1 font-mono text-sm text-gray-700">
                                    {quote.quote_id || 'N/A'}
                                </p>
                            </div>
                            <div>
                                <p className="mb-1 text-xs font-bold uppercase tracking-wider text-gray-400">Valid Until</p>
                                <p className="text-sm text-gray-700">{validUntil.toLocaleString()}</p>
                            </div>
                            <div>
                                <p className="mb-1 text-xs font-bold uppercase tracking-wider text-gray-400">Pricing Strategy</p>
                                <p className="text-sm capitalize text-gray-700">
                                    {quote.calculation_method?.replace('_', ' ') || 'standard'}
                                </p>
                            </div>
                            <div>
                                <p className="mb-1 text-xs font-bold uppercase tracking-wider text-gray-400">Calculation Speed</p>
                                <p className="text-sm text-gray-700">{Math.round(quote.query_time_ms || 0)}ms</p>
                            </div>
                        </div>

                        <div className="flex justify-center gap-4">
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
