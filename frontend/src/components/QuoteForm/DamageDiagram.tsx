import { useFormContext } from 'react-hook-form'
import { useState } from 'react'

interface DamageDiagramProps {
    type: 'exterior' | 'interior'
}

const EXTERIOR_ZONES = [
    { id: 'hood', label: 'Hood', x: 150, y: 80 },
    { id: 'roof', label: 'Roof', x: 150, y: 40 },
    { id: 'front_bumper', label: 'Front Bumper', x: 150, y: 120 },
    { id: 'rear_bumper', label: 'Rear Bumper', x: 150, y: 10 },
    { id: 'driver_door', label: 'Driver Door', x: 80, y: 60 },
    { id: 'passenger_door', label: 'Passenger Door', x: 220, y: 60 },
]

const INTERIOR_ZONES = [
    { id: 'dashboard', label: 'Dashboard', x: 150, y: 40 },
    { id: 'front_seats', label: 'Front Seats', x: 150, y: 70 },
    { id: 'rear_seats', label: 'Rear Seats', x: 150, y: 100 },
    { id: 'carpet', label: 'Carpet/Floor', x: 150, y: 130 },
]

const DAMAGE_TYPES = ['Scratch', 'Dent', 'Crack', 'Tear', 'Stain', 'Hole']

const DamageDiagram = ({ type }: DamageDiagramProps) => {
    const { setValue, watch } = useFormContext()
    const [selectedZone, setSelectedZone] = useState<string | null>(null)

    const fieldName = type === 'exterior' ? 'exterior_damage' : 'interior_damage'
    const currentDamage = watch(fieldName) || []

    const zones = type === 'exterior' ? EXTERIOR_ZONES : INTERIOR_ZONES

    const handleZoneClick = (zoneId: string) => {
        setSelectedZone(zoneId)
    }

    const addDamage = (damageType: string, severity: number) => {
        const newDamage = {
            zone_id: selectedZone,
            damage_type: damageType,
            severity,
        }

        setValue(fieldName, [...currentDamage, newDamage])
        setSelectedZone(null)
    }

    const removeDamage = (index: number) => {
        const updated = [...currentDamage]
        updated.splice(index, 1)
        setValue(fieldName, updated)
    }

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-800">
                {type === 'exterior' ? 'Exterior' : 'Interior'} Damage
            </h2>
            <p className="text-gray-600">Click on zones to mark damage (optional)</p>

            {/* SVG Diagram */}
            <div className="relative bg-gray-100 rounded-lg p-4 h-64">
                <svg viewBox="0 0 300 150" className="w-full h-full">
                    {/* Car outline */}
                    <rect x="50" y="20" width="200" height="100" fill="white" stroke="#333" strokeWidth="2" rx="10" />

                    {/* Zones */}
                    {zones.map((zone) => {
                        const isSelected = currentDamage.some((d: any) => d.zone_id === zone.id)
                        return (
                            <g key={zone.id} onClick={() => handleZoneClick(zone.id)} className="cursor-pointer">
                                <circle
                                    cx={zone.x}
                                    cy={zone.y}
                                    r={15}
                                    fill={isSelected ? '#ef4444' : '#e5e7eb'}
                                    stroke="#333"
                                    strokeWidth={selectedZone === zone.id ? 3 : 1}
                                />
                                <text x={zone.x} y={zone.y + 4} textAnchor="middle" fontSize="10" fill="#333">
                                    {zone.label}
                                </text>
                            </g>
                        )
                    })}
                </svg>
            </div>

            {/* Damage selector popup */}
            {selectedZone && (
                <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-medium mb-2">Add damage to {selectedZone}</h4>
                    <div className="flex flex-wrap gap-2">
                        {DAMAGE_TYPES.map((type) => (
                            <div key={type} className="flex gap-1">
                                {[1, 2, 3, 4, 5].map((severity) => (
                                    <button
                                        key={severity}
                                        type="button"
                                        onClick={() => addDamage(type, severity)}
                                        className="w-8 h-8 text-xs bg-white border rounded hover:bg-blue-100"
                                        title={`${type} - Severity ${severity}`}
                                    >
                                        {severity}
                                    </button>
                                ))}
                            </div>
                        ))}
                    </div>
                    <button
                        type="button"
                        onClick={() => setSelectedZone(null)}
                        className="mt-2 text-sm text-gray-600 underline"
                    >
                        Cancel
                    </button>
                </div>
            )}

            {/* Selected damage list */}
            {currentDamage.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium">Marked Damage:</h4>
                    {currentDamage.map((damage: any, idx: number) => (
                        <div key={idx} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                            <span>
                                {damage.zone_id}: {damage.damage_type} (Severity {damage.severity})
                            </span>
                            <button
                                type="button"
                                onClick={() => removeDamage(idx)}
                                className="text-red-600 text-sm"
                            >
                                Remove
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default DamageDiagram