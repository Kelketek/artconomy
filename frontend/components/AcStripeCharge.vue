<template>
    <div :id="`${id}-card-number`" />
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

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import StripeMixin from './views/order/mixins/StripeMixin'
import {genId} from '@/lib/lib'
import {StripeCardElement} from '@stripe/stripe-js'

@Component
export default class AcStripeCharge extends mixins(StripeMixin) {
  public elements = null
  public style = {}
  public card = null as unknown as StripeCardElement
  public id = genId()

  mounted() {
    this.card.mount(`#${this.id}-card-number`)
  }

  created() {
    const elements = this.stripe()!.elements()
    const classes = {focus: 'focus', empty: 'empty', invalid: 'invalid'}
    const style = {
      base: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontFamily: 'Roboto, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        borderBottom: 'solid white 1px',
        '::placeholder': {
          color: 'rgba(255, 255, 255, 0.4)',
        },
      },
    }
    this.card = elements.create('card', {style: style, iconStyle: 'solid', classes})
    this.$emit('card', this.card)
  }
}
</script>
