<template>
  <ac-load-section :controller="cards">
    <template v-slot:default>
      <div class="flex card-group-container">
        <v-radio-group :hide-details="true" :model-value="modelValue" @update:model-value="sendInput">
          <ac-card v-for="card in cards.list" :card="card" :key="card.x!.id" :card-list="cards" :value="modelValue"
                   :field-mode="true"/>
        </v-radio-group>
      </div>
    </template>
  </ac-load-section>
</template>

<style>
.card-group-container .v-input--radio-group .v-input__control {
  width: 100%;
}
</style>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcCard from '@/components/views/settings/payment/AcCard.vue'
import {ListController} from '@/store/lists/controller.ts'
import {CreditCardToken} from '@/types/CreditCardToken.ts'

@Component({
  components: {
    AcCard,
    AcLoadSection,
  },
  emits: ['update:modelValue'],
})
class AcSavedCards extends Vue {
  @Prop({required: true})
  public cards!: ListController<CreditCardToken>

  @Prop({default: null})
  public modelValue!: number

  public sendInput(value: number|null) {
    this.$emit('update:modelValue', value)
  }
}

export default toNative(AcSavedCards)
</script>
