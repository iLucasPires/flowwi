import { z } from 'zod'

/** Attribution stored with a cover picked from Unsplash. */
export const UnsplashCreditSchema = z.object({
  source: z.literal('unsplash'),
  photo_id: z.string(),
  photo_url: z.string(),
  author_name: z.string(),
  author_username: z.string(),
  author_url: z.string(),
})

export const FormThemeAccentColors = [
  'neutral',
  'red',
  'orange',
  'amber',
  'green',
  'emerald',
  'cyan',
  'blue',
  'indigo',
  'violet',
  'pink',
] as const

export const FormThemeRadii = ['none', 'sm', 'md', 'lg', 'xl'] as const
export const FormThemeInputSizes = ['sm', 'md', 'lg'] as const
export const FormThemeFonts = ['sans', 'serif', 'mono'] as const

export const FormThemeOutSchema = z.object({
  id: z.number(),
  workplace: z.number().nullable().optional(),
  name: z.string(),
  is_preset: z.boolean(),
  background_image: z.string().nullable().optional(),
  cover_style: z.string().default(''),
  cover_credit: UnsplashCreditSchema.nullable().default(null),
  accent_color: z.enum(FormThemeAccentColors).default('neutral'),
  radius: z.enum(FormThemeRadii).default('md'),
  input_size: z.enum(FormThemeInputSizes).default('md'),
  font: z.enum(FormThemeFonts).default('sans'),
  custom_css: z.string().default(''),
  created_at: z.string().optional(),
})

export const FormOutSchema = z.object({
  id: z.number(),
  title: z.string(),
  icon: z.string().default(''),
  description: z.string(),
  is_published: z.boolean(),
  created_at: z.string(),
  public_id: z.string(),
  cover_image: z.string().nullable().optional(),
  cover_style: z.string().default(''),
  cover_credit: UnsplashCreditSchema.nullable().default(null),
  require_auth: z.boolean(),
  require_identity: z.boolean(),
  grid_columns: z.number().default(1),
  responses_count: z.number().default(0),
  theme: z.union([z.number(), FormThemeOutSchema]).nullable().optional(),
})

export const FormBlockOutSchema = z.object({
  id: z.number(),
  form: z.number(),
  page: z.number().nullable().optional(),
  title: z.string(),
  type: z.string(),
  required: z.boolean(),
  order: z.number(),
  config: z.record(z.string(), z.any()),
  col_span: z.number().default(0),
  col_start: z.number().default(0),
  condition: z.record(z.string(), z.any()).default({}),
  client_id: z.string().default(''),
})

export const FormPageOutSchema = z.object({
  id: z.number(),
  form: z.number(),
  title: z.string().optional().default(''),
  description: z.string().optional().default(''),
  order: z.number(),
})

export const FormAnswerOutSchema = z.object({
  id: z.number(),
  block: z.number(),
  value: z.any(),
})

export const FormResponseOutSchema = z.object({
  id: z.number(),
  form: z.number(),
  created_at: z.string(),
  answers: z.array(FormAnswerOutSchema),
  respondent_email: z.string().optional().default(''),
  respondent_phone: z.string().optional().default(''),
})

export type tFormOut = z.infer<typeof FormOutSchema>
export type tFormThemeOut = z.infer<typeof FormThemeOutSchema>
export type tFormBlockOut = z.infer<typeof FormBlockOutSchema>
export type tFormPageOut = z.infer<typeof FormPageOutSchema>
export type tFormAnswerOut = z.infer<typeof FormAnswerOutSchema>
export type tFormResponseOut = z.infer<typeof FormResponseOutSchema>
