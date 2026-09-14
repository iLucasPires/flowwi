export type tAuthSocialProvider = 'google' | 'github'

export type tAuthType = 'login' | 'register'

export interface iLogin {
  username: string
  password: string
}

export interface iRegister {
  id: number
  email: string
  first_name: string
  last_name: string
  is_active: boolean
}
