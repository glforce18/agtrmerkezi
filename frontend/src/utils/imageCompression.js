/**
 * AGTR Merkezi - Client-Side Image Compression Utility
 * Yuklemeden once resimleri sikistirarak bant genisligi tasarrufu saglar
 */

/**
 * Compress an image file before upload
 * @param {File} file - The image file to compress
 * @param {Object} options - Compression options
 * @param {number} options.maxWidth - Maximum width (default: 1920)
 * @param {number} options.maxHeight - Maximum height (default: 1080)
 * @param {number} options.quality - JPEG quality 0-1 (default: 0.8)
 * @param {string} options.outputType - Output mime type (default: 'image/jpeg')
 * @param {number} options.maxSizeKB - Maximum file size in KB (default: 500)
 * @returns {Promise<File>} - Compressed file
 */
export async function compressImage(file, options = {}) {
  const {
    maxWidth = 1920,
    maxHeight = 1080,
    quality = 0.8,
    outputType = 'image/jpeg',
    maxSizeKB = 500
  } = options

  // Validate file type
  if (!file.type.startsWith('image/')) {
    throw new Error('Dosya bir resim degil')
  }

  // Skip compression for small files (< 100KB) and GIFs
  if (file.size < 100 * 1024 || file.type === 'image/gif') {
    return file
  }

  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (event) => {
      const img = new Image()
      img.onload = () => {
        try {
          const compressedFile = processImage(img, file.name, {
            maxWidth,
            maxHeight,
            quality,
            outputType,
            maxSizeKB
          })
          resolve(compressedFile)
        } catch (error) {
          reject(error)
        }
      }
      img.onerror = () => reject(new Error('Resim yuklenemedi'))
      img.src = event.target.result
    }
    reader.onerror = () => reject(new Error('Dosya okunamadi'))
    reader.readAsDataURL(file)
  })
}

/**
 * Process and compress the image using canvas
 */
function processImage(img, fileName, options) {
  const { maxWidth, maxHeight, quality, outputType, maxSizeKB } = options

  // Calculate new dimensions while maintaining aspect ratio
  let { width, height } = img

  if (width > maxWidth) {
    height = (height * maxWidth) / width
    width = maxWidth
  }

  if (height > maxHeight) {
    width = (width * maxHeight) / height
    height = maxHeight
  }

  // Create canvas
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height

  // Draw image
  const ctx = canvas.getContext('2d')
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'
  ctx.drawImage(img, 0, 0, width, height)

  // Try to compress to target size
  let currentQuality = quality
  let blob = null
  const maxIterations = 5
  let iteration = 0

  // Convert to blob with quality adjustment
  while (iteration < maxIterations) {
    const dataUrl = canvas.toDataURL(outputType, currentQuality)
    blob = dataURLtoBlob(dataUrl)

    // Check if size is acceptable
    if (blob.size <= maxSizeKB * 1024 || currentQuality <= 0.3) {
      break
    }

    // Reduce quality for next iteration
    currentQuality -= 0.1
    iteration++
  }

  // Generate new filename
  const extension = outputType === 'image/png' ? '.png' : '.jpg'
  const baseName = fileName.replace(/\.[^.]+$/, '')
  const newFileName = `${baseName}_compressed${extension}`

  return new File([blob], newFileName, { type: outputType })
}

/**
 * Convert data URL to Blob
 */
function dataURLtoBlob(dataURL) {
  const arr = dataURL.split(',')
  const mime = arr[0].match(/:(.*?);/)[1]
  const bstr = atob(arr[1])
  let n = bstr.length
  const u8arr = new Uint8Array(n)
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n)
  }
  return new Blob([u8arr], { type: mime })
}

/**
 * Compress multiple images
 * @param {FileList|File[]} files - Array of image files
 * @param {Object} options - Compression options
 * @returns {Promise<File[]>} - Array of compressed files
 */
export async function compressImages(files, options = {}) {
  const fileArray = Array.from(files)
  const compressedFiles = await Promise.all(
    fileArray.map(file => compressImage(file, options).catch(() => file))
  )
  return compressedFiles
}

/**
 * Get image dimensions without loading the full image
 * @param {File} file - Image file
 * @returns {Promise<{width: number, height: number}>}
 */
export function getImageDimensions(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (event) => {
      const img = new Image()
      img.onload = () => {
        resolve({ width: img.width, height: img.height })
      }
      img.onerror = () => reject(new Error('Resim boyutlari alinamadi'))
      img.src = event.target.result
    }
    reader.onerror = () => reject(new Error('Dosya okunamadi'))
    reader.readAsDataURL(file)
  })
}

/**
 * Create thumbnail from image
 * @param {File} file - Image file
 * @param {number} size - Thumbnail size (default: 150)
 * @returns {Promise<string>} - Base64 data URL of thumbnail
 */
export async function createThumbnail(file, size = 150) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (event) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')

        // Calculate crop dimensions for square thumbnail
        const minDim = Math.min(img.width, img.height)
        const sx = (img.width - minDim) / 2
        const sy = (img.height - minDim) / 2

        canvas.width = size
        canvas.height = size

        ctx.imageSmoothingEnabled = true
        ctx.imageSmoothingQuality = 'high'
        ctx.drawImage(img, sx, sy, minDim, minDim, 0, 0, size, size)

        resolve(canvas.toDataURL('image/jpeg', 0.7))
      }
      img.onerror = () => reject(new Error('Thumbnail olusturulamadi'))
      img.src = event.target.result
    }
    reader.onerror = () => reject(new Error('Dosya okunamadi'))
    reader.readAsDataURL(file)
  })
}

/**
 * Format file size to human readable
 * @param {number} bytes - File size in bytes
 * @returns {string} - Formatted size
 */
export function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
