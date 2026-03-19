import { z } from 'zod'

export const damageSelectionSchema = z.object({
    zone_id: z.string(),
    damage_type: z.string(),
    severity: z.number().min(1).max(5),
})

export const quoteRequestSchema = z.object({
    vin: z.string().optional().refine((val) => !val || val.length === 17, {
        message: "VIN must be exactly 17 characters if provided",
    }).transform(v => v || undefined),
    year: z.number().min(1900).max(2030),
    make: z.string().min(1),
    model: z.string().min(1),
    trim: z.string().optional(),
    mileage: z.number().min(0),
    title_status: z.enum(['clean', 'salvage', 'rebuilt', 'junk', 'lien']).optional(),
    condition_rating: z.enum(['excellent', 'good', 'fair', 'poor', 'junk']),
    drivable: z.any().transform(val => val === 'true' || val === true),
    engine_issues: z.string().optional(),
    transmission_issues: z.string().optional(),
    exterior_damage: z.array(damageSelectionSchema).optional(),
    interior_damage: z.array(damageSelectionSchema).optional(),
    glass_damage: z.array(damageSelectionSchema).optional(),
    wheel_damage: z.array(damageSelectionSchema).optional(),
    zip_code: z.string().min(5).max(10),
    city: z.string().optional(),
    state: z.string().optional(),
    pickup_address: z.string().optional(),
    classification_hint: z.enum(['junk', 'auction']).optional(),
})

export type QuoteFormData = z.infer<typeof quoteRequestSchema>