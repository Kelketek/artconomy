<template>
  <ac-load-section :controller="cards">
    <template v-slot:default>
      <div class="flex card-group-container">
        <v-radio-group :hide-details="true" :value="value" @change="sendInput">
          <ac-card v-for="card in cards.list" :card="card" :key="card.id" :card-list="cards" :value="value" :field-mode="true" />
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
import Component from 'vue-class-component'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcCard from '@/components/views/settings/payment/AcCard.vue'
import {Prop} from 'vue-property-decorator'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import Vue from 'vue'

  @Component({
    components: {AcCard, AcLoadSection},
  })
export default class AcSavedCards extends Vue {
    @Prop({required: true})
    public cards!: ListController<CreditCardToken>

    @Prop({default: null})
    public value!: number

    public sendInput(value: number) {
      this.$emit('input', value)
    }
}
</script>
