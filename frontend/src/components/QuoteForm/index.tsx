import { useState } from 'react'
import { useForm, FormProvider } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { quoteRequestSchema } from '../../schemas/quote'
import { useQuote } from '../../hooks/useQuote'
import type { QuoteRequest } from '../../types'
import Button from '../common/Button'
import ProgressBar from '../common/ProgressBar'
import VehicleInfoStep from './VehicleInfoStep'
import ConditionStep from './ConditionStep'
import DamageDiagram from './DamageDiagram'
import LocationStep from './LocationStep'
import OfferDisplay from './OfferDisplay'

const STEPS = [
    'Vehicle Info',
    'Condition',
    'Exterior Damage',
    'Interior Damage',
    'Location',
    'Offer'
]

const QuoteForm = () => {
    const [currentStep, setCurrentStep] = useState(0)
    const { quote, loading, error, getQuote, resetQuote } = useQuote()

    const methods = useForm<QuoteRequest>({
        resolver: zodResolver(quoteRequestSchema),
        mode: 'onChange',
        defaultValues: {
            drivable: true,
            condition_rating: 'good',
            title_status: 'clean',
        } as Partial<QuoteRequest>,
    })

    const handleNext = async () => {
        const stepFields: Record<number, any[]> = {
            0: ['vin', 'year', 'make', 'model', 'mileage', 'title_status'],
            1: ['condition_rating', 'drivable', 'engine_issues', 'transmission_issues'],
            2: ['exterior_damage', 'glass_damage', 'wheel_damage'],
            3: ['interior_damage'],
            4: ['zip_code', 'city', 'state', 'pickup_address']
        };

        const isValid = await methods.trigger(stepFields[currentStep]);
        if (!isValid) return;

        if (currentStep === STEPS.length - 2) {
            // Last step before offer - submit
            const isFullyValid = await methods.trigger();
            if (!isFullyValid) return;

            const data = methods.getValues();
            const response = await getQuote(data);
            if (!response) {
                return; // Stop if there was an API error, allowing the error box to show
            }
        }

        setCurrentStep(prev => Math.min(prev + 1, STEPS.length - 1))
    }

    const handleBack = () => {
        setCurrentStep(prev => Math.max(prev - 1, 0))
    }

    const handleReset = () => {
        methods.reset()
        resetQuote()
        setCurrentStep(0)
    }

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center p-20 bg-white rounded-2xl shadow-xl max-w-2xl mx-auto">
                 <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mb-4"></div>
                 <p className="text-xl font-medium text-gray-700">Calculating your instant offer...</p>
                 <p className="text-gray-500 mt-2 italic text-sm text-center">AI logic is evaluating your vehicle condition and finding the best partner price.</p>
            </div>
        )
    }

    if (quote) {
        return <OfferDisplay quote={quote} onReset={handleReset} />
    }

    return (
        <FormProvider {...methods}>
            <div className="max-w-2xl mx-auto">
                <div className="card mb-6">
                    <ProgressBar
                        current={currentStep}
                        total={STEPS.length}
                        labels={STEPS}
                    />
                </div>

                <div className="card">
                    {currentStep === 0 && <VehicleInfoStep />}
                    {currentStep === 1 && <ConditionStep />}
                    {currentStep === 2 && <DamageDiagram type="exterior" />}
                    {currentStep === 3 && <DamageDiagram type="interior" />}
                    {currentStep === 4 && <LocationStep />}

                    {error && (
                        <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg">
                            {error}
                        </div>
                    )}

                    <div className="flex justify-between mt-8">
                        <Button
                            variant="secondary"
                            onClick={handleBack}
                            disabled={currentStep === 0}
                        >
                            Back
                        </Button>

                        <Button
                            onClick={handleNext}
                            isLoading={loading}
                        >
                            {currentStep === STEPS.length - 2 ? 'Get Quote' : 'Next'}
                        </Button>
                    </div>
                </div>
            </div>
        </FormProvider>
    )
}

export default QuoteForm