import { z } from 'zod'

export const createSchema = z.object({
  name: z.string().min(1, 'Nome é obrigatório'),
})

export type CreateSchema = z.output<typeof createSchema>

export const joinSchema = z.object({
  invite_key: z.string().length(8, 'Chave deve ter 8 caracteres'),
})

export type JoinSchema = z.output<typeof joinSchema>
