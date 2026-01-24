<template>
  <div class="forum-live-preview">
    <!-- Toggle -->
    <div class="preview-toggle">
      <n-button-group size="small">
        <n-button :type="mode === 'edit' ? 'primary' : 'default'" @click="mode = 'edit'">
          <template #icon><n-icon><EditOutlined /></n-icon></template>
          Duzenle
        </n-button>
        <n-button :type="mode === 'preview' ? 'primary' : 'default'" @click="mode = 'preview'">
          <template #icon><n-icon><VisibilityOutlined /></n-icon></template>
          Onizleme
        </n-button>
        <n-button :type="mode === 'split' ? 'primary' : 'default'" @click="mode = 'split'">
          <template #icon><n-icon><VerticalSplitOutlined /></n-icon></template>
          Bolunmus
        </n-button>
      </n-button-group>
    </div>

    <!-- Content Area -->
    <div class="content-area" :class="mode">
      <!-- Editor -->
      <div class="editor-pane" v-show="mode !== 'preview'">
        <n-input
          ref="editorRef"
          v-model:value="localContent"
          type="textarea"
          :rows="rows"
          :placeholder="placeholder"
          @input="handleInput"
          @keydown="handleKeydown"
        />

        <!-- Quick Format Buttons -->
        <div class="format-toolbar">
          <n-tooltip v-for="btn in formatButtons" :key="btn.key" trigger="hover">
            <template #trigger>
              <n-button text size="small" @click="insertFormat(btn.format)">
                <n-icon :size="16"><component :is="btn.icon" /></n-icon>
              </n-button>
            </template>
            {{ btn.label }} ({{ btn.shortcut }})
          </n-tooltip>
        </div>
      </div>

      <!-- Preview -->
      <div class="preview-pane" v-show="mode !== 'edit'">
        <div v-if="!localContent" class="empty-preview">
          Onizleme icin icerik girin...
        </div>
        <div v-else class="preview-content" v-html="renderedContent"></div>
      </div>
    </div>

    <!-- Character Count -->
    <div class="char-count" v-if="maxLength">
      <span :class="{ 'over-limit': localContent.length > maxLength }">
        {{ localContent.length }}
      </span>
      / {{ maxLength }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { NButton, NButtonGroup, NIcon, NInput, NTooltip } from 'naive-ui'
import {
  Edit3Icon,
  EyeIcon,
  ColumnsIcon,
  BoldIcon,
  ItalicIcon,
  UnderlineIcon,
  CodeIcon,
  QuoteIcon,
  LinkIcon,
  ListIcon,
  ListOrderedIcon,
  ImageIcon
} from 'lucide-vue-next'

const EditOutlined = Edit3Icon
const VisibilityOutlined = EyeIcon
const VerticalSplitOutlined = ColumnsIcon
const FormatBold = BoldIcon
const FormatItalic = ItalicIcon
const FormatUnderlined = UnderlineIcon
const Code = CodeIcon
const FormatQuote = QuoteIcon
const Link = LinkIcon
const FormatListBulleted = ListIcon
const FormatListNumbered = ListOrderedIcon
const Image = ImageIcon
import { useDebounceFn } from '@vueuse/core'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Icerik yazin...'
  },
  rows: {
    type: Number,
    default: 10
  },
  maxLength: {
    type: Number,
    default: null
  },
  defaultMode: {
    type: String,
    default: 'edit',
    validator: (v) => ['edit', 'preview', 'split'].includes(v)
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

// State
const mode = ref(props.defaultMode)
const localContent = ref(props.modelValue)
const editorRef = ref(null)

// Format buttons config
const formatButtons = [
  { key: 'bold', label: 'Kalin', icon: FormatBold, format: '**', shortcut: 'Ctrl+B' },
  { key: 'italic', label: 'Italik', icon: FormatItalic, format: '*', shortcut: 'Ctrl+I' },
  { key: 'code', label: 'Kod', icon: Code, format: '`', shortcut: 'Ctrl+`' },
  { key: 'quote', label: 'Alinti', icon: FormatQuote, format: '> ', shortcut: 'Ctrl+Q' },
  { key: 'link', label: 'Link', icon: Link, format: '[text](url)', shortcut: 'Ctrl+K' },
  { key: 'ul', label: 'Liste', icon: FormatListBulleted, format: '- ', shortcut: 'Ctrl+L' },
  { key: 'ol', label: 'Numarali Liste', icon: FormatListNumbered, format: '1. ', shortcut: 'Ctrl+O' },
  { key: 'image', label: 'Resim', icon: Image, format: '![alt](url)', shortcut: 'Ctrl+G' }
]

// Computed - Simple markdown rendering
const renderedContent = computed(() => {
  let html = localContent.value || ''

  // Escape HTML
  html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

  // Code blocks
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')

  // Bold
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')

  // Italic
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')

  // Images
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />')

  // Quotes
  html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')

  // Headers
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>')

  // Lists
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')

  // Line breaks
  html = html.replace(/\n/g, '<br>')

  return html
})

// Methods
const handleInput = useDebounceFn(() => {
  emit('update:modelValue', localContent.value)
  emit('change', localContent.value)
}, 300)

const handleKeydown = (e) => {
  // Keyboard shortcuts
  if (e.ctrlKey || e.metaKey) {
    switch (e.key.toLowerCase()) {
      case 'b':
        e.preventDefault()
        insertFormat('**')
        break
      case 'i':
        e.preventDefault()
        insertFormat('*')
        break
      case '`':
        e.preventDefault()
        insertFormat('`')
        break
      case 'k':
        e.preventDefault()
        insertFormat('[text](url)')
        break
    }
  }
}

const insertFormat = (format) => {
  const textarea = editorRef.value?.$el?.querySelector('textarea')
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = localContent.value.substring(start, end)

  let newText = ''
  let newCursorPos = start

  if (format === '> ') {
    // Quote - add at line start
    newText = format + selectedText
    newCursorPos = start + format.length
  } else if (format === '- ' || format === '1. ') {
    // List
    newText = format + selectedText
    newCursorPos = start + format.length
  } else if (format === '[text](url)') {
    // Link
    if (selectedText) {
      newText = `[${selectedText}](url)`
      newCursorPos = start + selectedText.length + 3
    } else {
      newText = '[text](url)'
      newCursorPos = start + 1
    }
  } else if (format === '![alt](url)') {
    // Image
    newText = '![alt](url)'
    newCursorPos = start + 2
  } else {
    // Wrap selection
    if (selectedText) {
      newText = format + selectedText + format
      newCursorPos = end + format.length * 2
    } else {
      newText = format + format
      newCursorPos = start + format.length
    }
  }

  localContent.value =
    localContent.value.substring(0, start) +
    newText +
    localContent.value.substring(end)

  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(newCursorPos, newCursorPos)
  })

  handleInput()
}

