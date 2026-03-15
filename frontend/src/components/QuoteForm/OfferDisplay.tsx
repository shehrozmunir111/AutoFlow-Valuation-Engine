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
    const validUntil = new Date(quote.offer_valid_until)

    return (
        <div className="max-w-2xl mx-auto">
            <div className="card text-center">
                <h2 className="text-3xl font-bold text-gray-800 mb-6">Your Instant Offer</h2>

                {quote.needs_human_review ? (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
                        <p className="text-yellow-800 text-lg">
                            This vehicle needs manual review. We'll contact you within 24 hours with a guaranteed offer.
                        </p>
                    </div>
                ) : (
                    <>
                        <div className="mb-8">
                            <p className="text-gray-600 mb-2">We can offer you</p>
                            <div className="text-6xl font-bold text-green-600 mb-2">
                                {formatCurrency(quote.offer_amount)}
                            </div>
                            <p className="text-gray-500">
                                Valuation Category: {quote.classification} ({Math.round(quote.confidence * 100)}% confidence)
                            </p>
                        </div>

                        <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left">
                            <p className="text-sm text-gray-600 mb-1">
                                <span className="font-medium">Quote ID:</span> {quote.quote_id}
                            </p>
                            <p className="text-sm text-gray-600 mb-1">
                                <span className="font-medium">Valid until:</span>{' '}
                                {validUntil.toLocaleString()}
                            </p>
                            <p className="text-sm text-gray-600">
                                <span className="font-medium">Response time:</span>{' '}
                                {Math.round(quote.query_time_ms)}ms
                            </p>
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