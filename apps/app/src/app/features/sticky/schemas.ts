import { z } from 'zod'

export const stickyVisibilityEnum = z.enum(['private', 'workplace'])

export const stickyCreateSchema = z.object({
  text: z.string().default(''),
  color: z
    .string()
    .regex(/^#[0-9a-fA-F]{6}$/, 'Cor inválida')
    .default('#FEE440'),
  visibility: stickyVisibilityEnum.default('private'),
})

export type StickyCreateSchema = z.output<typeof stickyCreateSchema>
