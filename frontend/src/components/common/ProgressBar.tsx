interface ProgressBarProps {
    current: number
    total: number
    labels?: string[]
}

const ProgressBar = ({ current, total, labels }: ProgressBarProps) => {
    const progress =
        total > 1
            ? (current / (total - 1)) * 100
            : 0

    return (
        <div className="w-full">
            <div className="flex justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">
                    Step {current + 1} of {total}
                </span>
                <span className="text-sm font-medium text-gray-600">
                    {Math.round(progress)}%
                </span>
            </div>

            <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                />
            </div>

            {labels && (
                <div className="flex justify-between mt-2 text-xs text-gray-500">
                    {labels.map((label, idx) => (
                        <span
                            key={idx}
                            className={idx <= current ? 'text-blue-600 font-medium' : ''}
                        >
                            {label}
                        </span>
                    ))}
                </div>
            )}
        </div>
    )
}

export default ProgressBar