import { computed, type Ref } from 'vue'

export interface iPasswordStrength {
  score: number
  max: number
  label: string
  color: 'error' | 'warning' | 'success'
}

/**
 * Amostra dos 200 passwords mais comuns do common-passwords.txt.gz que o
 * Django embute (django.contrib.auth.password_validation.CommonPasswordValidator).
 * Só uma pista visual — a validação real acontece no backend com a lista completa.
 */
const COMMON_PASSWORDS = new Set([
  '123456', '123456789', 'qwerty', 'password', '111111', '12345678', 'abc123', '1234567',
  'password1', '12345', '1234567890', '123123', '000000', 'iloveyou', '1234', '1q2w3e4r5t',
  'qwertyuiop', '123', 'monkey', 'dragon', '123456a', '654321', '123321', '666666', '1qaz2wsx',
  '121212', 'myspace1', 'homelesspa', '123qwe', 'a123456', '1q2w3e4r', '123abc', 'qwe123',
  '7777777', 'qwerty123', '987654321', 'target123', 'zxcvbnm', 'tinkle', 'qwerty1', '222222',
  '1g2w3e4r', 'gwerty', 'zag12wsx', 'gwerty123', '555555', 'fuckyou', 'asdfghjkl', '112233',
  '1q2w3e', 'qazwsx', '123123123', 'princess', 'computer', '12345a', '159753', 'ashley',
  'michael', 'football', '1234qwer', 'sunshine', 'aaaaaa', 'iloveyou1', 'fuckyou1',
  '789456123', 'daniel', 'asdfgh', '777777', '123654', '11111', 'princess1', '999999',
  'abcd1234', '11111111', 'passer2009', 'love', 'shadow', '888888', 'superman', 'football1',
  'love123', 'jordan23', 'jessica', '12qwaszx', 'baseball', 'monkey1', 'killer', 'a12345',
  '123456789a', 'master', 'asd123', 'asdf', 'samsung', 'charlie', 'azerty', 'soccer',
  'q1w2e3r4t5y6', 'jordan', '88888888', 'fqrg7cs493', 'michael1', 'jesus1', 'blink182',
  '789456', 'qwer1234', 'linkedin', 'babygirl1', 'thomas', 'q1w2e3r4', 'status', 'michelle',
  'liverpool', 'nicole', '333333', 'asdasd', 'qwert', 'j38ifubn', '131313', '987654',
  '0123456789', 'lovely', 'andrew', 'gfhjkm', 'joshua', 'anthony', 'hello1', 'justin',
  'angel1', 'zxcvbn', 'hello', 'iloveyou2', '1111111', '1111', 'jennifer', 'naruto', 'tigger',
  'hunter', 'welcome', '159357', 'babygirl', '147258369', 'pokemon', '101010', 'bitch1',
  'jessica1', 'robert', '0987654321', '102030', 'parola', 'secret', '5201314', 'fuckyou2',
  '696969', 'loveme', '123456q', 'purple', 'mother', 'anthony1', 'apple', 'qazwsxedc',
  'money1', 'trustno1', 'matthew', 'buster', 'baseball1', '1111111111', 'andrea', 'hannah',
  'basketball', 'freedom', 'passw0rd', 'soccer1', 'abc', 'iloveu', 'chelsea', 'george',
  'friends', 'william', 'samantha', 'amanda', 'golfer', 'summer', 'chocolate', 'asdf1234',
  'qwerty12', 'number1', 'flower', 'maggie', 'letmein', 'charlie1', 'pakistan', 'batman',
  'superman1', 'asshole1', 'butterfly', '147258', 'marina', '010203',
])

/**
 * Espelha, em ordem, os validadores em `AUTH_PASSWORD_VALIDATORS`
 * (apps/api/config/settings.py) — quando uma regra falha aqui, o cadastro
 * também será rejeitado pelo backend.
 */
const RULES: Array<(password: string, email: string) => boolean> = [
  // MinimumLengthValidator (min_length padrão: 8)
  (password) => password.length >= 8,
  // UserAttributeSimilarityValidator (aproximação: não conter o usuário do email)
  (password, email) => {
    const local = email.split('@')[0]?.toLowerCase()
    return !local || local.length < 3 || !password.toLowerCase().includes(local)
  },
  // CommonPasswordValidator (aproximação com uma amostra da lista do Django)
  (password) => !COMMON_PASSWORDS.has(password.toLowerCase()),
  // NumericPasswordValidator
  (password) => !/^\d+$/.test(password),
]

const LEVELS: Array<Omit<iPasswordStrength, 'score' | 'max'>> = [
  { label: 'Muito fraca', color: 'error' },
  { label: 'Fraca', color: 'error' },
  { label: 'Média', color: 'warning' },
  { label: 'Forte', color: 'success' },
  { label: 'Muito forte', color: 'success' },
]

export function usePasswordStrength(password: Ref<string>, email: Ref<string>) {
  const strength = computed<iPasswordStrength>(() => {
    const score = password.value
      ? RULES.filter((rule) => rule(password.value, email.value)).length
      : 0

    return { score, max: RULES.length, ...(LEVELS[score] ?? LEVELS[0]!) }
  })

  return { strength }
}
