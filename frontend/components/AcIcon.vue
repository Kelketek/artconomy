<template>
  <div :class="`ac-icon-container ac-icon--size-${size}`">
    <svg :class="`ac-icon-${icon.slug}`" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="100%">
      <title>{{icon.title}}</title>
      <path fill="currentColor" :d="icon.path"/>
    </svg>
  </div>
</template>

<style>
.ac-icon-container {
  display: inline-flex;
  align-content: center;
}

.ac-icon--size-small {
  width: 1.25em;
}

.ac-icon--size-x-small {
  width: 1em;
}

.ac-icon--size-default {
  width: 1.5rem;
}

.ac-icon--size-large {
  width: 1.75rem;
}

.ac-icon--size-x-large {
  width: 2rem;
}
</style>

<script setup lang="ts">
import type {SimpleIcon} from 'simple-icons'

declare type Size = 'x-small' | 'small' | 'default' | 'large' | 'x-large'

withDefaults(defineProps<{ icon: SimpleIcon, size?: Size }>(), {size: 'default'})
</script>
