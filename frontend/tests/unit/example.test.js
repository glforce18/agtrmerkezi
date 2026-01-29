import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

describe('Example Test Suite', () => {
  it('should pass basic assertion', () => {
    expect(1 + 1).toBe(2)
  })

  it('should work with arrays', () => {
    const arr = [1, 2, 3]
    expect(arr).toHaveLength(3)
    expect(arr).toContain(2)
  })

  it('should work with objects', () => {
    const obj = { name: 'AGTR Merkezi', version: '1.0' }
    expect(obj).toHaveProperty('name')
    expect(obj.name).toBe('AGTR Merkezi')
  })
})
