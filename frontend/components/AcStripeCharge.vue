<template>
  <div :id="`${id}-card-number`"/>
</template>

<style>
.StripeElement {
  border-bottom-style: solid;
  border-bottom-color: rgba(255, 255, 255, 0.7);
  border-bottom-width: 1px;
}

.StripeElement.focus {
  border-bottom-color: white;
}

.StripeElement.invalid {
  border-bottom-color: darkred;
}
</style>

<script setup lang="ts">
import {getStripe} from './views/order/mixins/StripeMixin.ts'
import {genId} from '@/lib/lib.ts'
import {StripeCardElement} from '@stripe/stripe-js'
import {onMounted} from 'vue'

const emit = defineEmits<{card: [StripeCardElement]}>()
const id = genId()

const elements = getStripe()!.elements()
const classes = {
  focus: 'focus',
  empty: 'empty',
  invalid: 'invalid',
}
const style = {
  base: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontFamily: 'Roboto, sans-serif',
    fontSmoothing: 'antialiased',
    fontSize: '16px',
    backgroundColor: 'rgba(33, 33, 33, 1)',
    ':-webkit-autofill': {
      color: '#ffffff',
    },
    '::placeholder': {
      color: 'rgba(255, 255, 255, 0.4)',
    },
  },
}

const card = elements.create('card', {
  style,
  iconStyle: 'solid',
  classes,
})

onMounted(() => {
  card.mount(`#${id}-card-number`)
  emit('card', card)
})
</script>
