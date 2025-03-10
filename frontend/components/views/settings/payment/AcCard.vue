<template>
  <v-col
    v-if="card.x"
    class="saved-card-container"
    cols="12"
  >
    <v-row
      no-gutters
      align="center"
    >
      <v-col
        v-if="fieldMode"
        class="shrink px-2"
      >
        <v-radio :value="card.x.id" />
      </v-col>
      <v-col class="text-center fill-height shrink px-2">
        <v-icon
          size="large"
          :icon="cardIcon"
          :class="`ac-${cardType}`"
        />
      </v-col>
      <v-col class="text-center fill-height shrink px-2">
        <v-row
          no-gutters
          justify="center"
          align="center"
        >
          <v-col class="text-center">
            x{{ card.x!.last_four }}
          </v-col>
        </v-row>
      </v-col>
      <v-col class="text-right fill-height grow">
        <v-tooltip
          v-if="card.x.primary"
          top
        >
          <template #activator="{props}">
            <v-btn
              color="green"
              v-bind="props"
              icon
              size="x-small"
              class="default-indicator"
            >
              <v-icon
                :icon="mdiStar"
                size="x-large"
              />
            </v-btn>
          </template>
          <span>Default Card</span>
        </v-tooltip>
        <v-tooltip
          v-else
          top
        >
          <template #activator="{props}">
            <v-btn
              v-bind="props"
              size="x-small"
              icon
              color="black"
              class="make-default"
              @click="makePrimary"
            >
              <v-icon
                :icon="mdiStarOutline"
                size="x-large"
              />
            </v-btn>
          </template>
          <span>Set Default</span>
        </v-tooltip>
        <ac-confirmation
          :action="deleteCard"
          card-class="delete-confirm"
        >
          <template #default="{on}">
            <v-btn
              icon
              size="x-small"
              color="error"
              class="delete-card"
              v-on="on"
            >
              <v-icon
                :icon="mdiDelete"
                size="x-large"
              />
            </v-btn>
          </template>
        </ac-confirmation>
      </v-col>
    </v-row>
  </v-col>
</template>

<script setup lang="ts">
import {SingleController} from '@/store/singles/controller.ts'
import {ListController} from '@/store/lists/controller.ts'
import {artCall} from '@/lib/lib.ts'
import {ISSUERS} from '@/components/views/settings/payment/issuers.ts'
import {mdiCreditCard, mdiStar, mdiStarOutline, mdiDelete} from '@mdi/js'
import {computed, defineAsyncComponent} from 'vue'
import type {CreditCardToken} from '@/types/main'
const AcConfirmation = defineAsyncComponent(() => import('@/components/wrappers/AcConfirmation.vue'))

const props = withDefaults(defineProps<{
  card: SingleController<CreditCardToken>,
  cardList: ListController<CreditCardToken>,
  fieldMode?: boolean,
}>(), {fieldMode: false})

const deleteCard = async () => {
  props.card.delete().then(props.cardList.get)
}

const setPrimary = () => {
  props.cardList.list.forEach((card) => {
    card.updateX({primary: false})
  })
  props.card.setX({...(props.card.x as CreditCardToken), ...{primary: true}})
}

const makePrimary = () => {
  artCall({
    url: `${props.card.endpoint}primary/`,
    method: 'post',
  }).then(setPrimary)
}

const cardType = computed(() => {
  return ISSUERS[props.card.x!.type]?.name || 'unknown-card'
})

const cardIcon = computed(() => {
  return ISSUERS[props.card.x!.type]?.icon?.path || mdiCreditCard
})
</script>

<style>
.saved-card-container .v-radio {
  margin: 0; }
  .saved-card-container .v-radio .v-input--selection-controls__input {
    margin: 0; }

</style>
