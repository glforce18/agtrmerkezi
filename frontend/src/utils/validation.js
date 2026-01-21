/**
 * AGTR Merkezi - Form Validation Utilities
 * Comprehensive validation helpers for forms
 */

/**
 * Validation rules
 */
export const rules = {
  required: (value, fieldName = 'Alan') => {
    if (value === null || value === undefined || value === '') {
      return `${fieldName} zorunludur`
    }
    if (Array.isArray(value) && value.length === 0) {
      return `${fieldName} zorunludur`
    }
    return null
  },

  minLength: (min) => (value, fieldName = 'Alan') => {
    if (!value || value.length < min) {
      return `${fieldName} en az ${min} karakter olmali`
    }
    return null
  },

  maxLength: (max) => (value, fieldName = 'Alan') => {
    if (value && value.length > max) {
      return `${fieldName} en fazla ${max} karakter olmali`
    }
    return null
  },

  email: (value) => {
    if (!value) return null
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(value)) {
      return 'Gecerli bir e-posta adresi girin'
    }
    return null
  },

  username: (value) => {
    if (!value) return null
    if (value.length < 3) {
      return 'Kullanici adi en az 3 karakter olmali'
    }
    if (value.length > 32) {
      return 'Kullanici adi en fazla 32 karakter olmali'
    }
    if (!/^[a-zA-Z0-9_]+$/.test(value)) {
      return 'Kullanici adi sadece harf, rakam ve alt cizgi icermeli'
    }
    return null
  },

  password: (value) => {
    if (!value) return null
    if (value.length < 8) {
      return 'Sifre en az 8 karakter olmali'
    }
    if (!/[A-Z]/.test(value)) {
      return 'Sifre en az 1 buyuk harf icermeli'
    }
    if (!/[a-z]/.test(value)) {
      return 'Sifre en az 1 kucuk harf icermeli'
    }
    if (!/[0-9]/.test(value)) {
      return 'Sifre en az 1 rakam icermeli'
    }
    return null
  },

  passwordMatch: (confirmValue) => (value) => {
    if (value !== confirmValue) {
      return 'Sifreler eslesmiyor'
    }
    return null
  },

  numeric: (value, fieldName = 'Alan') => {
    if (value === null || value === undefined || value === '') return null
    if (isNaN(Number(value))) {
      return `${fieldName} sayisal olmali`
    }
    return null
  },

  min: (minValue) => (value, fieldName = 'Alan') => {
    if (value === null || value === undefined || value === '') return null
    if (Number(value) < minValue) {
      return `${fieldName} en az ${minValue} olmali`
    }
    return null
  },

  max: (maxValue) => (value, fieldName = 'Alan') => {
    if (value === null || value === undefined || value === '') return null
    if (Number(value) > maxValue) {
      return `${fieldName} en fazla ${maxValue} olmali`
    }
    return null
  },

  url: (value) => {
    if (!value) return null
    try {
      new URL(value)
      return null
    } catch {
      return 'Gecerli bir URL girin'
    }
  },

  phone: (value) => {
    if (!value) return null
    const phoneRegex = /^(\+90|0)?[1-9][0-9]{9}$/
    if (!phoneRegex.test(value.replace(/\s/g, ''))) {
      return 'Gecerli bir telefon numarasi girin'
    }
    return null
  },

  steamId: (value) => {
    if (!value) return null
    // STEAM_0:0:12345678 or STEAM_0:1:12345678
    const steamIdRegex = /^STEAM_[0-5]:[01]:\d+$/
    // 76561198012345678 (64-bit)
    const steamId64Regex = /^7656119\d{10}$/

    if (!steamIdRegex.test(value) && !steamId64Regex.test(value)) {
      return 'Gecerli bir Steam ID girin'
    }
    return null
  },

  ip: (value) => {
    if (!value) return null
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
    if (!ipRegex.test(value)) {
      return 'Gecerli bir IP adresi girin'
    }
    return null
  },

  port: (value) => {
    if (!value) return null
    const port = Number(value)
    if (isNaN(port) || port < 1 || port > 65535) {
      return 'Gecerli bir port numarasi girin (1-65535)'
    }
    return null
  }
}

/**
 * Validate a single field with multiple rules
 * @param {any} value - Field value
 * @param {Array} validators - Array of validator functions
 * @param {string} fieldName - Field name for error messages
 * @returns {string|null} - Error message or null
 */
export function validateField(value, validators, fieldName = 'Alan') {
  for (const validator of validators) {
    const error = validator(value, fieldName)
    if (error) return error
  }
  return null
}

/**
 * Validate entire form
 * @param {Object} formData - Form data object
 * @param {Object} validationSchema - Schema with field validators
 * @returns {Object} - { isValid: boolean, errors: Object }
 */
export function validateForm(formData, validationSchema) {
  const errors = {}
  let isValid = true

  for (const [field, config] of Object.entries(validationSchema)) {
    const value = formData[field]
    const validators = config.validators || []
    const fieldName = config.label || field

    const error = validateField(value, validators, fieldName)
    if (error) {
      errors[field] = error
      isValid = false
    }
  }

  return { isValid, errors }
}

/**
 * Create reactive form validation hook
 * @param {Object} initialValues - Initial form values
 * @param {Object} validationSchema - Validation schema
 * @returns {Object} - Form state and methods
 */
export function useFormValidation(initialValues, validationSchema) {
  const values = { ...initialValues }
  const errors = {}
  const touched = {}

  const validate = (field) => {
    if (!validationSchema[field]) return true

    const config = validationSchema[field]
    const error = validateField(values[field], config.validators || [], config.label || field)
    errors[field] = error
    return !error
  }

  const validateAll = () => {
    let isValid = true
    for (const field of Object.keys(validationSchema)) {
      touched[field] = true
      if (!validate(field)) {
        isValid = false
      }
    }
    return isValid
  }

  const reset = () => {
    Object.assign(values, initialValues)
    Object.keys(errors).forEach(key => delete errors[key])
    Object.keys(touched).forEach(key => delete touched[key])
  }

  const setFieldValue = (field, value) => {
    values[field] = value
    if (touched[field]) {
      validate(field)
    }
  }

  const setFieldTouched = (field) => {
    touched[field] = true
    validate(field)
  }

  return {
    values,
    errors,
    touched,
    validate,
    validateAll,
    reset,
    setFieldValue,
    setFieldTouched
  }
}

/**
 * Common validation schemas
 */
export const schemas = {
  login: {
    username: {
      label: 'Kullanici adi',
      validators: [rules.required]
    },
    password: {
      label: 'Sifre',
      validators: [rules.required]
    }
  },

  register: {
    username: {
      label: 'Kullanici adi',
      validators: [rules.required, rules.username]
    },
    email: {
      label: 'E-posta',
      validators: [rules.required, rules.email]
    },
    password: {
      label: 'Sifre',
      validators: [rules.required, rules.password]
    }
  },

  serverConfig: {
    name: {
      label: 'Sunucu adi',
      validators: [rules.required, rules.minLength(3), rules.maxLength(64)]
    },
    ip: {
      label: 'IP adresi',
      validators: [rules.required, rules.ip]
    },
    port: {
      label: 'Port',
      validators: [rules.required, rules.port]
    }
  },

  payment: {
    amount: {
      label: 'Tutar',
      validators: [rules.required, rules.numeric, rules.min(10)]
    }
  },

  profile: {
    email: {
      label: 'E-posta',
      validators: [rules.email]
    },
    steamId: {
      label: 'Steam ID',
      validators: [rules.steamId]
    }
  }
}

export default {
  rules,
  validateField,
  validateForm,
  useFormValidation,
  schemas
}
