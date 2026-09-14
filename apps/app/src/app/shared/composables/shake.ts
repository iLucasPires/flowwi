export function useShake() {
  const shaking = ref(false)

  function shake() {
    shaking.value = true
    setTimeout(() => {
      shaking.value = false
    }, 500)
  }

  return { shaking, shake }
}