// Watch prop changes
watch(() => props.modelValue, (val) => {
  if (val !== localContent.value) {
    localContent.value = val
  }
})
</script>

<style scoped>
.forum-live-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-toggle {
  display: flex;
  justify-content: flex-end;
}

.content-area {
  display: flex;
  gap: 16px;
  min-height: 200px;
}

.content-area.edit .editor-pane {
  flex: 1;
}

.content-area.preview .preview-pane {
  flex: 1;
}

.content-area.split .editor-pane,
.content-area.split .preview-pane {
  flex: 1;
}

.editor-pane {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.format-toolbar {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 4px;
}

.preview-pane {
  border: 1px solid var(--n-border-color);
  border-radius: 4px;
  padding: 12px;
  background: var(--n-color);
  overflow-y: auto;
}

.empty-preview {
  color: var(--n-text-color-3);
  font-style: italic;
}

.preview-content {
  line-height: 1.6;
}

.preview-content :deep(h1),
.preview-content :deep(h2),
.preview-content :deep(h3) {
  margin: 16px 0 8px;
}

.preview-content :deep(pre) {
  background: var(--n-color-modal);
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}

.preview-content :deep(code) {
  background: var(--n-color-modal);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.preview-content :deep(blockquote) {
  border-left: 4px solid var(--n-primary-color);
  padding-left: 16px;
  margin: 8px 0;
  color: var(--n-text-color-2);
}

.preview-content :deep(img) {
  max-width: 100%;
  border-radius: 4px;
}

.preview-content :deep(a) {
  color: var(--n-primary-color);
}

.preview-content :deep(ul) {
  padding-left: 20px;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: var(--n-text-color-3);
}

.char-count .over-limit {
  color: var(--n-error-color);
  font-weight: bold;
}
</style>
