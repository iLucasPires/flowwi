import { z } from 'zod'

export const taskPriorityEnum = z.enum(['low', 'medium', 'high', 'urgent'])

export const taskCreateSchema = z.object({
  title: z.string().min(1, 'Título é obrigatório'),
  description: z.string().default(''),
  type: z.number().nullable().default(null),
  priority: taskPriorityEnum.default('medium'),
  status: z.number().nullable().default(null),
  assignees: z.array(z.number()).default([]),
  startDate: z.any().nullable().default(null),
  endDate: z.any().nullable().default(null),
})

export type TaskCreateSchema = z.output<typeof taskCreateSchema>

export const taskUpdateSchema = z.object({
  title: z.string().min(1, 'Título é obrigatório'),
  description: z.string().default(''),
  type: z.number().nullable().default(null),
  status: z.number().nullable().default(null),
  priority: taskPriorityEnum.default('medium'),
  assignees: z.array(z.number()).default([]),
  deadline: z.any().nullable().default(null),
})

export type TaskUpdateSchema = z.output<typeof taskUpdateSchema>
