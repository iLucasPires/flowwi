import { StatusCodes } from 'http-status-codes'
import type { FetchError } from 'ofetch'

interface iErrorAllAuth {
  message: string
  code: string
  param: string
}

interface iErrorDRF {
  detail: string
  code: string
  attr: string | null
}

interface tApiError {
  detail?: string
  errors?: (iErrorDRF | iErrorAllAuth)[]
}

export function parseError(error: FetchError): string {
  const data = error.data as tApiError | undefined

  if (!data?.errors) {
    return data?.detail || error.message || 'Erro inesperado'
  }

  return data.errors
    .map((err: iErrorDRF | iErrorAllAuth) => ('message' in err ? err.message : err.detail))
    .join(' | ')
}

export function toastError(error: FetchError) {
  const toast = useToast()
  const status = error?.status
  const message = parseError(error)

  const config = {
    description: message,
    color: 'error' as const,
  }

  switch (status) {
    case StatusCodes.BAD_REQUEST:
    case StatusCodes.UNPROCESSABLE_ENTITY:
      return toast.add({
        ...config,
        title: 'Erro de validação',
        color: 'warning',
      })

    case StatusCodes.UNAUTHORIZED:
      return toast.add({
        ...config,
        title: 'Não autorizado',
        description: message || 'Faça login novamente.',
      })

    case StatusCodes.FORBIDDEN:
      return toast.add({
        ...config,
        title: 'Acesso negado',
      })

    case StatusCodes.NOT_FOUND:
      return toast.add({
        ...config,
        title: 'Não encontrado',
        color: 'warning',
      })

    case StatusCodes.INTERNAL_SERVER_ERROR:
      return toast.add({
        ...config,
        title: 'Erro interno',
        description: 'Algo deu errado no servidor.',
      })

    default:
      return toast.add({
        ...config,
        title: 'Erro inesperado',
      })
  }
}
